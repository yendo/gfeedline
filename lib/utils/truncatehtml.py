import re

from BeautifulSoup import BeautifulSoup

re_word = re.compile('\w')

def truncate_html(html, length, ellipsis="."*6): 

    is_tag = False
    body_counter = 0
    
    for i, char in enumerate(html):
        if is_tag == True:
            if char == '>':
                is_tag = False
        elif char == '<':
            is_tag = True
        else:
            if body_counter >= length:
                if not re_word.match(char):
                    # print i, body_counter, char
                    return unicode(BeautifulSoup(html[:i] + ellipsis))
            elif char != "\n":
                body_counter += 1

    return html
