import re
from gi.repository import Gtk, GObject, WebKit

class AuthWebKitScrolledWindow(Gtk.ScrolledWindow):

    def __init__(self):
        super(AuthWebKitScrolledWindow, self).__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
       
        url = self._get_auth_url()

        w = WebKit.WebView.new()
        w.set_vexpand(True)
        w.load_uri(url)
        w.connect("document-load-finished", self._get_document_cb)

        self.add(w)
        self.show_all()

    def _get_document_cb(self, w, e):
        url = w.get_property('uri')
        re_token = re.compile(self.RE_TOKEN)

        if url.startswith(self.LOGIN_URL):
            self.emit("login-started", None)
        elif re_token.search(url):
            self.emit("token-acquired", url)
        elif url.startswith(self.ERROR_URL):
            self.emit("error-occurred", None)

for signal in ["login-started", "token-acquired", "error-occurred"]:
    GObject.signal_new(signal, AuthWebKitScrolledWindow,
                       GObject.SignalFlags.RUN_LAST, None,
                       (GObject.TYPE_PYOBJECT,))
