# -*- coding: utf-8 -*-

import re
from xml.sax.saxutils import escape, unescape

from ...utils.usercolor import UserColor
from ...utils.timeformat import TimeFormat
from ...utils.htmlentities import decode_html_entities
from ...theme import Theme
from ..twitter.tweetentry import AddedHtmlMarkup

user_color = UserColor()


class TumblrEntry(object):

    def __init__(self, entry):
        self.entry = entry
        self.theme = Theme()

    def get_dict(self, api):
        entry = self.entry
        body = entry.get('text') or entry.get('body') or entry.get('caption') or ''
        body = add_markup.convert(body)

        image_uri = 'http://api.tumblr.com/v2/blog/%s.tumblr.com/avatar/30' \
            % entry.get('blog_name')

     
        if entry.get('type') == 'photo':
            url =  entry['photos'][0]['alt_sizes'][2]['url']
            template = self.theme.template['image']
            key_dict = {'url': url}
            body = template.substitute(key_dict) + body


        entry_dict = dict(
            date_time=entry['date'],
            id=entry['id'],
            styles='tumblr',
            image_uri=image_uri,
            permalink='',

            command='',

            retweet='',
            retweet_by_screen_name='',
            retweet_by_name='',

            pre_username='',
            post_username='',
            event='',

            in_reply_to='',

            user_name=entry['blog_name'],
            user_name2='',
            full_name=entry['blog_name'],
            user_color=user_color.get(entry['blog_name']),
            protected='',
            source='',

            status_body=body,
            popup_body='',
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

class AddedTumblrHtmlMarkup(AddedHtmlMarkup):

    def __init__(self):
        super(AddedTumblrHtmlMarkup, self).__init__()

        num = 5
        self.new_lines = re.compile('^(([^\n]*\n){%d})(.*)' % num, re.DOTALL)

    def convert(self, text):
        # text = super(AddedTumblrHtmlMarkup, self).convert(text)
        text = text.replace('"', '&quot;')

        text = self.new_lines.sub(
            ("\\1"
             "<span class='main-text'>...<br>"
             "<a href='#' onclick='readMore(this); return false;'>%s</a>"
             "</span>"
             "<span class='more-text'>\\3<br>"
             "<a href='#' onclick='readMore(this); return false;'>%s</a>"
             "</span>") % (_('See more'), _('See less')), 
            text)
#        text = text.replace('\n', '<br>')
        return text

add_markup = AddedTumblrHtmlMarkup()
