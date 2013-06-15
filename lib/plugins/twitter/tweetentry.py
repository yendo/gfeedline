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
TweetEntry -- RestRetweetEntry  -- FeedRetweetEntry -- MyFeedRetweetEntry
           |- DirectMessageEntry
           \- FeedEventEntry
"""


class TweetEntryDict(dict):

    def __init__(self, **init_dict):
        super(TweetEntryDict, self).__init__(dict(init_dict))
        self.setdefault('pre_username', '')
        self.setdefault('post_username', '')
        self.setdefault('event', '')
        self.setdefault('child', '')
        self.setdefault('onmouseover', 'toggleCommand(this, &quot;command&quot;)')

    def __getitem__(self, key):
        if key == 'permalink' and 'permalink' not in self:
            val = 'gfeedline://twitter.com/%s/status/%s' % (
                self['user_name'], self._get_entry_id(self['id']))
        elif key == 'userlink':
            val = 'gfeedlinetw://user/%s/' % self['user_name']
        elif key == 'user_name2':
            val = '@'+self['user_name']
        else:
            val = super(TweetEntryDict, self).__getitem__(key)

        return val

    def _get_entry_id(self, entry_id):
        return entry_id.split('-')[0] if str(entry_id).find('-') > 0 else entry_id

class TweetEntry(object):

    def __init__(self, entry):
        self.entry = entry
        self.retweet_by_screen_name = ''
        self.retweet_by_name = ''

    def get_dict(self, api):
        entry = self.entry

        time = TimeFormat(entry.created_at)
        body_string = self._get_body(entry.text) # FIXME
        entities = entry.raw['entities'] if entry.raw else entry.entities
        body = TwitterEntities().convert(body_string, entities)

        user = self._get_sender(api)

        styles = self._get_styles(api, user.screen_name, entry)

        if entry.in_reply_to_status_id and str(entry.id).find('-') >= 0:
            target = ("<div class='target'>"
                      "<a href='gfeedlinetw://moreconversation/%s/%s'>%s</a>"
                      "</div>") % ( str(entry.id).split('-')[1], 
                entry.in_reply_to_screen_name, _('View more in conversation'))
        else:
            target = ''

        entry_dict = TweetEntryDict(
            date_time=time.get_local_time(),
            id=entry.id,
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
            command=self._get_commands(entry, user, api),
            target=target
            )

        return entry_dict

    def _get_styles(self, api, screen_name, entry=None):
        style_obj = EntryStyles()
        return style_obj.get(api, screen_name, entry)

    def _get_commands(self, entry, user, api):
        is_liked = entry.favorited

        if not isinstance(is_liked, bool):
            is_liked = is_liked == 'true'

        entry_info = '%s/%s' % (entry.id, user.screen_name)

        replylink =   'gfeedlinetw://reply/%s' % entry_info
        retweetlink = 'gfeedlinetw://retweet/%s' % entry_info
        deletelink =  'gfeedlinetw://delete/%s' % entry_info
        favlink =     'gfeedlinetw://fav/%s' % entry_info
        unfavlink =   'gfeedlinetw://unfav/%s' % entry_info
        morelink =    'gfeedlinetw://more/%s' % entry_info

#        "<a href='%s' title='%s'><i class='%s'></i><span class='%s'>%s</span></a>"

        # Reply
        commands = "<a href='%s' title='%s'><i class='icon-reply icon-large'></i><span class='label'>%s</span></a> " % (replylink, _('Reply'), _('Reply'))

        # Retweet FIXME
        is_protected = entry.user.protected \
            if hasattr(entry.user, 'protected') else entry.user.get('protected')
        if not is_protected and api.account.user_name != user.screen_name:
            commands += "<a href='%s' title='%s'><i class='icon-retweet icon-large'></i><span class='label'>%s</span></a> " % (retweetlink, _('Retweet'), _('Retweet'))

        # Delete
        if api.account.user_name == user.screen_name:
            commands += "<a href='%s' title='%s'><i class='icon-trash icon-large'></i><span class='label'>%s</span></a> " % (deletelink, _('Delete'), _('Delete'))

        # Favorite
        commands += (
        "<a href='%s' title='%s' class='like-first %s' onclick='like(this)'><i class='icon-star icon-large'></i><span class='label'>%s</span></a> "
        "<a href='%s' title='%s' class='like-second %s' style='color:red;' onclick='like(this)'><i class='icon-star icon-large'></i><span class='label'>%s</span></a> "

#        "<a href='%s' title='More' class='icon-double-angle-right icon-large'>More</a>"
        ) % (
            favlink, _('Favorite'), 'hidden' if is_liked else '', _('Favorite'), 
            unfavlink, _('Favorite'), '' if is_liked else 'hidden', _('Favorite'), 
            # morelink
            )

        if entry.in_reply_to_status_id and str(entry.id).find('-') < 0:
            conversationlink = 'gfeedlinetw://conversation/%s-%s/%s' % (
                entry.id, entry.in_reply_to_status_id, user.screen_name)

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

        if not styles_string:
            styles_string = "normaltweet"
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

    def _get_commands(self, entry, user, api):
        entry_info = '%s/%s' % (entry.id, user.screen_name)

        # replylink =   'gfeedlinetw://replydm/%s' % entry_info
        deletelink =  'gfeedlinetw://deletedm/%s' % entry_info

        # Delete
        commands = "<a href='%s' title='%s'><i class='icon-trash icon-large'></i><span class='label'>%s</span></a> " % (deletelink, _('Delete'), _('Delete'))

        return commands

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
        user = self.original_entry.raw['user']
        created_at = self.original_entry.created_at
        body = _('retweeted your Tweet')

        target_date_time = self._get_target_date_time(
            self.entry, self.entry.user['screen_name'])
        target_body = self.original_entry.raw['retweeted_status']['text']

        target ="""
    <div class='target'>
      <span class='body'>%s</span> 
      <span class='datetime'>%s</span>
    </div>
""" % (target_body, target_date_time)

        entry_dict = TweetEntryDict(
            date_time=TimeFormat(created_at).get_local_time(),
            id='',
            styles='twitter event',

            image_uri=user['profile_image_url'],
            retweet='',
            in_reply_to = '',

            user_name=user['screen_name'],
            full_name=user['name'],
            user_color=user_color.get(user['screen_name']),
            protected=self._get_protected_icon(user['protected']),
            source=self._decode_source_html_entities(self.original_entry.source),
            permalink="https://twitter.com/%s" % user['screen_name'],

            status_body='',
            popup_body="%s %s" % (user['name'], body),

            event=body,
            target=target,

            pre_username = '',
            post_username = ' ',

            onmouseover='',
            command='',
            )

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
            permalink="https://twitter.com/%s" % entry.source.screen_name,

            status_body='',
            popup_body="%s %s" % (entry.source.name, body),

            event=body,
            target=target,

            pre_username = '',
            post_username = ' ',

            command='',
            onmouseover='',
#            target_body=target_body,
#            target_date_time=target_date_time,
            )

        return entry_dict

    def get_sender_name(self, api=None):
        pass

    def get_full_name(self, entry):
        pass

    def get_source_name(self):
        pass

class TwitterEntities(object):

    def convert(self, text, entities):
        ent = {}
        offset = 0

        for key, val in entities.items():
            for i in val:
                ent[i['indices'][0]] = key, i

        for key, value in sorted(ent.items()):
            entity, v = value
            start, end = key, v['indices'][1]

            if entity == 'urls':
                expanded_url = v['expanded_url']
                alt = "<a href='%s' title='%s'>%s</a>" % (
                    expanded_url, expanded_url, v['display_url'])

                if expanded_url.startswith("http://twitpic.com/"):
                    twitpic_id = expanded_url.replace("http://twitpic.com/", '')
                    url = 'http://twitpic.com/show/%s/' + twitpic_id
                    text = self._add_image(text, url % 'full', url % 'thumb')

                if expanded_url.endswith((".jpg", ".jpeg", ".png", ".gif")):
                    text = self._add_image(text, expanded_url, expanded_url)

            elif entity == 'user_mentions':
                url = 'gfeedlinetw://user/%s/' % v['screen_name']
                alt = "<span class='%s'>@<a href='%s' title='%s'>%s</a></span>" % (
                    'user-mentions', url, v['name'], v['screen_name'])

            elif entity == 'hashtags':
                url = 'gfeedlinetw://hashtag/#%s/' % v['text']
                alt = "<span class='%s'>#<a href='%s'>%s</a></span>" % (
                    'hashtags', url, v['text'])

            elif entity == 'media':
                height = self._get_image_height(v['sizes']['large'])
                alt = "<a href='%s'>%s</a>" % (v['expanded_url'], v['display_url'])
                url = v['media_url_https']
                text = self._add_image(text, url+":large", url+":small", height)

            else:
                alt = text[start+offset:end+offset]

            text = text[:start+offset] + alt + text[end+offset:]
            offset += start-end+len(alt)
        
#        print text

#        text = unescape(text)
#        text = escape(text, {"'": '&apos;'}) # Important!
        text = text.replace('"', '&quot;')
        text = text.replace('\r\n', '\n')
        text = text.replace('\n', '<br>')

        return text

    def _add_image(self, text, link_url, image_url, height=90):
        link_url = link_url.replace('http', 'gfeedlineimg', 1)
        img = ("<div class='image'>"
               "<a href='%s'><img src='%s' height='%s'></a></div>") % (
            link_url, image_url, height)
        text = text + img
        return text

    def _get_image_height(self, image):
        w = image['w']
        h = image['h']

        tmp_h = 160 * h / w
        new_h = tmp_h if w > h and tmp_h < 90 else 90
        return new_h

class DictObj(object):

    def __init__(self, d):
        self.d = d

    def __getattr__(self, m):
        return self.d.get(m, None)
