#!/usr/bin/python
#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from lib.utils import gtk3reactor
gtk3reactor.install()
from twisted.internet import reactor

from lib.liststore import FeedListStore


if __name__ == '__main__':

    liststore = FeedListStore()
    reactor.run()
