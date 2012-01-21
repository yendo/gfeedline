#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os
import sys
import re
from string import Template

import dateutil.parser
from BeautifulSoup import BeautifulStoneSoup
from gi.repository import GLib

from ...utils.usercolor import UserColor
from ...utils.settings import SETTINGS_TWITTER
from ...utils.nullobject import Null

user_color = UserColor()


class TwitterAPIDict(dict):

    def __init__(self):
        all_api = [
             TwitterAPIHomeTimeLine,
             TwitterAPIListTimeLine,
             TwitterAPIMentions,
    
             TwitterAPIUserStream,
             TwitterAPITrack,
             ]

        null = Null()
        for api in all_api:
            self[api(null).name] = api

class TwitterAPIBase(object):

    def __init__(self, authed=None):
        self.authed = authed

        self._get_output_class()
        self._setup()

    def create_obj(self, view, argument, params):
        options = params.get('params') if params else None
        obj = self.output(self.api, self.authed, view, argument, options)
        return obj

    def _get_output_class(self):
        self.output= TwitterOutput

class TwitterFeedAPIBase(TwitterAPIBase):

    def _get_output_class(self):
        self.output = TwitterFeedOutput

class TwitterAPIHomeTimeLine(TwitterAPIBase):

    def _setup(self):
        self.api = self.authed.api.home_timeline
        self.name = 'Home TimeLine'

class TwitterAPIListTimeLine(TwitterAPIBase):

    def _setup(self):
        self.api = self.authed.api.list_timeline
        self.name = 'List TimeLine'

class TwitterAPIMentions(TwitterAPIBase):

    def _setup(self):
        self.api = self.authed.api.mentions
        self.name = 'Mentions'

class TwitterAPIUserStream(TwitterFeedAPIBase):

    def _setup(self):
        self.api = self.authed.api.userstream
        self.name = 'User Stream'

class TwitterAPITrack(TwitterFeedAPIBase):

    def _setup(self):
        self.api = self.authed.api.track
        self.name = 'Track'
    

class TwitterTime(object):

    def __init__(self, utc_str):
        dt = dateutil.parser.parse(utc_str)
        self.datetime = dt.replace(tzinfo=dateutil.tz.tzutc()
                                   ).astimezone(dateutil.tz.tzlocal())

    def get_local_time(self):
        return self.datetime.strftime('%H:%M:%S')

class TwitterOutput(object):

    def __init__(self, api, authed, view=None, argument='', params={}):
        self.all_entries = []
        self.last_id = 0
        self.view = view
        self.api = api
        self.authed = authed
        self.params = params

        SETTINGS_TWITTER.connect("changed::access-secret", self._restart)

    def got_entry(self, msg, *args):
        self.all_entries.append(msg)

    def conv(self, text):
        return BeautifulStoneSoup(
            text, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)

    def print_all_entries(self):
        for entry in reversed(self.all_entries):
            self.print_entry(entry)
        self.all_entries = []

    def print_entry(self, entry):
        time = TwitterTime(entry.created_at)

        body = self._add_links_to_body(entry.text)
        body = body.replace('"', '&quot;')
        body = body.replace('\n', '<br>')

        template_file = os.path.abspath('html/status.html')
        file = open(template_file).read()
        temp = Template(unicode(file, 'utf-8', 'ignore'))
        text = temp.substitute(
            datetime=time.get_local_time(),
            id=entry.id,
            image_uri=entry.user.profile_image_url.replace('_normal.', '_mini.'),
            user_name=entry.user.screen_name,
            user_color=user_color.get(entry.user.id),
            status_body=body)

        #print text
        self.last_id = entry.id
        self.view.webview.update(text)

    def _add_links_to_body(object, text):

        link_pattern = re.compile(r"(s?https?://[-_.!~*'a-zA-Z0-9;/?:@&=+$,%#]+)", re.IGNORECASE | re.DOTALL)
        nick_pattern = re.compile("\B@([A-Za-z0-9_]+|@[A-Za-z0-9_]$)")
        hash_pattern = re.compile(r'(\A|\s|\b)(?:#|\uFF03)([a-zA-Z0-9_\u3041-\u3094\u3099-\u309C\u30A1-\u30FA\u3400-\uD7FF\uFF10-\uFF19\uFF20-\uFF3A\uFF41-\uFF5A\uFF66-\uFF9E]+)')

        text = link_pattern.sub(r"<a href='\1'>\1</a>", text)
        text = nick_pattern.sub(r"<a href='https://twitter.com/\1'>@\1</a>", text)
        text = hash_pattern.sub(r"\1<a href='https://twitter.com/search?q=%23\2'>#\2</a>", text)

        return text

    def start(self, interval=180):
        print "start!"
        if not self.authed.api.use_oauth:
            print "not authorized"
            return

        if self.last_id:
            self.params['since_id'] = str(self.last_id)

        self.d = self.api(self.got_entry, params=self.params)
        self.d.addErrback(self._on_error).addBoth(lambda x: self.print_all_entries())

        print self.authed.api.rate_limit_remaining
        # print self.authed.api.rate_limit_limit
        # print self.authed.api.rate_limit_reset

        self.timeout = GLib.timeout_add_seconds(interval, self.start, interval)

    def exit(self):
        print "exit!"
        print self.d.cancel()
        self.view.remove()

    def _restart(self, *args):
        print "restart!"
        self.authed.update_credential()
        self.start()

    def _on_error(self, e):
        print "error!", e

class TwitterFeedOutput(TwitterOutput):

    def got_entry(self, msg, *args):
        self.print_entry(msg)

    def conv(self, text):
        return text

    def start(self, interval=False):
        if not self.authed.api.use_oauth:
            return

        self.d = self.api(self.got_entry, self.params).\
            addErrback(self._on_error).\
            addBoth(self._on_connect)
        self.is_connecting = True

    def exit(self):
        print "exit!"
        print self.d.cancel()
        #print self.timeout
        self.stream.transport.stopProducing()
        self.is_connecting = False
        self.view.remove()

    def _on_connect(self, stream):
        self.stream = stream
        if stream:
            stream.deferred.addCallback(self._on_error, 'Lost connection.')

    def _on_error(self, *e):
        print "Error:", e
        if self.is_connecting:
            GLib.timeout_add_seconds(10, self._restart)
