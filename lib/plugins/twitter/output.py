#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import re
import copy
import time

import dateutil.parser
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup
from twisted.internet import reactor

from ...utils.usercolor import UserColor
from ...utils.settings import SETTINGS_TWITTER

user_color = UserColor()

# replace hexadecimal character reference by decimal one
hexentityMassage = copy.copy(BeautifulSoup.MARKUP_MASSAGE)
hexentityMassage += [(re.compile('&#x([^;]+);'), 
                      lambda m: '&#%d;' % int(m.group(1), 16))]

class TwitterTime(object):

    def __init__(self, utc_str):
        dt = dateutil.parser.parse(utc_str)
        self.datetime = dt.replace(tzinfo=dateutil.tz.tzutc()
                                   ).astimezone(dateutil.tz.tzlocal())

    def get_local_time(self):
        return self.datetime.strftime('%H:%M:%S')

class TwitterOutput(object):

    api_connections = 0

    def __init__(self, api, authed, view=None, argument='', options={}):
        self.all_entries = []
        self.last_id = 0
        self.view = view
        self.api = api
        self.authed = authed
        self.params = {}
        self.argument = argument
        self.options = options

        SETTINGS_TWITTER.connect("changed::access-secret", self._restart)

        TwitterOutput.api_connections += 1
        self.delayed = DelayedPool()

    def got_entry(self, msg, *args):
        self.all_entries.append(msg)

    def conv(self, text):
        soup = BeautifulStoneSoup(
            text, convertEntities=BeautifulStoneSoup.HTML_ENTITIES,
             markupMassage=hexentityMassage)
        return unicode(soup)

    def print_all_entries(self, api_interval):
        self.delayed.delete_called()

        if not self.all_entries:
            return

        interval = api_interval / len(self.all_entries)
        print "!", interval, api_interval, len(self.all_entries)
        for i, entry in enumerate(reversed(self.all_entries)):
            #self.print_entry(entry)
            self.delayed.append(reactor.callLater(interval*i, 
                                                  self.print_entry, entry))
        self.all_entries = []

    def print_entry(self, entry):
        time = TwitterTime(entry.created_at)

        body = self._add_links_to_body(entry.text)
        body = body.replace('"', '&quot;')
        body = body.replace('\n', '<br>')
#        body = body.replace("'", '&apos;')

        text = dict(
            datetime=time.get_local_time(),
            id=entry.id,
            image_uri=entry.user.profile_image_url.replace('_normal.', '_mini.'),
            user_name=entry.user.screen_name,
            user_color=user_color.get(entry.user.screen_name),
            status_body=body,
            popup_body=self.conv(entry.text)
            )

        self.last_id = entry.id
        self.view.update(text, self.options.get('notification'))

    def _add_links_to_body(object, text):

        link_pattern = re.compile(r"(s?https?://[-_.!~*'a-zA-Z0-9;/?:@&=+$,%#]+)", re.IGNORECASE | re.DOTALL)
        nick_pattern = re.compile("\B@([A-Za-z0-9_]+|@[A-Za-z0-9_]$)")
        hash_pattern = re.compile(r'(\A|\s|\b)(?:#|\uFF03)([a-zA-Z0-9_\u3041-\u3094\u3099-\u309C\u30A1-\u30FA\u3400-\uD7FF\uFF10-\uFF19\uFF20-\uFF3A\uFF41-\uFF5A\uFF66-\uFF9E]+)')

        text = link_pattern.sub(r"<a href='\1'>\1</a>", text)
        text = nick_pattern.sub(r"<a href='https://twitter.com/\1'>@\1</a>", text)
        text = hash_pattern.sub(r"\1<a href='https://twitter.com/search?q=%23\2'>#\2</a>", text)

        return text

    def start(self, interval=60):
        print "start!"
        if not self.authed.api.use_oauth:
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
        print "connections:", TwitterOutput.api_connections

        rate_limit_remaining = self.authed.api.rate_limit_remaining
        rate_limit_limit = self.authed.api.rate_limit_limit
        rate_limit_reset = self.authed.api.rate_limit_reset

        diff = 0
        if rate_limit_reset:
            diff = rate_limit_reset - int(time.time())
            interval = diff*1.0/rate_limit_remaining * TwitterOutput.api_connections
        else:
            interval = 60.0*60/150*TwitterOutput.api_connections

        interval = 10 if interval < 10 else int(interval)
        print diff, rate_limit_remaining, rate_limit_limit, interval

        return interval


    def exit(self):
        print "exit!"
        if hasattr(self, 'd'):
            self.d.cancel()
        if hasattr(self, 'timeout'):
            self.timeout.cancel()
        self.view.remove()
        self.delayed.clear()
        TwitterOutput.api_connections -= 1

    def _restart(self, *args):
        print "restart!"
        self.authed.update_credential()
        self.start()

    def _on_error(self, e):
        print "error!", e

class DelayedPool(list):

    def delete_called(self):
        for i in self:
            if i.called:
                self.remove(i)

    def clear(self):
        for i in self:
            if not i.called:
                i.cancel()

class TwitterSearchOutput(TwitterOutput):

    def print_entry(self, entry):
        time = TwitterTime(entry.published)

        body = self._add_links_to_body(entry.title) # entry.content
        body = body.replace('"', '&quot;')
#        body = body.replace("'", '&apos;')
        body = body.replace('\n', '<br>')

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
                popup_body=self.conv(entry.title))
        except:
            print body
            print "bad!"

        self.last_id = id
        self.view.update(text, self.options.get('notification'))

class TwitterFeedOutput(TwitterOutput):

    def got_entry(self, msg, *args):
        self.print_entry(msg)

    def conv(self, text):
        return text

    def start(self, interval=False):
        if not self.authed.api.use_oauth:
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
            stream.deferred.addCallback(self._on_error, 'Lost connection.')

    def _on_error(self, *e):
        print "Error:", e
        if self.is_connecting:
            reactor.callLater(10, self._restart)
