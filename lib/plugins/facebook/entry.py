# -*- coding: utf-8 -*-

import re
from xml.sax.saxutils import escape, unescape

from ...utils.usercolor import UserColor
from ...utils.timeformat import TimeFormat
from ...utils.htmlentities import decode_html_entities
from ...theme import Theme
from ..base.entry import AddedHtmlMarkup

user_color = UserColor()


class FacebookEntry(object):

    def __init__(self, entry):
        self.entry = entry
        self.theme = Theme()

    def get_dict(self, api):
        entry = self.entry

        time = TimeFormat(entry['created_time'])
        body_string = entry.get('message') or entry.get('story') or entry.get('caption') or entry.get('name') or ''

        if not body_string:
            print "skip!"
            print entry
            return None

        body = add_markup.convert(body_string) # add_markup is global

        userid, postid = entry['id'].split('_')
        permalink = ('gfeedline://www.facebook.com/permalink.php'
                     '?id=%s&v=wall&story_fbid=%s') % (userid, postid)

        if entry['type'] == 'photo':
            template = self.theme.template['image']
            url = entry['picture']
            link = url.replace('http', 'gfeedlineimg').replace('_s.', '_n.')
            key_dict = {'url': url, 'link': link}
            body += template.substitute(key_dict)

        if entry.get('description'):
            template = self.theme.template['linkbox']
            key_dict = {'url': entry.get('link'),
                        'name': add_markup.cut(entry.get('name')),
                        'caption': add_markup.cut(entry.get('caption')),
                        'description': add_markup.convert(entry.get('description'))
                        }
            body += template.substitute(key_dict).replace('\r', '') # Unexpected EOF

        command=''
        if entry.get('actions'):
            is_liked = False
            if entry.get('likes'):
                for i in entry['likes'].get('data'):
                    if i['id'] == api.account.idnum:
                        is_liked =True
                        break

            likelink = 'gfeedlinefblike://%s' % entry['id']
            unlikelink = 'gfeedlinefbunlike://%s' % entry['id']

            command = (
                "<a class='like-first %s'  href='%s' onclick='like(this);'>%s</a>"
                "<a class='like-second %s' href='%s' onclick='like(this);'>%s</a>"
                u" · <a href='%s'>%s</a> · ") % (
                'hidden' if is_liked else '', likelink,   _('Like'),
                '' if is_liked else 'hidden', unlikelink, _('Unlike'), 
                permalink, _('Comment'))

        entry_dict = dict(
            date_time=time.get_local_time(),
            epoch=time.get_epoch(),
            id=entry['id'],
            styles='facebook',
            image_uri='https://graph.facebook.com/%s/picture' % entry['from']['id'],
            permalink=permalink,
            userlink='http://www.facebook.com/%s' % userid,

            command=command,
            onmouseover='',

            retweet='',
            retweet_by_screen_name='',
            retweet_by_name='',

            pre_username='',
            post_username='',
            event='',

            in_reply_to='',

            user_name=entry['from']['name'],
            user_name2='', # entry['type'],
            full_name=entry['from']['name'],
            user_color=user_color.get(entry['from']['name']),
            protected='',
            source='',

            status_body=body,
            popup_body=body_string,
            target='',
            child=''
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

class AddedFacebookHtmlMarkup(AddedHtmlMarkup):

    def __init__(self):
        super(AddedFacebookHtmlMarkup, self).__init__()

        num = 5
        self.new_lines = re.compile('^(([^\n]*\n){%d})(.*)' % num, re.DOTALL)

    def convert(self, text):
        text = super(AddedFacebookHtmlMarkup, self).convert(text)
        is_matched = self.new_lines.match(text)

        text = self.new_lines.sub(
            ("\\1"
             "<span class='readmore-first'>...<br>"
             "<a href='#' onclick='readMore(this); return false;'>%s</a>"
             "</span>"
             "<span class='readmore-second'>\\3<br>"
             "<a href='#' onclick='readMore(this); return false;'>%s</a>"
             "</span>") % (_('See more'), _('See less')), 
            text)

        if not is_matched:
            text = self._cut(text, 200)

        text = text.replace('\n', '<br>')
        return text

    def cut(self, text):
        if not text:
            return ''

        text = super(AddedFacebookHtmlMarkup, self).convert(text)
        return self._cut(text)

    def _cut(self, text, num=100):
        if len(text) > num: 
            text = text[:num] + '...'
        return text

add_markup = AddedFacebookHtmlMarkup()
