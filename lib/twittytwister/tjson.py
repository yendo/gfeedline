# Copyright (c) 2012 Alexander Duryagin <aduryagin@gmail.com>
# https://raw.github.com/daa/twitty-twister/master/twittytwister/tjson.py

import json

from . import streaming

class Parser(object):
    """
    A file-like thingy that parses a JSON feed.
    """

    def __init__(self, handler):
        self.data=[]
        self.handler=handler

    def write(self, b):
        self.data.append(b)

    def close(self):
        self.handler(parse(''.join(self.data)) if self.data else None)

    def open(self):
        pass

    def read(self):
        return None

    def __enter__(self):
        return self

    def __exit__(self):
        pass

parse = json.loads
