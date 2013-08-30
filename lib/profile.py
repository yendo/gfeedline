import os

from gi.repository import Gtk

from utils.urlgetautoproxy import UrlGetWithAutoProxy
from constants import SHARED_DATA_FILE, CACHE_HOME

class ProfilePane(object):

    def __init__(self):
        self.gui = gui = Gtk.Builder()
        self.gui.add_from_file(SHARED_DATA_FILE('profile.glade'))
        self.gui.connect_signals(self)

        self.widget =  self.gui.get_object('profile')
        self.widget.hide()

    def set_profile(self, entry):
        label_name = self.gui.get_object('label_name')
        label_name.set_label('<b><big>%s</big></b>' % entry.get('name'))

        label_screen_name =  self.gui.get_object('label_screen_name')
        label_screen_name.set_label("@"+entry.get('screen_name'))

        description = ''
        if entry.get('description'):
            entities = entry.get('entities')['description']
            description = self._convert(entry['description'], entities)
        self._set_label('label_description', description)

        location = ''
        if entry.get('location'):
            location += entry.get('location')
            if entry.get('url'):
                location += ' &#183; '
        if entry.get('url'):
            url = entry['entities']['url']['urls'][0]
            location += '<a href="%s">%s</a>' % (
                url['expanded_url'], url['display_url'])
        self._set_label('label_location', location)

        dic = {'count_tweets': entry['statuses_count'], 
               'count_following': entry['friends_count'], 
               'count_followers': entry['followers_count']}
        for label, text in dic.items():
            self.gui.get_object(label).set_label(str(text))

        self.widget.show()

        icon_uri = str(entry['profile_image_url']).replace('_normal.', '_bigger.')
        icon_file = os.path.join(CACHE_HOME, 'profile_icon.jpg')

        urlget = UrlGetWithAutoProxy(icon_uri)
        d = urlget.downloadPage(icon_uri, icon_file)
        d.addCallback(self._set_profile_icon, icon_file)  

    def _set_label(self, label_name, text):
        label = self.gui.get_object(label_name)
        if text:
            label.set_label("<small>%s</small>" % text)
        else:
            label.hide()

    def _set_profile_icon(self, data, icon_file):
        icon =  self.gui.get_object('icon')
        icon.set_from_file(icon_file)

    def on_button_close_clicked(self, button):
        self.widget.hide()

    def _convert(self, text, entities):
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

            elif entity == 'user_mentions':
                pass

            elif entity == 'hashtags':
                url = 'https://twitter.com/search?q=#%s/' % v['text']
                alt = "<span class='%s'>#<a href='%s'>%s</a></span>" % (
                    'hashtags', url, v['text'])

            else:
                alt = text[start+offset:end+offset]

            text = text[:start+offset] + alt + text[end+offset:]
            offset += start-end+len(alt)
        
        text = text.replace('&', '&amp;')
        text = text.replace('\r', '')
        text = text.replace('\n', ' ')

        return text
