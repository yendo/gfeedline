#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

"""
TwitterOutputBase --- TwitterRestOutput --- TwitterSearchOutput
                   |
                   \- TwitterFeedOutput

Rest: check_entry -> got_entry : print_all_entries -> print_entry
Feed: check_entry -> got_entry                     -> print_entry
"""

import re
import time

import dateutil.parser
from twisted.internet import reactor

from ...utils.usercolor import UserColor
from ...utils.settings import SETTINGS_TWITTER
from ...utils.htmlentities import decode_html_entities

user_color = UserColor()


class TwitterOutputBase(object):

    def __init__(self, api, account, view=None, argument='', options={}):
        self.api = api
        self.account = account
        self.view = view
        self.argument = argument
        self.options = options

        self.all_entries = []
        self.last_id = 0
        self.params = {}
        self.counter = 0

        SETTINGS_TWITTER.connect("changed::access-secret", self._restart)

        self.add_markup = AddedHtmlMarkup()

    def check_entry(self, msg, *args):
        msg.text = decode_html_entities(msg.text)
        if msg.text.startswith('RT @') and not self.api.include_rt:
            print "rt!"
        else:
            self.got_entry(msg, args)

    def print_entry(self, entry, is_first_call=False):
        time = TwitterTime(entry.created_at)
        body_string = decode_html_entities(entry.text)
        body = self.add_markup.convert(body_string)
        user = entry.sender if self.api.name == 'Direct Messages' else entry.user

        text = dict(
            datetime=time.get_local_time(),
            id=entry.id,
            image_uri=user.profile_image_url.replace('_normal.', '_mini.'),
            user_name=user.screen_name,
            user_color=user_color.get(user.screen_name),
            status_body=body,
            popup_body=body_string,
            )

        self.last_id = entry.id
        self.view.update(text, self.options.get('notification'), is_first_call)

    def exit(self):
        print "exit!"
        if hasattr(self, 'd'):
            self.d.cancel()
        if hasattr(self, 'timeout') and not self.timeout.called:
            self.timeout.cancel()
        self.view.remove()

    def _restart(self, *args):
        print "restart!"
        self.account.update_credential()
        self.start()

class TwitterRestOutput(TwitterOutputBase):

    api_connections = 0

    def __init__(self, api, account, view=None, argument='', options={}):
        super(TwitterRestOutput, self).__init__(api, account, view, argument, options)
        TwitterRestOutput.api_connections += 1
        self.delayed = DelayedPool()

    def got_entry(self, msg, *args):
        self.all_entries.append(msg)

    def print_all_entries(self, api_interval):
        self.delayed.delete_called()

        if not self.all_entries:
            return

        interval = api_interval / len(self.all_entries)
        print "!", interval, api_interval, len(self.all_entries)
        for i, entry in enumerate(reversed(self.all_entries)):
            if self.counter:
                self.delayed.append(
                    reactor.callLater(interval*i, self.print_entry, entry))
            else:
                self.print_entry(entry, is_first_call=True)

        self.counter += 1
        self.all_entries = []

    def start(self, interval=60):
        print "start!"
        if not self.account.api.use_oauth:
            print "not authorized"
            return

        if self.last_id:
            self.params['since_id'] = str(self.last_id)

        params = self.api.get_options(self.argument)
        self.params.update(params)

        self.d = self.api.api(self.check_entry, params=self.params)
        self.d.addErrback(self._on_error).addBoth(lambda x: 
                                                  self.print_all_entries(interval))

        interval = self._get_interval_seconds()
        self.timeout = reactor.callLater(interval, self.start, interval)

    def _get_interval_seconds(self):
        print "connections:", TwitterRestOutput.api_connections

        rate_limit_remaining = self.account.api.rate_limit_remaining
        rate_limit_limit = self.account.api.rate_limit_limit
        rate_limit_reset = self.account.api.rate_limit_reset

        diff = 0
        if rate_limit_reset:
            diff = rate_limit_reset - int(time.time())
            interval = diff*1.0/rate_limit_remaining * TwitterRestOutput.api_connections
        else:
            interval = 60.0*60/150*TwitterRestOutput.api_connections

        interval = 10 if interval < 10 else int(interval)
        print diff, rate_limit_remaining, rate_limit_limit, interval

        return interval

    def exit(self):
        super(TwitterRestOutput, self).exit()
        TwitterRestOutput.api_connections -= 1
        self.delayed.clear()

    def _on_error(self, e):
        print "error!", e

class TwitterSearchOutput(TwitterRestOutput):

    def check_entry(self, msg, *args):
        msg.title = decode_html_entities(msg.title)
        if msg.title.startswith('RT @') and not self.api.include_rt:
            print "rt!"
        else:
            self.got_entry(msg, args)

    def print_entry(self, entry, is_first_call=False):
        time = TwitterTime(entry.published)
        body_string = decode_html_entities(entry.title)
        body = self.add_markup.convert(body_string)

        name = entry.author.name.split(' ')[0]
        id = entry.id.split(':')[2]

        try:
            text = dict(
                datetime=time.get_local_time(),
                id=id,
                image_uri=entry.image,
                user_name=name,
                user_color=user_color.get(name),
                status_body=body,
                popup_body=body_string)
        except:
            print body
            print "bad!"

        self.last_id = id
        self.view.update(text, self.options.get('notification'), is_first_call)

class TwitterFeedOutput(TwitterOutputBase):

    def __init__(self, api, account, view=None, argument='', options={}):
        super(TwitterFeedOutput, self).__init__(api, account, view, argument, options)
        self.reconnect_interval = 10

    def got_entry(self, msg, *args):
        self.print_entry(msg)

    def start(self, interval=False):
        if not self.account.api.use_oauth:
            return

        argument = self.api.get_options(self.argument)
        # print argument

        self.d = self.api.api(self.check_entry, argument).\
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

class TwitterTime(object):

    def __init__(self, utc_str):
        dt = dateutil.parser.parse(utc_str)
        self.datetime = dt.replace(tzinfo=dateutil.tz.tzutc()
                                   ).astimezone(dateutil.tz.tzlocal())

    def get_local_time(self):
        return self.datetime.strftime('%H:%M:%S')

class AddedHtmlMarkup(object):

    def __init__(self):
        self.link_pattern = re.compile(
            r"(s?https?://[-_.!~*'a-zA-Z0-9;/?:@&=+$,%#]+)", 
            re.IGNORECASE | re.DOTALL)
        self.nick_pattern = re.compile("\B@([A-Za-z0-9_]+|@[A-Za-z0-9_]$)")
        self.hash_pattern = re.compile(
            u'(?:#|\uFF03)([a-zA-Z0-9_\u3041-\u3094\u3099-\u309C\u30A1-\u30FA\u3400-\uD7FF\uFF10-\uFF19\uFF20-\uFF3A\uFF41-\uFF5A\uFF66-\uFF9E]+)')

        self.sequence_pattern = re.compile(r'((.)\2{10,10})') # 10 times

    def convert(self, text):
        text = text.replace("'", '&apos;')

        text = self.link_pattern.sub(r"<a href='\1'>\1</a>", text)
        text = self.nick_pattern.sub(r"<a href='https://twitter.com/\1'>@\1</a>", 
                                     text)
        text = self.hash_pattern.sub(
            r"<a href='https://twitter.com/search?q=%23\1'>#\1</a>", text)

        text = text.replace('"', '&quot;')
        text = text.replace('\n', '<br>')
        # text = self.sequence_pattern.sub(r'\1 ', text)

        return text

class DelayedPool(list):

    def delete_called(self):
        for i in self:
            if i.called:
                self.remove(i)

    def clear(self):
        for i in self:
            if not i.called:
                i.cancel()
