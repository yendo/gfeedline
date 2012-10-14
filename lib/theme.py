#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os
from string import Template

from gi.repository import Pango

from constants import SHARED_DATA_FILE, THEME_HOME
from utils.settings import SETTINGS_VIEW


class Theme(object):

    def __init__(self):
        self.template = {}

        self.all_themes = {}
        theme_system = SHARED_DATA_FILE('html/theme/')

        alllist = [(theme_system, p) for p in os.listdir(theme_system)] +\
            [(THEME_HOME, p) for p in os.listdir(THEME_HOME)]

        for path, filename in alllist:
            full_path = os.path.join(path, filename)
            if not os.path.isdir(full_path):
                continue

            name = filename.split('.')[0]
            self.all_themes.setdefault(name, {})
            self.all_themes[name]['dir'] = full_path

            if filename.count('Ascending'):
                self.all_themes[name]['is_ascending'] = True

        SETTINGS_VIEW.connect("changed::theme", self.on_setting_theme_changed)
        self.on_setting_theme_changed(SETTINGS_VIEW, 'theme')

    def is_ascending(self, save_value=None):
        if save_value == None:
            save_value = SETTINGS_VIEW.get_int('timeline-order')

        if save_value == 0: # default
            theme_name = self._get_theme_name()
            is_ascending = bool(self.all_themes[theme_name].get('is_ascending'))
        else:
            is_ascending = save_value == 1

        return is_ascending

    def get_all_list(self):
        return self.all_themes.keys()

    def get_css_file(self):
        theme_name = self._get_theme_name()
        css_file = os.path.join(self.all_themes[theme_name]['dir'], 'default.css') \
             if theme_name in self.all_themes else ''

        if not os.path.isfile(css_file):
            css_file = SHARED_DATA_FILE('html/theme/Twitter/default.css')

        return css_file

    def _get_theme_name(self):
        return SETTINGS_VIEW.get_string('theme')

    def on_setting_theme_changed(self, settings, key): # get_status_template
        theme_name = self._get_theme_name()

        for style in ['status', 'event', 'retweet', 'protected', 
                      'image', 'linkbox', 'like']:
            template_file = os.path.join(
                self.all_themes[theme_name]['dir'], '%s.html' % style) \
                if theme_name in self.all_themes else ''

            if not os.path.isfile(template_file):
                template_file = SHARED_DATA_FILE(
                    'html/theme/Twitter/%s.html' % style)

            with open(template_file, 'r') as fh:
                file = fh.read()

            self.template[style] = Template(unicode(file, 'utf-8', 'ignore'))

class FontSet(object):

    def __init__(self):
        self.font_template, self.size = self._get_default()

    def zoom_in(self):
        self.size = int(round(self.size * 1.2))
        css = self.font_template % self.size
        return css

    def zoom_out(self):
        self.size = int(round(self.size / 1.2))
        css = self.font_template % self.size
        return css

    def zoom_default(self):
        self.font_template, self.size = self._get_default()
        css = self.font_template % self.size
        return css

    def _get_default(self):
        font_name = SETTINGS_VIEW.get_string('font')
        pango_font = Pango.font_description_from_string(font_name)

        size = int(font_name.rpartition(' ')[-1])
        style = pango_font.get_style().value_nick
        weight = pango_font.get_weight().real
        family = pango_font.get_family()

        font_template = "%s %s %%spt '%s'" % (style, weight, family)
        #print font_template

        return font_template, size
