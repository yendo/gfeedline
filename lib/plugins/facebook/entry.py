# -*- coding: utf-8 -*-

import re
from xml.sax.saxutils import escape, unescape

from ...utils.usercolor import UserColor
from ...utils.timeformat import TimeFormat
from ...utils.htmlentities import decode_html_entities
from ...theme import Theme
from ..twitter.tweetentry import AddedHtmlMarkup

user_color = UserColor()


class FacebookEntry(object):

    def __init__(self, entry):
        self.entry = entry
        self.theme = Theme()

    def get_dict(self, api):
        entry = self.entry

        time = TimeFormat(entry['created_time'])
        body_string = entry.get('message') or entry.get('story') or entry.get('caption') or entry.get('name') or ''

        body = add_markup.convert(body_string) # add_markup is global

        userid, postid = entry['id'].split('_')
        permalink = ('gfeedline://www.facebook.com/permalink.php'
                     '?id=%s&v=wall&story_fbid=%s') % (userid, postid)

        if entry['type'] == 'photo':
            template = self.theme.template['image']
            key_dict = {'url': entry['picture']}
            body += template.substitute(key_dict)

        if entry.get('description'):
            template = self.theme.template['linkbox']
            key_dict = {'url': entry.get('link'),
                        'name': entry.get('name') or '',
                        'caption': entry.get('caption') or '',
                        'description': add_markup.convert(entry.get('description'))
                        }
            body += template.substitute(key_dict)

        command=''
        if entry.get('actions'):
            is_liked = False
            if entry.get('likes'):
                for i in entry['likes'].get('data'):
                    if i['id'] == api.account.idnum:
                        is_liked =True
                        break

            path = '//graph.facebook.com/%s/likes' % entry['id']
            likelink = 'gfeedlinefblike:%s' % path
            unlikelink = 'gfeedlinefbunlike:%s' % path

            command = (
                "<a class='like %s' href='%s' onclick='like(this);'>%s</a>"
                "<a class='unlike %s' href='%s' onclick='like(this);'>%s</a>"
                u" · <a href='%s'>%s</a> · ") % (
                'hidden' if is_liked else '', likelink,   _('Like'),
                '' if is_liked else 'hidden', unlikelink, _('Unlike'), 
                permalink, _('Comment'))


        entry_dict = dict(
            date_time=time.get_local_time(),
            id=entry['id'],
            styles='facebook',
            image_uri='https://graph.facebook.com/%s/picture' % entry['from']['id'],
            permalink=permalink,

            command=command,

            retweet='',
            retweet_by_screen_name='',
            retweet_by_name='',

            pre_username='',
            post_username='',
            event='',

            in_reply_to='',

            user_name=entry['from']['name'],
            user_name2=entry['type'],
            full_name=entry['from']['name'],
            user_color=user_color.get(entry['from']['name']),
            protected='',
            source='',

            status_body=body,
            popup_body=body_string,
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

class AddedFacebookHtmlMarkup(AddedHtmlMarkup):

    def __init__(self):
        super(AddedFacebookHtmlMarkup, self).__init__()

        num = 5
        self.new_lines = re.compile('^(([^\n]*\n){%d})(.*)' % num, re.DOTALL)

    def convert(self, text):
        text = super(AddedFacebookHtmlMarkup, self).convert(text)

        text = self.new_lines.sub(
            ("\\1"
             "<span class='main-text'>...<br>"
             "<a href='#' onclick='readMore(this); return false;'>%s</a>"
             "</span>"
             "<span class='more-text'>\\3<br>"
             "<a href='#' onclick='readMore(this); return false;'>%s</a>"
             "</span>") % (_('See more'), _('See less')), 
            text)
        text = text.replace('\n', '<br>')
        return text

add_markup = AddedFacebookHtmlMarkup()
