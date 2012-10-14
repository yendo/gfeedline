import re
import urllib

from gi.repository import GObject, Gtk, Gdk, WebKit


class FacebookWebKitScrolledWindow(Gtk.ScrolledWindow):

    app_id = 203600696439990

    def __init__(self):
        super(FacebookWebKitScrolledWindow, self).__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        values = { 'client_id': self.app_id,
                   'redirect_uri': 
                   'http://www.facebook.com/connect/login_success.html',
                   'response_type': 'token',
                   'scope': 'user_photos,friends_photos,read_stream,offline_access,publish_stream',
                   'display': 'popup'}
        uri = 'https://www.facebook.com/dialog/oauth?' + urllib.urlencode(values)

        w = WebKit.WebView.new()
        w.set_vexpand(True)
        w.load_uri(uri)
        w.connect("document-load-finished", self._get_document_cb)

        self.add(w)
        self.show_all()

    def _get_document_cb(self, w, e):
        url = w.get_property('uri')
        re_token = re.compile('.*access_token=(.*)&.*')
        login_url = 'https://www.facebook.com/login.php?'
        error_url = 'http://www.facebook.com/connect/login_success.html?error'

        if url.startswith(login_url):
            self.emit("login-started", None)
        elif re_token.search(url):
            token = re_token.sub("\\1", url)
            self.emit("token-acquired", token)
        elif url.startswith(error_url):
            self.emit("error-occurred", None)

for signal in ["login-started", "token-acquired", "error-occurred"]:
    GObject.signal_new(signal, FacebookWebKitScrolledWindow,
                       GObject.SignalFlags.RUN_LAST, None,
                       (GObject.TYPE_PYOBJECT,))
