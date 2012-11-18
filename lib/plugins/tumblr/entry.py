# -*- coding: utf-8 -*-

import re
from xml.sax.saxutils import escape, unescape

# from BeautifulSoup import BeautifulSoup
# from django.utils.text import Truncator

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

#     def truncate_html(self, html, length, end_text='...'):
#         truncate = end_text and ' %s' % end_text or ''
#         return Truncator(html).words(length, truncate=truncate)
# 
#     def truncate_html2(self, html, length): 
# 
#         a = unicode(BeautifulSoup(html[:length]))
#         b = unicode(BeautifulSoup(html))
# 
#         if len(a) < len(b):
#             a+='...'
#             print a
#         return a

    def get_dict(self, api):
        entry = self.entry
        body = entry.get('text') or entry.get('body') or entry.get('caption') or ''

        # body = self.truncate_html(body, 10)
        # print body

        time = TimeFormat(entry['date'])

        if entry.get('source'):
            body +=  "<div class='source'>%s</div>" % entry.get('source')

        body = add_markup.convert(body)

        image_uri = 'http://api.tumblr.com/v2/blog/%s.tumblr.com/avatar/30' \
            % entry.get('blog_name')

        if entry.get('type') == 'photo':
            url =  entry['photos'][0]['alt_sizes'][2]['url']
            template = self.theme.template['image']
            key_dict = {'url': url}
            body = template.substitute(key_dict) + body

        entry_dict = dict(
            date_time=time.get_local_time(),
            id=entry['id'],
            styles='tumblr',
            image_uri=image_uri,
            permalink=entry['post_url'],

            command='',

            retweet='',
            retweet_by_screen_name='',
            retweet_by_name='',

            pre_username='',
            post_username='',
            event='',

            in_reply_to='',

            user_name=entry['blog_name'],
            user_name2=entry['type'],
            full_name=entry['blog_name'],
            user_color=user_color.get(entry['blog_name']),
            protected='',
            source='',

            status_body=body,
            popup_body='',
            target=''
            )

        return entry_dict

class AddedTumblrHtmlMarkup(AddedHtmlMarkup):

    def __init__(self):
        super(AddedTumblrHtmlMarkup, self).__init__()

        num = 5
        self.new_lines = re.compile('^(([^\n]*\n){%d})(.*)' % num, re.DOTALL)

    def convert(self, text):
        text = text.replace('target="_blank"', "")
        # text = super(AddedTumblrHtmlMarkup, self).convert(text)
#        text = text.replace('"', '&quot;')
        text = text.replace('"', "'")

#        text = self.new_lines.sub(
#            ("\\1"
#             "<span class='main-text'>...<br>"
#             "<a href='#' onclick='readMore(this); return false;'>%s</a>"
#             "</span>"
#             "<span class='more-text'>\\3<br>"
#             "<a href='#' onclick='readMore(this); return false;'>%s</a>"
#             "</span>") % (_('See more'), _('See less')), 
#            text)

#        text = text.replace('\n', '<br>')
        return text

add_markup = AddedTumblrHtmlMarkup()
