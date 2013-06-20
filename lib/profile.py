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

    def on_button_close_clicked(self, button):
        self.widget.hide()

    def set_profile(self, entry):
        label_name =  self.gui.get_object('label_name')
        label_name.set_label('<b><big>%s</big></b>' % entry.get('name'))

        label_screen_name =  self.gui.get_object('label_screen_name')
        label_screen_name.set_label("@"+entry.get('screen_name'))

        description = ''
        if entry.get('description'):
            description += entry.get('description'
                                     ).replace('\r', '').replace('\n', ' ')
            if entry.get('location') or entry.get('url'):
                description += '\n'
        if entry.get('location'):
            description += entry.get('location')
            if entry.get('url'):
                description += ' &#183; '
        if entry.get('url'):
            url = entry['entities']['url']['urls'][0]
            description += '<a href="%s">%s</a>' % (
                url['expanded_url'], url['display_url'])

        label_description = self.gui.get_object('label_description')
        label_description.set_label("<small>%s</small>" % description)

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

    def _set_profile_icon(self, data, icon_file):
        icon =  self.gui.get_object('icon')
        icon.set_from_file(icon_file)

