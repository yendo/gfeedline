# -*- coding: utf-8 -*-


import re
from datetime import datetime, timedelta
from xml.sax.saxutils import escape, unescape
import dateutil.parser

from ...utils.usercolor import UserColor
from ...utils.htmlentities import decode_html_entities

user_color = UserColor()

class FacebookEntry(object):

    def __init__(self, entry):
        self.entry = entry
        self.retweet_by_screen_name = ''
        self.retweet_by_name = ''

    def get_dict(self, api):
        entry = self.entry

        time = TwitterTime(entry['created_time'])
        body_string = entry.get('message') or entry.get('story') or entry.get('name') 
        body = add_markup.convert(body_string) # add_markup is global
#        styles = self._get_styles(api, user.screen_name, entry)

        entry_dict = dict(
            date_time=time.get_local_time(),
            id=entry['id'],
            styles='',
            image_uri='https://graph.facebook.com/%s/picture' % entry['from']['id'],

            retweet='',
            retweet_by_screen_name='',
            retweet_by_name='',

            in_reply_to='',

            user_name='',
            full_name=entry['from']['name'],
            user_color=user_color.get(entry['from']['name']),
            protected='',
            source='',

            status_body=body,
            popup_body=body,
            target=''
            )

        return entry_dict

    def _get_styles(self, api, screen_name, entry=None):
        style_obj = EntryStyles()
        return style_obj.get(api, screen_name, entry)

    def _get_body(self, text):
        text = decode_html_entities(text) # need to decode!
        return text

    def _get_protected_icon(self, attribute):
        return True if attribute and attribute != 'false' else ''

class EntryStyles(object):

    def get(self, api, screen_name, entry=None):

        styles = [ self._get_style_own_message(api, screen_name) ]

        if entry:
            styles.append(self._get_style_reply(entry, api))
            styles.append(self._get_style_favorited(entry) )

        styles_string = " ".join([x for x in styles if x])
        return styles_string

    def _get_style_own_message(self, api, name):
        return 'mine' if api.account.user_name == name else ''

    def _get_style_reply(self, entry, api):
        return 'reply' \
            if entry.in_reply_to_screen_name == api.account.user_name else ''

    def _get_style_favorited(self, entry):
        fav = entry.favorited
        return '' if fav == 'false' or not fav else 'favorited'

    def _get_style_retweet(self):
        pass

class DictObj(object):

    def __init__(self, d):
        self.d = d

    def __getattr__(self, m):
        return self.d.get(m, None)

class TwitterTime(object):

    def __init__(self, utc_str):
        self.utc = dateutil.parser.parse(utc_str).replace(tzinfo=None)
        self.local_time = self.utc.replace(tzinfo=dateutil.tz.tzutc()
                                   ).astimezone(dateutil.tz.tzlocal())

    def get_local_time(self):
        datetime_format = '%y-%m-%d' \
            if datetime.utcnow() - self.utc >= timedelta(days=1) \
            else '%H:%M:%S'

        return self.local_time.strftime(datetime_format)

class AddedHtmlMarkup(object):

    def __init__(self):
        self.link_pattern = re.compile(
            r"(s?https?://[-_.!~*'a-zA-Z0-9;/?:@&=+$,%#]+)", 
            re.IGNORECASE | re.DOTALL)
        self.nick_pattern = re.compile("\B@([A-Za-z0-9_]+|@[A-Za-z0-9_]$)")
        self.hash_pattern = re.compile(
            u'(?:#|\uFF03)([a-zA-Z0-9_'
            u'\u3041-\u3094\u3099-\u309C\u30A1-\u30FF\u3400-\uD7FF'
            u'\uFF10-\uFF19\uFF20-\uFF3A\uFF41-\uFF5A\uFF66-\uFF9E]+)')

    def convert(self, text):
        text = unescape(text)
        text = escape(text, {"'": '&apos;'}) # Important!

        text = self.link_pattern.sub(r"<a href='\1'>\1</a>", text)
        text = self.nick_pattern.sub(r"<a href='https://twitter.com/\1'>@\1</a>", 
                                     text)

#        screen_name_re = r"<a href='gfeedlinereply://%s'>@\1</a>" % 120
#        text = self.nick_pattern.sub(screen_name_re, text)

        text = self.hash_pattern.sub(
            r"<a href='https://twitter.com/search?q=%23\1'>#\1</a>", text)

        text = text.replace('"', '&quot;')
        text = text.replace('\r\n', '<br>')
        text = text.replace('\n', '<br>')

        return text

add_markup = AddedHtmlMarkup()
