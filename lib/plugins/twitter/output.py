#
# gfeedline - Gnome Social Feed Reader
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
from ...utils.settings import SETTINGS


class TwitterOutputFactory(object):

    def create_obj(self, api, view, argument, options):
        obj = api.output(api, view, argument, options)
        return obj

class TwitterOutputBase(object):

    def __init__(self, api, view=None, argument='', options={}):
        self.api = api
        self.view = view
        self.argument = argument
        self.options = options

        self.all_entries = []
        self.last_id = 0
        self.params = {}
        self.counter = 0

        api.account.connect("update_credential", self._restart)

    def got_entry(self, msg, *args):
        msg.text = decode_html_entities(msg.text)
        self.check_entry(msg, msg.text, args)

    def check_entry(self, entry, text, *args):
        pass_rt = text.startswith('RT @') and not self.api.include_rt

        has_bad = bool([bad for bad in SETTINGS.get_strv('bad-words')
                        if text.find(bad.decode('utf-8')) >= 0])

        if pass_rt or has_bad:
            print text
        else:
            self.buffer_entry(entry, args)

    def print_entry(self, entry, is_first_call=False):
        entry_class = self._get_entry_class(entry)
        text = entry_class(entry).get_dict(self.api)

        self.last_id = text['id']
        self.view.update(text, self.options.get('notification'), is_first_call)

    def _get_entry_class(self, entry):
        return TweetEntry

    def exit(self):
        print "exit!"
        if hasattr(self, 'd'):
            self.d.cancel()
        if hasattr(self, 'timeout') and not self.timeout.called:
            self.timeout.cancel()
        self.view.remove()

    def _restart(self, *args):
        print "restart!"
        self.start()

class TwitterRestOutput(TwitterOutputBase):

    api_connections = 0

    def __init__(self, api, view=None, argument='', options={}):
        super(TwitterRestOutput, self).__init__(api, view, argument, options)
        TwitterRestOutput.api_connections += 1
        self.delayed = DelayedPool()

    def buffer_entry(self, msg, *args):
        self.all_entries.append(msg)

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

    def _get_entry_class(self, entry):
        if hasattr(entry, 'retweeted_status') and entry.retweeted_status:
            entry_class = RestRetweetEntry
        else:
            entry_class = TweetEntry
        return entry_class

    def start(self, interval=60):
        print "start!"
        if not self.api.account.api.use_oauth:
            print "not authorized"
            return

        if self.last_id:
            self.params['since_id'] = str(self.last_id)

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
        print "time: %s, limit: %s/%s, connections: %s, interval: %s" % (
            diff, rate_limit_remaining, rate_limit_limit, 
            TwitterRestOutput.api_connections, interval)

        return interval

    def exit(self):
        super(TwitterRestOutput, self).exit()
        TwitterRestOutput.api_connections -= 1
        self.delayed.clear()

    def _on_error(self, e):
        print "error!", e

class TwitterSearchOutput(TwitterRestOutput):

    def got_entry(self, msg, *args):
        msg.title = decode_html_entities(msg.title)
        self.check_entry(msg, msg.title, args)

    def _get_entry_class(self, entry):
        return SearchTweetEntry

class TwitterFeedOutput(TwitterOutputBase):

    def __init__(self, api, view=None, argument='', options={}):
        super(TwitterFeedOutput, self).__init__(api, view, argument, options)
        self.reconnect_interval = 10

    def buffer_entry(self, msg, *args):
        self.print_entry(msg)

    def _get_entry_class(self, entry):
        if hasattr(entry, 'raw') and entry.raw.get('retweeted_status'):
            entry_class = FeedRetweetEntry 
        else:
            entry_class = TweetEntry

        return entry_class

    def start(self, interval=False):
        if not self.api.account.api.use_oauth:
            return

        argument = self.api.get_options(self.argument)
        # print argument

        self.d = self.api.api(self.got_entry, argument).\
            addErrback(self._on_error).\
            addBoth(self._on_connect)
        self.is_connecting = True

    def exit(self):
        if hasattr(self, 'stream') and hasattr(self.stream, 'transport'):
            self.stream.transport.stopProducing()
        self.is_connecting = False
        super(TwitterFeedOutput, self).exit()

    def _on_connect(self, stream):
        self.stream = stream
        if stream:
            self.reconnect_interval = 10
            stream.deferred.addCallback(self._on_error, 'Lost connection.')

    def _on_error(self, *e):
        print "Error:", e
        if self.is_connecting:
            self.timeout = reactor.callLater(self.reconnect_interval, self._restart)
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
