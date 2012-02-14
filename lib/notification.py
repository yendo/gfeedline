#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os
import webbrowser
import cPickle as pickle

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

            action_array = action_string.split(' ')
            action = action_array[0]
            entry_pickle = ' '.join(action_array[1:])
            entry_dict = pickle.loads(entry_pickle)

            if action == 'reply':
                entry_dict['status_body'] = entry_dict['popup_body']
                update_window = UpdateWindow(None, entry_dict)
            elif action == 'open':
                uri = 'https://twitter.com/%s/status/%s' % (
                    entry_dict['user_name'], entry_dict['id'])
                webbrowser.open(uri)

    def _get_actions(self, entry):
        #print entry
        if self.has_actions:
            entry_pickle = pickle.dumps(entry)
            actions = ['reply %s' % entry_pickle, _('Reply'),
                       'open %s'  % entry_pickle, _('Open')]
        else:
            actions = []

        return actions

    def _error(self, *e):
        print "icon get error!", e
