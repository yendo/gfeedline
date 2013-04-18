#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os
import webbrowser
import base64
import cPickle as pickle

from constants import CACHE_HOME
from updatewindow import UpdateWindow
from utils.notification import Notification
from utils.urlgetautoproxy import UrlGetWithAutoProxy


class StatusNotification(Notification):

    def __init__(self, notification):
        super(StatusNotification, self).__init__('GFeedLine')
        # Can't access dbus when auto-start.
        # self.has_actions = 'actions' in self.get_capabilities()
        self.icon_file = os.path.join(CACHE_HOME, 'notification_icon.jpg')

    def notify(self, entry):
        icon_uri = str(entry['image_uri'])

        urlget = UrlGetWithAutoProxy(icon_uri)
        d = urlget.downloadPage(icon_uri, self.icon_file)
        d.addCallback(self._notify, entry).addErrback(self._error, entry)

    def _notify(self, unknown, entry):
        user_name = entry['user_name'] or entry['full_name']
        super(StatusNotification, self).notify(
            self.icon_file, user_name, entry['popup_body'], entry)

    def on_dbus_signal(self, proxy, sender_name, signal_name, params):
        if signal_name == "ActionInvoked":
            notify_id, action_string = params.unpack()

            action_array = action_string.split(' ')
            action = action_array[0]
            entry_base64 = ' '.join(action_array[1:])
            if entry_base64: # for a GNOME Classic bug
                entry_pickle = base64.b64decode(entry_base64)
                entry_dict = pickle.loads(entry_pickle)

            if action == 'reply':
                entry_dict['status_body'] = entry_dict['popup_body']
                UpdateWindow(None, entry_dict)
            elif action == 'open':
                uri = entry_dict['permalink'].replace('gfeedline://', 'https://')
                webbrowser.open(uri)

    def _get_actions(self, entry):
        #print entry
        self.has_actions = 'actions' in self.get_capabilities()
        if self.has_actions and entry.get('id'):
            entry_pickle = pickle.dumps(entry)
            entry_base64 = base64.b64encode(entry_pickle)

            actions = ['reply %s' % entry_base64, _('Reply'),
                       'open %s'  % entry_base64, _('Open')]
        else:
            actions = []

        return actions

    def _error(self, *args):
        print "Notification call back error: ", args
