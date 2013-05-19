#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012-2013, Yoshizumi Endo.
# Licence: GPL3

import re
from xml.sax.saxutils import escape, unescape

from BeautifulSoup import BeautifulSoup

from ...utils.usercolor import UserColor
from ...utils.timeformat import TimeFormat 
from ...utils.htmlentities import decode_html_entities

user_color = UserColor()

"""
TweetEntry -- RestRetweetEntry  -- FeedRetweetEntry
           \- FeedEventEntry
"""

class TweetEntryDict(dict):

    def __init__(self, **init_dict):
        super(TweetEntryDict, self).__init__(dict(init_dict))
        self.setdefault('pre_username', '')
        self.setdefault('post_username', '')
        self.setdefault('event', '')
        self.setdefault('child', '')
        self.setdefault('onmouseover', 'toggleShow(this, &quot;command&quot;)')

    def __getitem__(self, key):
        if key == 'permalink':
            val = 'gfeedline://twitter.com/%s/status/%s' % (
                self['user_name'], self['id'])
        elif key == 'user_name2':
            val = '@'+self['user_name']

        else:
            val = super(TweetEntryDict, self).__getitem__(key)

        return val

class TweetEntry(object):

    def __init__(self, entry):
        self.entry = entry
        self.retweet_by_screen_name = ''
        self.retweet_by_name = ''

    def get_dict(self, api):
        entry = self.entry

        time = TimeFormat(entry.created_at)
        body_string = self._get_body(entry.text) # FIXME
        body = add_markup.convert(body_string) # add_markup is global
        user = self._get_sender(api)

        styles = self._get_styles(api, user.screen_name, entry)

        entry_dict = TweetEntryDict(
            date_time=time.get_local_time(),
            id=str(entry.id).split('-')[0], # for replied status
            styles='twitter %s' % styles,
            image_uri=user.profile_image_url,

            retweet='',
            retweet_by_screen_name=self.retweet_by_screen_name,
            retweet_by_name=self.retweet_by_name,

            in_reply_to=self._get_in_reply_to_status_id(entry),

            user_name=user.screen_name,
            full_name=user.name,
            user_color=user_color.get(user.screen_name),
            protected=self._get_protected_icon(user.protected),
            source=self._get_source(entry),

            status_body=body,
            popup_body=body_string,
            command=self._get_commands(entry),
            target=''
            )

        return entry_dict

    def _get_styles(self, api, screen_name, entry=None):
        style_obj = EntryStyles()
        return style_obj.get(api, screen_name, entry)

    def _get_commands(self, entry):
        entry_id = entry.id
        is_liked = entry.favorited

        if not isinstance(is_liked, bool):
            is_liked = is_liked == 'true'

        replylink =   'gfeedlinetw://reply/%s' % entry_id
        retweetlink = 'gfeedlinetw://retweet/%s'  % entry_id
        favlink =     'gfeedlinetw://fav/%s' % entry_id
        unfavlink =   'gfeedlinetw://unfav/%s' % entry_id
        morelink =    'gfeedlinetw://more/%s' % entry_id

#        "<a href='%s' title='%s'><i class='%s'></i><span class='%s'>%s</span></a>"

        commands = (
        "<a href='%s' title='%s'><i class='icon-reply icon-large'></i><span class='label'>%s</span></a> "
        "<a href='%s' title='%s'><i class='icon-retweet icon-large'></i><span class='label'>%s</span></a> "

        "<a href='%s' title='%s' class='like-first %s' onclick='like(this)'><i class='icon-star icon-large'></i><span class='label'>%s</span></a> "
        "<a href='%s' title='%s' class='like-second %s' style='color:red;' onclick='like(this)'><i class='icon-star icon-large'></i><span class='label'>%s</span></a> "

#        "<a href='%s' title='More' class='icon-double-angle-right icon-large'>More</a>"

        ) % (
            replylink, _('Reply'), _('Reply'),
            retweetlink, _('Retweet'), _('Retweet'), 

            favlink, _('Favorite'), 'hidden' if is_liked else '', _('Favorite'), 
            unfavlink, _('Favorite'), '' if is_liked else 'hidden', _('Favorite'), 
            # morelink
            )

        if entry.in_reply_to_status_id:
            conversationlink = 'gfeedlinetw://conversation/%s-%s' % (
                entry_id, entry.in_reply_to_status_id)

            conv = "<a href='%s' title='%s'><i class='icon-comment icon-large'></i><span class='label'>%s</span></a> " % (
                conversationlink, _('Conversation'), _('Conversation'))
            commands = conv + commands


        return commands

    def _get_source(self, entry):
        return self._decode_source_html_entities(entry.source)

    def get_sender_name(self, api):
        sender = self._get_sender(api)
        return sender.screen_name

    def _get_sender(self, api):
        sender = self.entry.user
        if isinstance(sender, dict):
            sender = DictObj(sender) # FIXME
        return sender

    def get_source_name(self):
        return self._parse_source_html(self.entry.source)

    def _parse_source_html(self, source):
        source = decode_html_entities(source)

        if source.startswith('<a href='):
            soup = BeautifulSoup(source)
            source = [x.contents[0] for x in soup('a')][0]
        return source

    def _get_in_reply_to_status_id(self, entry):
        text = ""
        if entry.in_reply_to_status_id:
            text = "%s/%s" % (entry.in_reply_to_screen_name, 
                              entry.in_reply_to_status_id)
        return text

    def _get_body(self, text):
        text = decode_html_entities(text) # need to decode!
        return text

    def _get_protected_icon(self, attribute):
        icon = "<i class='icon-lock'></i>"
        return icon if attribute and attribute != 'false' else ''

    def _decode_source_html_entities(self, source_html):
        source_html = unescape(source_html)
        return decode_html_entities(source_html).replace('"', "'")

    def _get_target_date_time(self, target_object, original_screen_name):
        "Get the datetime of retweeted original post not retweeting post."

        date_time = TimeFormat(target_object.created_at).get_local_time()
        dt_format = ("(<a href='http://twitter.com/%s/status/%s' "
                     "class='target-datetime'>%s</a>)")
        target_date_time = dt_format % (
            original_screen_name, target_object.id, date_time)

        return target_date_time

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

class DirectMessageEntry(TweetEntry):

    def _get_sender(self, api):
        return DictObj(self.entry.sender)

    def _get_styles(self, api, screen_name, entry):
        return ''

    def _get_source(self, entry):
        return ''

    def get_source_name(self):
        return ''

    def _get_in_reply_to_status_id(self, entry):
        return ''

class RestRetweetEntry(TweetEntry):

    def __init__(self, entry):
        #self.entry=entry.retweeted_status
        #self.retweet_by_screen_name = entry.user.screen_name
        #self.retweet_by_name = entry.user.name
        self.entry=DictObj(entry.retweeted_status)
        self.retweet_by_screen_name = entry.user['screen_name']
        self.retweet_by_name = entry.user['name']

class FeedRetweetEntry(RestRetweetEntry):

    def __init__(self, entry):
        self.entry=entry.retweeted_status
        self.retweet_by_screen_name = entry.user.screen_name
        self.retweet_by_name = entry.user.name

        self.original_entry = entry
        self.entry=DictObj(entry.raw.get('retweeted_status'))

        self.retweet_by_screen_name = entry.raw['user']['screen_name']
        self.retweet_by_name = entry.raw['user']['name']

class MyFeedRetweetEntry(FeedRetweetEntry):

    def get_dict(self, api):
        retweeted_dict = super(FeedRetweetEntry, self).get_dict(api)

        user = self.original_entry.raw['user']
        created_at = self.original_entry.created_at
        body = _('retweeted your Tweet')
        target_date_time = self._get_target_date_time(
            self.entry, self.entry.user['screen_name'])

        entry_dict = TweetEntryDict(
            date_time=TimeFormat(created_at).get_local_time(),
            id='',
            styles='twitter',

            image_uri=user['profile_image_url'],
            retweet='',
            in_reply_to = '',

            user_name=user['screen_name'],
            full_name=user['name'],
            user_color=user_color.get(user['screen_name']),
            protected=self._get_protected_icon(user['protected']),
            source=self.original_entry.source,

            status_body=body,
            popup_body="%s %s" % (user['name'], body),

            event=body,
            target='',

            pre_username = '',
            post_username = ' ',

            command='oops!',

            target_body=retweeted_dict['status_body'],
            target_date_time=target_date_time,)

        return entry_dict

class FeedEventEntry(TweetEntry):

    def get_dict(self, api):
        entry = self.entry

        msg_dict = {
            'favorite': _('favorited your Tweet'),
            'unfavorite': _('unfavorited your Tweet'),
            'follow': _('followed you'),
            'list_member_added': _('added you to list %s'),
            'list_member_removed': _('removed you from list %s'),
            # 'user_update': 'user_update',
            }

        body = msg_dict.get(entry.event) or ''
        if entry.event.startswith('list_member'):
            body = body % entry.raw['target_object']['uri'][1:]

        if hasattr(entry, 'target_object') and hasattr(entry.target_object, 'text'):
            target_body = entry.target_object.text
            target_date_time = self._get_target_date_time(
                entry.target_object, entry.target.screen_name)
        else:
            target_body = ''
            target_date_time = ''

        target ="""
    <div class='target'>
      <span class='body'>%s</span> 
      <span class='datetime'>%s</span>
    </div>
""" % (target_body, target_date_time)


        entry_dict = TweetEntryDict(
            date_time=TimeFormat(entry.created_at).get_local_time(),
            id='',
            styles='twitter event',
            image_uri=entry.source.profile_image_url,
            retweet='',
            in_reply_to = '',

            user_name=entry.source.screen_name,
            full_name=entry.source.name,
            user_color=user_color.get(entry.source.screen_name),
            protected=self._get_protected_icon(entry.source.protected),
            source='',

            status_body='',
            popup_body="%s %s" % (entry.source.name, body),

            event=body,
            target=target,

            pre_username = '',
            post_username = ' ',

            command='',
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

class AddedHtmlMarkup(object):

    def __init__(self):
        self.link_pattern = re.compile(
            r"(s?https?://[-_.!~*'a-zA-Z0-9;/?:@&=+$,%#]+)", 
            re.IGNORECASE | re.DOTALL)

    def convert(self, text):
        text = unescape(text)
        text = escape(text, {"'": '&apos;'}) # Important!
        text = self.link_pattern.sub(r"<a href='\1'>\1</a>", text)
        text = text.replace('"', '&quot;')
        text = text.replace('\r\n', '\n')

        return text

class AddedTwitterHtmlMarkup(AddedHtmlMarkup):

    def __init__(self):
        super(AddedTwitterHtmlMarkup, self).__init__()

        self.nick_pattern = re.compile("\B@([A-Za-z0-9_]+|@[A-Za-z0-9_]$)")
        self.hash_pattern = re.compile(
            u'(?:#|\uFF03)([a-zA-Z0-9_'
            u'\u3041-\u3094\u3099-\u309C\u30A1-\u30FF\u3400-\uD7FF'
            u'\uFF10-\uFF19\uFF20-\uFF3A\uFF41-\uFF5A\uFF66-\uFF9E]+)')

    def convert(self, text):
        text = super(AddedTwitterHtmlMarkup, self).convert(text)

        text = self.nick_pattern.sub(
            r"<a href='https://twitter.com/\1'>@\1</a>", text)
        text = self.hash_pattern.sub(
            r"<a href='https://twitter.com/search?q=%23\1'>#\1</a>", text)
        text = text.replace('\n', '<br>')
        return text

add_markup = AddedTwitterHtmlMarkup()
