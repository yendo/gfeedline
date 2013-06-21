import os
from os.path import abspath, dirname
from stat import S_IMODE

from xdg.BaseDirectory import *

VERSION = '2.3-b1'
APP_NAME = 'gfeedline'

SHARED_DATA_DIR = abspath(os.path.join(dirname(__file__), '../share'))
if not os.access(os.path.join(SHARED_DATA_DIR, 'gfeedline.glade'), os.R_OK):
    SHARED_DATA_DIR = '/usr/share/gfeedline'

# DATA_HOME = os.path.join(xdg_data_home, APP_NAME)
CACHE_HOME = os.path.join(xdg_cache_home, APP_NAME)
CONFIG_HOME = os.path.join(xdg_config_home, APP_NAME)
THEME_HOME = os.path.join(CONFIG_HOME, 'theme')

for dir in [CACHE_HOME, CONFIG_HOME, THEME_HOME]:
    if not os.path.isdir(dir):
        os.makedirs(dir, 0700)
    elif S_IMODE(os.stat(dir).st_mode) != 0700:
        os.chmod(dir, 0700)

def SHARED_DATA_FILE(file):
    return os.path.join(SHARED_DATA_DIR, file)

class Column(object):

    (GROUP, ICON, SOURCE, USERNAME, NAME, TARGET, ARGUMENT, 
     OPTIONS, ACCOUNT, API) = range(10)
