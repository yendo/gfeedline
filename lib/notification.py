#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import webbrowser

from updatewindow import UpdateWindow
from utils.notification import Notification
from utils.urlgetautoproxy import UrlGetWithAutoProxy


class StatusNotification(Notification):

    def __init__(self, notification):
        super(StatusNotification, self).__init__('Gnome Feed Line')

    def notify(self, entry):
        icon_uri = str(entry['image_uri'])
        entry['icon_path'] = '/tmp/twitter_profile_image.jpg'
 
        urlget = UrlGetWithAutoProxy(icon_uri)
        d = urlget.downloadPage(icon_uri, entry['icon_path']).\
            addCallback(self._notify, entry).addErrback(self._error)
 
    def _notify(self, unknown, entry):
        super(StatusNotification, self).notify(
            entry['icon_path'], entry['user_name'], entry['popup_body'], entry)

    def on_dbus_signal(self, proxy, sender_name, signal_name, params):
        if signal_name == "ActionInvoked":
            id, action_string = params.unpack()
            action, user, id = action_string.split(' ')
            
            if action == 'reply':
                print "replay"
                update_window = UpdateWindow(None, user, id)
        
            elif action == 'open':
                uri = 'https://twitter.com/%s/status/%s' % (user, id)
                print "open"
                webbrowser.open(uri)

    def _get_actions(self, entry):
        #print entry
        user = entry['user_name']
        id = entry['id']

        return  ['reply %s %s' % (user, id), _('Reply'),
                 'open %s %s'  % (user, id), _('Open')]

    def _error(self, *e):
        print "icon get error!", e
