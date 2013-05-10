import urllib

try:
    import libproxy
except ImportError:
    libproxy = False

from urlget import UrlGetWithProxy


class AutoProxy(object):

    def get_proxy(self, url):
        if not libproxy: return ""
        pf = libproxy.ProxyFactory()
        for proxy in pf.getProxies(url):
            if proxy.startswith('http'):
                return proxy

        return ""

class UrlGetWithAutoProxy(UrlGetWithProxy):

    def __init__(self, url):
        self.url = url
        proxy_url = AutoProxy().get_proxy(url)
        super(UrlGetWithAutoProxy, self).__init__(proxy_url)

    def catch_error(self, error):
        # print "Failure: %s: %s" % (error.getErrorMessage(), self.url)
        print error
        print self.url

def urlget_with_autoproxy(url, arg=None, cb=None, **kargs):
    if arg:
        url += urllib.urlencode(arg)
    client = UrlGetWithAutoProxy(url)
    d = client.getPage(url, **kargs)
    if cb:
        d.addCallback(cb)
    d.addErrback(client.catch_error)

    return d

def urlpost_with_autoproxy(url, arg, cb=None, method='POST'):
    client = UrlGetWithAutoProxy(url)
    content_type = {'Content-Type' : 'application/x-www-form-urlencoded'}

    d = client.getPage(url, method=method,
                       postdata = urllib.urlencode(arg),
                       headers = content_type)
    if cb:
        d.addCallback(cb)
    d.addErrback(client.catch_error)

    return d

if __name__ == "__main__":
    pac = ParseProxyPac()
    print pac.get_proxy("http://master/")
    print pac.get_proxy("http://master.edu/")
