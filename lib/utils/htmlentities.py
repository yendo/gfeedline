import re
import copy
import urllib

from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup

# replace hexadecimal character reference by decimal one
hexentityMassage = copy.copy(BeautifulSoup.MARKUP_MASSAGE)
hexentityMassage += [(re.compile('&#x([^;]+);'), 
                      lambda m: '&#%d;' % int(m.group(1), 16))]

def decode_html_entities(text):
    soup = BeautifulStoneSoup(
        text, convertEntities=BeautifulStoneSoup.HTML_ENTITIES,
        markupMassage=hexentityMassage)
    return unicode(soup)

def decode_url_entities(text):
    return decode_html_entities(urllib.unquote(text))
