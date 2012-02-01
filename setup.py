#!/usr/bin/python

import os
import glob
from distutils.core import setup

from DistUtilsExtra.command import *
from lib.constants import VERSION

for file in glob.glob('share/*.*'):
    os.chmod(file, 0644)

setup(name = 'gfeedline',
      version = VERSION,
      description = 'Gnome Feed Line',
      long_description = 'A Gnome Social Feed Reader.',
      author = 'Yoshizumi Endo',
      author_email = 'y-endo@ceres.dti.ne.jp',
      url = 'http://code.google.com/p/gfeedline/',
      license = 'GPL3',
      package_dir = {'gfeedline' : 'lib'},
      packages = ['gfeedline', 'gfeedline.utils',
                  'gfeedline.preferences', 'gfeedline.twittytwister',
                  'gfeedline.plugins', 'gfeedline.plugins.twitter', ],
      scripts = ['gfeedline'],
      data_files = [('share/gfeedline', ['share/assistant_twitter.glade',
                                         'share/feedsource.glade',
                                         'share/gfeedline.glade',
                                         'share/preferences.glade',
                                         'share/update.glade', ]),
                    ('share/gfeedline/html', 
                     [ 'share/html/default.css',
                       'share/html/base.html',
                       'share/html/status.html',
                       'share/html/retweet.png',
                       'share/html/scrollsmoothly.js', ])],
      cmdclass = {"build" : build_extra.build_extra,
                  "build_i18n" : build_i18n.build_i18n,
                  "build_icons" : build_icons.build_icons}
      )
