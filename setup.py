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
      description = 'GFeedLine',
      long_description = 'A Social Networking Client',
      author = 'Yoshizumi Endo',
      author_email = 'y-endo@ceres.dti.ne.jp',
      url = 'http://code.google.com/p/gfeedline/',
      license = 'GPL3',
      package_dir = {'gfeedline' : 'lib'},
      packages = ['gfeedline', 'gfeedline.utils',
                  'gfeedline.preferences', 'gfeedline.twittytwister',
                  'gfeedline.plugins', 'gfeedline.plugins.base',
                  'gfeedline.plugins.twitter',
                  'gfeedline.plugins.facebook',
                  'gfeedline.plugins.tumblr',
                  ],
      scripts = ['gfeedline'],
      data_files = [('share/gfeedline', ['share/assistant_twitter.glade',
                                         'share/assistant_facebook.glade',
                                         'share/filters.glade',
                                         'share/feedsource.glade',
                                         'share/gfeedline.glade',
                                         'share/notebook_popup_menu.glade',
                                         'share/preferences.glade',
                                         'share/retweet.glade',
                                         'share/select_assistant.glade',
                                         'share/update.glade', ]),
                    ('share/indicators/messages/applications',
                     [ 'share/gfeedline.indicator', ]),
                    ('share/gfeedline/html',
                     [ 'share/html/default.css',
                       'share/html/base.html',
                       'share/html/key.png',
                       'share/html/retweet.png',
                       'share/html/gfeedline.js',
                       'share/html/toggleshow.js',
                       'share/html/scrollsmoothly.js', ]),
                    ('share/gfeedline/html/theme/Chat.Ascending',
                     [ 'share/html/theme/Chat.Ascending/status.html',
                       'share/html/theme/Chat.Ascending/image.html',
                       'share/html/theme/Chat.Ascending/retweet.html',
                       'share/html/theme/Chat.Ascending/default.css', ]),
                    ('share/gfeedline/html/theme/Default',
                     [ 'share/html/theme/Default/status.html',
                       'share/html/theme/Default/retweet.html',
                       'share/html/theme/Default/protected.html',
                       'share/html/theme/Default/image.html',
                       'share/html/theme/Default/linkbox.html',
                       'share/html/theme/Default/bubble.html',
                       'share/html/theme/Default/default.css', ]),
                    ('share/gfeedline/html/theme/RTL',
                     [ 'share/html/theme/RTL/default.css', ]),
                    ('share/gfeedline/html/theme/Bubble',
                     [ 'share/html/theme/Bubble/default.css', ]), ],
      cmdclass = {"build" : build_extra.build_extra,
                  "build_i18n" : build_i18n.build_i18n,
                  "build_icons" : build_icons.build_icons}
      )
