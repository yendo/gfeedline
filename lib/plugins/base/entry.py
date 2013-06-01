import re
from xml.sax.saxutils import escape, unescape

class AddedHtmlMarkup(object):

    def __init__(self):
        self.link_pattern = re.compile(
            r"(s?https?://[-_.!~*'a-zA-Z0-9;/?:@&=+$,%#]+)", 
            re.IGNORECASE | re.DOTALL)

    def convert(self, text):
        text = unescape(text)
        text = escape(text, {"'": '&apos;'}) # Important!
        text = self.link_pattern.sub(r"<a href='\1'>\1</a>", text)
        text = text.replace('"', '&quot;')
        text = text.replace('\r\n', '\n')

        return text
