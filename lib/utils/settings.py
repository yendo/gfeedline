from gi.repository import Gio

def get_settings(key=""):
    base = 'com.googlecode.gfeedline'
    object = Gio.Settings.new(base + key)
    return object

SETTINGS = get_settings()
SETTINGS_PLUGINS = get_settings('.plugins')
SETTINGS_TWITTER = get_settings('.plugins.twitter')
