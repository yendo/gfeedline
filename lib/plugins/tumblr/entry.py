# -*- coding: utf-8 -*-

import re
from xml.sax.saxutils import escape, unescape

from ...utils.usercolor import UserColor
from ...utils.timeformat import TimeFormat
from ...utils.htmlentities import decode_html_entities
from ...utils.truncatehtml import truncate_html
from ...theme import Theme
from ..twitter.tweetentry import AddedHtmlMarkup

user_color = UserColor()


class TumblrEntry(object):

    def __init__(self, entry):
        self.entry = entry
        self.theme = Theme()

    def get_dict(self, api):
        entry = self.entry
        body = self._get_body(entry)

        return self._get_entry_dict(entry, body)

    def _get_body(self, entry):
        link = "<a href='%s' title='%s'>......</a>" % (
            entry['post_url'], _('Read more'))
        body = entry.get('text') or entry.get('body') or entry.get('caption') or ''
        body = truncate_html(body, 140, link)

        if entry.get('type') == 'quote':
            body = u'“%s”' % body

        if entry.get('source'):
            source = truncate_html(entry.get('source'), 80)
            body +=  "<div class='source'>%s</div>" % source

        return body

    def _get_entry_dict(self, entry, body):
        image_uri = 'http://api.tumblr.com/v2/blog/%s.tumblr.com/avatar/40' \
            % entry.get('blog_name')

        entry_dict = dict(
            date_time=TimeFormat(entry['date']).get_local_time(),
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

            status_body=add_markup.convert(body),
            popup_body='',
            target=''
            )

        return entry_dict

class TumblrTextEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        body = self._get_body(entry)

        title = entry.get('title')
        if title:
            body = '<p><b>%s</b></p>%s' % (title, body)

        return self._get_entry_dict(entry, body)

class TumblrPhotosEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        body = self._get_body(entry)

        new_body = "<div class='image'>"
        # template = self.theme.template['image']

        for photo in entry['photos']:
            url =  photo['alt_sizes'][2]['url']
            # key_dict = {'url': url}
            # new_body += template.substitute(key_dict)
            new_body += "<img height='90' src='%s'>" % url

        new_body += "</div>" + body

        return self._get_entry_dict(entry, new_body)

class TumblrLinkEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        body = self._get_body(entry)

        url = entry.get('url')
        title = entry.get('title') or url
        link = "<p><a href='%s'>%s</a><p>" % (url, title)
        body = link + body

        return self._get_entry_dict(entry, body)

class TumblrChatEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        entry['body'] = entry['body'].replace('\r', '').replace('\n', '<br>')
        body = self._get_body(self.entry)

        title = self.entry.get('title')
        if title:
            body = '<p><b>%s</b></p>%s' % (title, body)

        return self._get_entry_dict(self.entry, body)

class TumblrAudioEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        body = ""

        artist = entry.get('artist')
        track_name = entry.get('track_name')
        album = entry.get('album')
        image = entry.get('album_art')

        if artist:
            body = ("<p>%s</p>" % artist) + body
        if track_name:
            body = ("<p>%s</p>" % track_name) + body
        if album:
            body = ("<p>%s</p>" % album) + body

        if image:
            template = self.theme.template['image']
            key_dict = {'url': image}
            body += template.substitute(key_dict)

        body += self._get_body(entry)
        return self._get_entry_dict(entry, body)

class TumblrVideoEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        body = self._get_body(entry)

        template = self.theme.template['image']
        key_dict = {'url': entry['thumbnail_url']}
        body = template.substitute(key_dict) + body
        return self._get_entry_dict(entry, body)

class TumblrAnswerEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        name = entry.get('asking_name')
        url = entry.get('asking_url')

        image = 'http://api.tumblr.com/v2/blog/%savatar/40' % \
            url.replace('http://', '') if url else \
            'http://www.tumblr.com/images/anonymous_avatar_40.gif'

        template = self.theme.template['bubble']
        key_dict = {'image_uri': image,
                    'permalink': url,
                    'text': entry.get('question'),
                    }
        body = template.substitute(key_dict)
        body += entry.get('answer')

        return self._get_entry_dict(entry, body)

class AddedTumblrHtmlMarkup(AddedHtmlMarkup):

    def __init__(self):
        super(AddedTumblrHtmlMarkup, self).__init__()

        num = 5
        self.new_lines = re.compile('^(([^\n]*\n){%d})(.*)' % num, re.DOTALL)

    def convert(self, text):
        text = text.replace('target="_blank"', "")
        # text = super(AddedTumblrHtmlMarkup, self).convert(text)
        # text = text.replace('"', '&quot;')
        text = text.replace('"', "'")
        text = text.replace('\r', '')
        text = text.replace('\n', '')

        return text

add_markup = AddedTumblrHtmlMarkup()
