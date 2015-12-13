GFeedLine - A Social Networking Client
======================================

About
-----

GFeedLine is a social networking client.
It supports Twitter, Facebook & Tumblr.

Installation
------------

### Depends

  - Python: 2.6 or 2.7
  - python-gobject
  - gir1.2-gtk-3.0
  - gir1.2-webkit-3.0 (> 1.6)
  - Twisted: twisted.internet & twisted.web
  - python-openssl
  - python-beautifulsoup
  - python-oauth
  - python-dateutil
  - python-xdg

### Recommends

  - python-libproxy: for Gnome Proxy Settings
  - gnome-sushi: as image previewer
  - python-gtkspellcheck: for spell checking

### Installation

The gschema file *must* be installed.

    sudo cp ./share/com.googlecode.gfeedline.gschema.xml.in /usr/share/glib-2.0/schemas/com.googlecode.gfeedline.gschema.xml
    sudo glib-compile-schemas /usr/share/glib-2.0/schemas

You can install with the setup script.

    sudo python ./setup.py install --force

Or, you can launch without installation. (Some functions are restricted.)

    ./gfeedline

Contact
-------

Web: https://github.com/yendo/gfeedline  
E-mail: yendo0206@gmail.com  
Twitter: yendo0206

Local variables:  
mode: markdown  
end:
