#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012-2013, Yoshizumi Endo.
# Licence: GPL3

"""
TwitterOutputBase --- TwitterRestOutput --- TwitterSearchOutput
                   |
                   \- TwitterFeedOutput

Rest: got_entry-> check_entry-> buffer_entry : print_all_entries-> print_entry
Feed: got_entry-> check_entry-> buffer_entry---------------------> print_entry
              \-> (events)--------------------------------------/
"""

import time

from twisted.internet import reactor

from tweetentry import *
from ...utils.htmlentities import decode_html_entities
from ...utils.settings import SETTINGS_VIEW
from ...filterliststore import FilterColumn
from ...constants import Column
from ...theme import Theme
from ..base.output import OutputBase


class TwitterOutputBase(OutputBase):

    def __init__(self, api, view=None, argument='', options={}, filters=None):
        super(TwitterOutputBase, self).__init__(api, view, argument, options,
                                                filters)
        self.all_entries = []
        api.account.connect("update_credential", self._on_reconnect_credential)

    def got_entry(self, entry, *args):
        if not entry:
            return

        for i in entry:
            entry = DictObj(i) # FIXME
            entry.text = decode_html_entities(entry.text)
            self._set_since_id(entry.id)
            self.check_entry(entry, entry.text, args)

    def check_entry(self, entry, text, *args):
        pass_rt = text.startswith('RT @') and not self.api.include_rt
        is_bad_body = self._check_filter(text, _('Body'), self.filters)

        entry_obj = self._get_entry_obj(entry)

        sender = entry_obj.get_sender_name(self.api)
        is_bad_sender = self._check_filter(sender, _('Sender'), self.filters)

        source = entry_obj.get_source_name()
        is_bad_source = self._check_filter(source, _('Source'), self.filters)

#        if is_bad_sender:
#            print text

        if pass_rt or is_bad_body or is_bad_sender or is_bad_source:
            # print "Del: ", text
            pass
        else:
            self.buffer_entry(entry, args)

    def _check_filter(self, text, target, filters):
        TARGET, WORD = FilterColumn.TARGET, FilterColumn.WORD
        is_bad = bool([
                row for row in filters
                if text.lower().count(row[WORD].decode('utf-8').lower())
                and row[TARGET].decode('utf-8') == target
                ])
        return is_bad

    def print_entry(self, entry, is_first_call=False):
        entry_dict = self._get_entry_obj(entry).get_dict(self.api)
        has_notify = self.options.get('notification') 

        # FIXME
        entry_dict['source'] = _('via %s') % entry_dict['source'] \
            if entry_dict['source'] else ''

        # retweet template
        if entry_dict.get('retweet_by_name'):
            text = _("Retweeted by %s")
            retweet_by_screen_name = entry_dict['retweet_by_screen_name']
            title_by_screen_name = text % entry_dict['retweet_by_screen_name']
            title_by_name = text % entry_dict['retweet_by_name']

            template = self.theme.template['retweet']
            key_dict = {'retweet_by_screen_name': retweet_by_screen_name,
                        'title_by_screen_name': title_by_screen_name, 
                        'title_by_name': title_by_name}
            entry_dict['retweet'] = template.substitute(key_dict)

        if entry_dict.get('event'):
            style = 'status' # FIXME
            is_new_update = True

            has_notify = has_notify or self.options.get('notify_events')
        else:
            style = 'status' # FIXME
            is_new_update = self.last_id < entry_dict['id']

            if is_new_update:
                self.last_id = entry_dict['id']

        self.view.update(entry_dict, style, has_notify, 
                         is_first_call, is_new_update)

        other_view = self.api.print_to_other_view(entry_dict)
        if other_view:
            output_views = [x[Column.API].view for x in self.view.liststore 
                            if x[Column.TARGET].decode('utf-8') == other_view]
            for view in output_views:
                view.update(entry_dict, style, is_new_update=is_new_update)

    def _get_entry_obj(self, entry):
        return TweetEntry(entry)

class TwitterRestOutput(TwitterOutputBase):

    SINCE = 'since_id'

    def buffer_entry(self, entry, *args):
        self.all_entries.append(entry)

    def print_all_entries(self, api_interval):
        self.delayed.delete_called()

        if not self.all_entries:
            return

        interval = api_interval*1.0 / len(self.all_entries)
        # print "interval: ", interval
        for i, entry in enumerate(reversed(self.all_entries)):
            if self.counter:
                self.delayed.append(
                    reactor.callLater(interval*i, self.print_entry, entry))
            else:
                self.print_entry(entry, is_first_call=True)

        self.counter += 1
        self.all_entries = []

    def _get_entry_obj(self, entry):
        if hasattr(entry, 'retweeted_status') and entry.retweeted_status:
            entry_class = RestRetweetEntry
        elif 'sender_screen_name' in entry.d:
            entry_class = DirectMessageEntry
        else:
            entry_class = TweetEntry
        return entry_class(entry)

    def start(self, interval=60):
        if not self.api.account.api.use_oauth:
            print "Not authorized."
            return

        self.params.clear()
        if self.since_id:
            self.params[self.SINCE] = str(self.since_id)

        params = self.api.get_options(self.argument)
        self.params.update(params)

        self.d = self.api.api(self.got_entry, params=self.params)
        self.d.addErrback(self._on_error).addBoth(lambda x: 
                                                  self.print_all_entries(interval))
        self.d.addErrback(self._on_error)

        interval = self._get_interval_seconds()
        self.timeout = reactor.callLater(interval, self.start, interval)

    def _get_interval_seconds(self):
        rate_limit_remaining = self.api.account.api.rate_limit_remaining
        rate_limit_limit = self.api.account.api.rate_limit_limit
        rate_limit_reset = self.api.account.api.rate_limit_reset

        # print self.api.name, self.api.connections

        diff = 0
        if rate_limit_reset and rate_limit_remaining:
            diff = rate_limit_reset - int(time.time())
            interval = diff * 1.0 / rate_limit_remaining * self.api.connections
        else:
            interval = 15 * 60 / self.api.rate_limit * self.api.connections

        # FIXME
        interval = 15 * 60 / self.api.rate_limit * self.api.connections
        interval = 10 if interval < 10 else interval

#        print "time: %s, limit: %s/%s, connections: %s (%s), interval: %s" % (
#            diff, rate_limit_remaining, rate_limit_limit, 
#            self.api.connections, self.api.name, interval)

        return interval

    def exit(self):
        super(TwitterRestOutput, self).exit()
        self.api.exit()

class TwitterSearchOutput(TwitterRestOutput):

    def got_entry(self, entry, *args):
        if entry:
            entry = entry['statuses']
            super(TwitterSearchOutput, self).got_entry(entry, args)

class TwitterRelatedResultsOutput(TwitterRestOutput):

    def got_entry(self, all_entries, *args):
        new_entries = []

        if len(all_entries) < 1:
            print "no entries."
            return

        for raw_entry in all_entries[0]['results']:
            entry = raw_entry['value']

            if entry['id'] > self.since_id:
                self._set_since_id(entry['id'])
                new_entries.append(entry)

        for entry in reversed(new_entries):
            self.check_entry(entry, entry['text'], args)

    def _get_entry_obj(self, entry):
        return RelatedResultsEntry(entry)

class TwitterFeedOutput(TwitterOutputBase):

    def __init__(self, api, view=None, argument='', options={}, filters=None):
        super(TwitterFeedOutput, self).__init__(api, view, argument, options, 
                                                filters)
        self.reconnect_interval = 10

    def buffer_entry(self, entry, *args):
        self.print_entry(entry)

    def got_entry(self, entry, *args):
        if hasattr(entry, 'event'):
            print "event!", entry.event

            if self.api.account.user_name == entry.source.screen_name:
                print "skip user own activity"
                return
            elif entry.event == 'user_update':
                return

            self.print_entry(entry)
        else:
            entry.text = decode_html_entities(entry.text)
            self._set_since_id(entry.id)
            self.check_entry(entry, entry.text, args)

    def _get_entry_obj(self, entry):
        if hasattr(entry, 'raw') and entry.raw.get('retweeted_status'):
            retweeted_user = entry.raw['retweeted_status']['user']['screen_name']
            account_user = self.api.account.user_name 
            entry_class = MyFeedRetweetEntry \
                if retweeted_user == account_user else FeedRetweetEntry
        elif hasattr(entry, 'event'):
            entry_class = FeedEventEntry
        else:
            entry_class = TweetEntry

        return entry_class(entry)

    def start(self, interval=False):
        if not self.api.account.api.use_oauth:
            return

        argument = self.api.get_options(self.argument)
        # print argument

        self.d = self.api.api(self.got_entry, argument).\
            addErrback(self._on_error).\
            addBoth(self._on_connect)
        self.is_connecting = True

    def disconnect(self):
        super(TwitterFeedOutput, self).disconnect()

        if hasattr(self, 'stream') and hasattr(self.stream, 'transport'):
            # print "force stop stream connection!"
            self.stream.transport.stopProducing()
        self.is_connecting = False

    def _on_reconnect_credential(self, *args):
        self.disconnect()

        self.view.clear_buffer()
        reactor.callLater(2, self.start) # waits lost connection.

    def _on_restart_theme_changed(self, *args):
        self.view.clear_buffer()

    def _reconnect_lost_connection(self, *args):
        # print "reconnect for lost stream connection!"
        self.start()

    def _on_connect(self, stream):
        self.stream = stream
        if stream:
            self.reconnect_interval = 10
            stream.deferred.addCallback(self._on_error, 'Lost connection.')

    def _on_error(self, *e):
        print "Error:", e
        if self.is_connecting:
            self.timeout = reactor.callLater(self.reconnect_interval, 
                                             self._reconnect_lost_connection)
            if self.reconnect_interval < 180:
                self.reconnect_interval += 10
