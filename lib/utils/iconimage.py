import os

from gi.repository import Gtk, GdkPixbuf

from ..constants import SHARED_DATA_DIR, CACHE_HOME
from urlgetautoproxy import UrlGetWithAutoProxy


class IconImage(object):

    def __init__(self, icon_name='image-x-generic'):
        self.icon_name = icon_name

    def get_image(self, size=16):
        self.size = size
        pixbuf = self.get_pixbuf()

        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        return image

    def get_pixbuf(self, grayscale=False, size=16):
        self.size = size
        file = self._get_icon_file()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(file, size, size, True)

        if grayscale:
            pixbuf = self._set_grayscale(pixbuf)

        return pixbuf

    def _get_icon_file(self):
        theme = Gtk.IconTheme.get_default()
        info = theme.lookup_icon(self.icon_name, self.size, 0) or \
            theme.lookup_icon('image-x-generic', self.size, 0)
        return info.get_filename()

    def _set_grayscale(self, pixbuf):
        pixbuf_gray = pixbuf.copy()
        pixbuf.saturate_and_pixelate(pixbuf_gray, 0.0, False)
        return pixbuf_gray

class LocalIconImage(IconImage):

    def _get_icon_file(self):
        icon_path = os.path.join(SHARED_DATA_DIR, self.icon_name)
        return icon_path

class WebIconImage(IconImage):

    def _get_icon_file(self):
        file = os.path.join(CACHE_HOME, self.icon_name)

        if not os.access(file, os.R_OK):
            self._download_icon(self.icon_url, self.icon_name)

            super(WebIconImage, self).__init__()
            file = super(WebIconImage, self)._get_icon_file()

        return file

    def _download_icon(self, icon_url, icon_name):
        icon_file = os.path.join(CACHE_HOME, icon_name)
        urlget = UrlGetWithAutoProxy(icon_url)
        d = urlget.downloadPage(icon_url, icon_file)
