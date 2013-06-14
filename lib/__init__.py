import gettext
import locale
from constants import APP_NAME

LOCALE_DIR = '/usr/share/locale'

for module in (gettext, locale):
    module.bindtextdomain(APP_NAME, LOCALE_DIR)
    module.textdomain(APP_NAME)

gettext.install(APP_NAME, LOCALE_DIR, unicode=True)
