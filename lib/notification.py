#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os
import webbrowser

from constants import TMP_DIR
from updatewindow import UpdateWindow
from utils.notification import Notification
from utils.urlgetautoproxy import UrlGetWithAutoProxy


class StatusNotification(Notification):

    def __init__(self, notification):
        super(StatusNotification, self).__init__('Gnome Feed Line')
        self.has_actions = 'actions' in self.get_capabilities()
        self.icon_file = os.path.join(TMP_DIR, 'notification_icon.jpg')

    def notify(self, entry):
        icon_uri = str(entry['image_uri'])

        urlget = UrlGetWithAutoProxy(icon_uri)
        d = urlget.downloadPage(icon_uri, self.icon_file).\
            addCallback(self._notify, entry).addErrback(self._error)
 
    def _notify(self, unknown, entry):
        super(StatusNotification, self).notify(
            self.icon_file, entry['user_name'], entry['popup_body'], entry)

    def on_dbus_signal(self, proxy, sender_name, signal_name, params):
        if signal_name == "ActionInvoked":
            notify_id, action_string = params.unpack()
            action, user, entry_id = action_string.split(' ')
            
            if action == 'reply':
                pass
#                entry_dict = self.all_entries[ int(entry_id)]
#                update_window = UpdateWindow(None, entry_dict)
            elif action == 'open':
                uri = 'https://twitter.com/%s/status/%s' % (user, entry_id)
                webbrowser.open(uri)

    def _get_actions(self, entry):
        #print entry
        if self.has_actions:
            user = entry['user_name']
            entry_id = entry['id']

            actions = ['reply %s %s' % (user, entry_id), _('Reply'),
                       'open %s %s'  % (user, entry_id), _('Open')]
        else:
            actions = []

        return actions

    def _error(self, *e):
        print "icon get error!", e
