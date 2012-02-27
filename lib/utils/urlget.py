# Copyright (c) 2001-2008 Twisted Matrix Laboratories.
# Copyright (c) 2009-2011 Yoshizumi Endo.
#
# This urlget is a modified version of twisted.web.client module.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
HTTP Client with proxy support.
"""

import os

from twisted.web import client
from twisted.internet import reactor


class UrlGetWithProxy(object):

    def __init__(self, proxy=None):
        if proxy is None:
            proxy = os.environ.get('http_proxy') or ""
        self.proxy_host, self.proxy_port = client._parse(proxy)[1:3]
        self.use_proxy = bool(self.proxy_host and self.proxy_port)

    def getPage(self, url, contextFactory=None, *args, **kwargs):
        factory = client.HTTPClientFactory(url, *args, **kwargs)
        d = self._urlget(factory, url, contextFactory)
        return d

    def downloadPage(self, url, file, contextFactory=None, *args, **kwargs):
        factory = client.HTTPDownloader(url, file, *args, **kwargs)
        d = self._urlget(factory, url, contextFactory)
        return d

    def _urlget(self, factory, url, contextFactory=None):
        scheme, host, port, path = client._parse(url)
        if self.use_proxy and scheme != 'https': # HTTPS proxy isn't supported.
            host, port = self.proxy_host, self.proxy_port
            factory.path = url
        if scheme == 'https':
            from twisted.internet import ssl
            if contextFactory is None:
                contextFactory = ssl.ClientContextFactory()
            reactor.connectSSL(host, port, factory, contextFactory)
        else:
            reactor.connectTCP(host, port, factory)
        return factory.deferred
