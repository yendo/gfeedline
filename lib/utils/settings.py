from gi.repository import Gio

def get_settings(key=""):
    base = 'com.googlecode.gfeedline'
    object = Gio.Settings.new(base + key)
    return object

SETTINGS = get_settings()
SETTINGS_VIEW = get_settings('.view')
SETTINGS_GEOMETRY = get_settings('.geometry')
SETTINGS_PLUGINS = get_settings('.plugins')
SETTINGS_TWITTER = get_settings('.plugins.twitter')
SETTINGS_FACEBOOK = get_settings('.plugins.facebook')
SETTINGS_TUMBLR = get_settings('.plugins.tumblr')
