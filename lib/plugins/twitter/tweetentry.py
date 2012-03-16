import re
from datetime import datetime, timedelta
from xml.sax.saxutils import escape

from BeautifulSoup import BeautifulSoup
import dateutil.parser

from ...utils.usercolor import UserColor
from ...utils.htmlentities import decode_html_entities

user_color = UserColor()

"""
TweetEntry -- RestRetweetEntry  -- FeedRetweetEntry
           |- SearchTweetEntry
           \- FeedEventEntry
"""


class TweetEntry(object):

    def __init__(self, entry):
        self.retweet_icon = ''
        self.entry=entry

    def get_dict(self, api):
        entry = self.entry

        time = TwitterTime(entry.created_at)
        body_string = self._get_body(entry.text) # FIXME
        body = add_markup.convert(body_string) # add_markup is global
        user = self._get_sender(api)

        self.style_obj = EntryStyles()
        styles = self.style_obj.get(api, user.screen_name, entry)

        entry_dict = dict(
            date_time=time.get_local_time(),
            id=entry.id,
            styles=styles,
            image_uri=user.profile_image_url,
            retweet=self.retweet_icon,

            user_name=user.screen_name,
            full_name=user.name,
            user_color=user_color.get(user.screen_name),
            protected=self._get_protected_icon(user.protected),
            source=entry.source,

            status_body=body,
            popup_body=body_string,
            target=''
            )

        return entry_dict

    def get_sender_name(self, api):
        sender = self._get_sender(api)
        return sender.screen_name

    def _get_sender(self, api):
        sender = self.entry.sender if api.name == _('Direct Messages') \
            else self.entry.user
        return sender

    def get_source_name(self):
        return self._parse_source_html(self.entry.source)

    def _parse_source_html(self, source):
        source = decode_html_entities(source)

        if source.find('http') > 0:
            soup = BeautifulSoup(source)
            source = [x.contents[0] for x in soup('a')][0]
        return source

    def _get_body(self, text):
        text = decode_html_entities(text) # need to decode!
        return text

    def _get_protected_icon(self, attribute):
        key = '' if attribute == 'false' or not attribute \
            else "<img class='protected' src='key.png' width='10' height='13'>"
        return key

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

class RestRetweetEntry(TweetEntry):

    def __init__(self, entry):
        self.retweet_icon = "<img src='retweet.png' width='18' height='14'>"
        self.entry=entry.retweeted_status

class FeedRetweetEntry(RestRetweetEntry):

    def __init__(self, entry):
        super(FeedRetweetEntry, self).__init__(entry)

        self.entry=DictObj(entry.raw.get('retweeted_status'))
        self.entry.user=DictObj(self.entry.user)

class SearchTweetEntry(TweetEntry):

    def get_dict(self, api):
        entry = self.entry

        time = TwitterTime(entry.published)
        body_string = self._get_body(entry.title) # FIXME
        body = add_markup.convert(body_string) # add_markup is global
        #body = decode_html_entities(entry.content)
        #body = body.replace('"', "'")

        name = self.get_sender_name()
        entry_id = entry.id.split(':')[2]

        self.style_obj = EntryStyles()
        styles = self.style_obj.get(api, name)

        entry_dict = dict(
            date_time=time.get_local_time(),
            id=entry_id,
            styles=styles,
            image_uri=entry.image,
            retweet='',

            user_name=name,
            full_name=self.get_full_name(entry),
            user_color=user_color.get(name),
            protected='',
            source=entry.twitter_source,

            status_body=body,
            popup_body=body_string,
            target=''
            )

        return entry_dict

    def get_sender_name(self, api=None):
        return self.entry.author.name.split(' ')[0]

    def get_full_name(self, entry):
        return entry.author.name.partition(' ')[2][1:-1] # removed parentheses

    def _get_sender(self, api):
        pass

    def get_source_name(self):
        return self._parse_source_html(self.entry.twitter_source)

    def _get_body(self, text):
        return text

class FeedEventEntry(TweetEntry):

    def get_dict(self, api):
        entry = self.entry

        if entry.event == 'favorite':
            body = _('favorited your Tweet')
        elif entry.event == 'unfavorite':
            body = _('unfavorited your Tweet')
        elif entry.event == 'follow':
            body = _('followed you')
        elif entry.event == 'list_member_added':
            body = _('added you to list %s'
                     ) % entry.raw['target_object']['uri'][1:]
        elif entry.event == 'list_member_removed':
            body = _('removed you from list %s'
                     ) % entry.raw['target_object']['uri'][1:]
#        elif entry.event == 'user_update':
#            body = 'user_update'

        if hasattr(entry, 'target_object') and hasattr(entry.target_object, 'text'):
            target_object = entry.target_object
            target_body = entry.target_object.text

            date_time = TwitterTime(target_object.created_at).get_local_time()
            dt_format = ("(<a href='http://twitter.com/%s/status/%s' "
                         "class='target_datetime'>%s</a>)")
            target_date_time = dt_format % (
                entry.target.screen_name, target_object.id, date_time)
        else:
            target_body = ''
            target_date_time = ''

        entry_dict = dict(
            date_time=TwitterTime(entry.created_at).get_local_time(),
            id='',
            styles='',
            image_uri=entry.source.profile_image_url,
            retweet='',

            user_name=entry.source.screen_name,
            full_name=entry.source.name,
            user_color=user_color.get(entry.source.screen_name),
            protected=self._get_protected_icon(user.protected),
            source='',

            status_body=body,
            popup_body="%s %s" % (entry.source.name, body),
            
            event=body,
            target='',

            pre_username = '',
            post_username = ' ',

            target_body=target_body,
            target_date_time=target_date_time,
            )

        return entry_dict

    def get_sender_name(self, api=None):
        pass

    def get_full_name(self, entry):
        pass

    def get_source_name(self):
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
            u'(?:#|\uFF03)([a-zA-Z0-9_\u3041-\u3094\u3099-\u309C\u30A1-\u30FA\u3400-\uD7FF\uFF10-\uFF19\uFF20-\uFF3A\uFF41-\uFF5A\uFF66-\uFF9E]+)')

    def convert(self, text):
        text = escape(text, {"'": '&apos;'}) # Important!

        text = self.link_pattern.sub(r"<a href='\1'>\1</a>", text)
        text = self.nick_pattern.sub(r"<a href='https://twitter.com/\1'>@\1</a>", 
                                     text)
        text = self.hash_pattern.sub(
            r"<a href='https://twitter.com/search?q=%23\1'>#\1</a>", text)

        text = text.replace('"', '&quot;')
        text = text.replace('\n', '<br>')

        return text

add_markup = AddedHtmlMarkup()
