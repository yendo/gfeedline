#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

"""
TwitterOutputBase --- TwitterRestOutput --- TwitterSearchOutput
                   |
                   \- TwitterFeedOutput

Rest: got_entry-> check_entry-> buffer_entry : print_all_entries-> print_entry
Feed: got_entry-> check_entry-> buffer_entry->                     print_entry
"""

import time

from twisted.internet import reactor

from tweetentry import *
from ...utils.htmlentities import decode_html_entities
from ...utils.settings import SETTINGS_VIEW
from ...filterliststore import FilterColumn

class TwitterOutputFactory(object):

    def create_obj(self, api, view, argument, options, filters):
        obj = api.output(api, view, argument, options, filters)
        return obj

class TwitterOutputBase(object):

    def __init__(self, api, view=None, argument='', options={}, filters=None):
        self.api = api
        self.view = view
        self.argument = argument
        self.options = options
        self.filters = filters

        self.all_entries = []
        self.since_id = 0
        self.last_id = options.get('last_id') or 0
        self.params = {}
        self.counter = 0

        api.account.connect("update_credential", self._on_reconnect_credential)
        SETTINGS_VIEW.connect_after("changed::theme", self._on_restart_theme_changed)

    def got_entry(self, entry, *args):
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
                if text.lower().find(row[WORD].decode('utf-8').lower()) >= 0
                and row[TARGET].decode('utf-8') == target
                ])
        return is_bad

    def print_entry(self, entry, is_first_call=False):
        entry_dict = self._get_entry_obj(entry).get_dict(self.api)

        is_new_update = self.last_id < entry_dict['id']
        if is_new_update:
            self.last_id = entry_dict['id']

        self.view.update(entry_dict, self.options.get('notification'), 
                         is_first_call, is_new_update)

    def _get_entry_obj(self, entry):
        return TweetEntry(entry)

    def _set_since_id(self, entry_id):
        entry_id = int(entry_id)

        if self.since_id < entry_id:
            self.since_id = entry_id

    def exit(self):
        # print "exit!"
        self.disconnect()
        self.view.remove()

    def disconnect(self):
        if hasattr(self, 'd'):
            self.d.cancel()
        if hasattr(self, 'timeout') and not self.timeout.called:
            self.timeout.cancel()

class TwitterRestOutput(TwitterOutputBase):

    api_connections = 0

    def __init__(self, api, view=None, argument='', options={}, filters=None):
        super(TwitterRestOutput, self).__init__(api, view, argument, options, 
                                                filters)
        TwitterRestOutput.api_connections += 1
        self.delayed = DelayedPool()

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
        else:
            entry_class = TweetEntry
        return entry_class(entry)

    def start(self, interval=60):
        # print "start!"
        if not self.api.account.api.use_oauth:
            print "Not authorized."
            return

        self.params.clear()
        if self.since_id:
            self.params['since_id'] = str(self.since_id)

        params = self.api.get_options(self.argument)
        self.params.update(params)

        self.d = self.api.api(self.got_entry, params=self.params)
        self.d.addErrback(self._on_error).addBoth(lambda x: 
                                                  self.print_all_entries(interval))

        interval = self._get_interval_seconds()
        self.timeout = reactor.callLater(interval, self.start, interval)

    def _get_interval_seconds(self):
        rate_limit_remaining = self.api.account.api.rate_limit_remaining
        rate_limit_limit = self.api.account.api.rate_limit_limit
        rate_limit_reset = self.api.account.api.rate_limit_reset

        diff = 0
        if rate_limit_reset and rate_limit_remaining:
            diff = rate_limit_reset - int(time.time())
            interval = diff*1.0 / rate_limit_remaining * TwitterRestOutput.api_connections
        else:
            interval = 60*60.0 / 150 * TwitterRestOutput.api_connections

        interval = 10 if interval < 10 else int(interval)
#        print "time: %s, limit: %s/%s, connections: %s, interval: %s" % (
#            diff, rate_limit_remaining, rate_limit_limit, 
#            TwitterRestOutput.api_connections, interval)

        return interval

    def exit(self):
        super(TwitterRestOutput, self).exit()
        TwitterRestOutput.api_connections -= 1
        self.delayed.clear()

    def _on_restart_theme_changed(self, *args):
        self.view.clear_buffer()
        self.disconnect()
        self.since_id = 0
        self.counter = 0
        self.start()

    def _on_reconnect_credential(self, *args):
        # print "reconnect for updating credential!"
        self._on_restart_theme_changed()

    def _on_error(self, e):
        print "Error: ", e

class TwitterSearchOutput(TwitterRestOutput):

    def got_entry(self, entry, *args):
        entry.title = decode_html_entities(entry.title)
        self._set_since_id( entry.id.split(':')[2] )
        self.check_entry(entry, entry.title, args)

    def _get_entry_obj(self, entry):
        return SearchTweetEntry(entry)

class TwitterFeedOutput(TwitterOutputBase):

    def __init__(self, api, view=None, argument='', options={}, filters=None):
        super(TwitterFeedOutput, self).__init__(api, view, argument, options, 
                                                filters)
        self.reconnect_interval = 10

    def buffer_entry(self, entry, *args):
        self.print_entry(entry)

    def _get_entry_obj(self, entry):
        if hasattr(entry, 'raw') and entry.raw.get('retweeted_status'):
            entry_class = FeedRetweetEntry 
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

class DelayedPool(list):

    def delete_called(self):
        for i in self:
            if i.called:
                self.remove(i)

    def clear(self):
        for i in self:
            if not i.called:
                i.cancel()
