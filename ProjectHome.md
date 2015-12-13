GFeedLine is a social networking client.
It supports Twitter, Facebook & Tumblr.

# FAQ #

## If you select "Home Timeline" on Twitter as a target, the time line is not updated in real time. "User Stream" is recommended. ##

## Twitterのターゲットに「ホームタイムライン」を選択するとリアルタイムに更新されません。「ユーザーストリーム」を選択してください。 ##

![http://www.tsurukawa.org/~yendo/blog/images/120209-gfeedline.png](http://www.tsurukawa.org/~yendo/blog/images/120209-gfeedline.png)

_Translate gfeedline: you can check the [gfeedline transifex page](http://www.transifex.net/projects/p/gfeedline/)._

# Releases #

## 2.4.6 release (2015-07-12) ##

  * Fixed a Twitter authorization error ([issue #77](https://code.google.com/p/gfeedline/issues/detail?id=#77)).
  * Added new gstting key [view/auto-scroll-delay](https://code.google.com/p/gfeedline/issues/detail?id=41#c4).
  * Updated Catalan translation. Thanks Adolfo Jayme Barrientos!
  * Updated Dutch translation. Thanks Heimen Stoffels!
  * Fixed bugs.


## 2.4.5 release (2015-05-09) ##

  * Fixed a Twitter authorization error ([issue #77](https://code.google.com/p/gfeedline/issues/detail?id=#77)).

## 2.4.4 release (2015-02-13) ##

  * Improved auto scroll stop timer.
  * Fixed Facebook image links ([issue #76](https://code.google.com/p/gfeedline/issues/detail?id=#76)).
  * Added AppData.

## 2.4.3 release (2014-11-30) ##

  * Added support for multiple images on Twitter entries (except search API).
  * Added support for Twisted 14.0.0.
  * Added Asturian translation. Tanks Ḷḷumex03!
  * Updated Spanish translation. Thanks Adolfo Jayme Barrientos!
  * Updated Dutch translation. Thanks Heimen Stoffels!
  * Fixed bugs.

## 2.4.2 release (2014-08-21) ##

  * Fixed Facebook authentication expiration problem ([issue 71](https://code.google.com/p/gfeedline/issues/detail?id=71)).
  * Fixed the bug that UserStream loses the connection by suspend ([issue 72](https://code.google.com/p/gfeedline/issues/detail?id=72)).
  * Updated translation.

## 2.4.1 release (2013-10-26) ##

  * Added support for thumbnails on Instagram.
  * Added Polish translation.  Thanks hakunamatata!
  * Updated Arabic translation.  Thanks Humaidan Mohammed!
  * Updated French translation.   Thanks madx!
  * Fixed bugs related to notifications.

## 2.4 release (2013-09-01) ##

  * Added support for the system font setting ([issue #36](https://code.google.com/p/gfeedline/issues/detail?id=#36)).
  * Added support for inserting all @users when replying ([issue #56](https://code.google.com/p/gfeedline/issues/detail?id=#56)).
  * Added support for clearing tabs.
  * Added a kludge for removing redundant error messages ([issue #30](https://code.google.com/p/gfeedline/issues/detail?id=#30)).
  * Added checking user account for sending events to reply tabs ([issue #46](https://code.google.com/p/gfeedline/issues/detail?id=#46)).
  * Fixed a problem that is caused in Twisted 13.1. ([issue #57](https://code.google.com/p/gfeedline/issues/detail?id=#57)).
  * Fixed a bug that prevents retweet notices.
  * Removed a redundant escaping # in URLs ([issue #59](https://code.google.com/p/gfeedline/issues/detail?id=#59)).
  * Added new French translation.  Thanks madx!
  * Updated translation.


# Depends #

  * Python: 2.6 or 2.7
  * python-gobject
  * gir1.2-gtk-3.0
  * gir1.2-webkit-3.0
  * Twisted: twisted.internet & twisted.web
  * python-openssl
  * python-beautifulsoup
  * python-oauth
  * python-dateutil
  * python-xdg

# Installation #

The gschema file must be installed.

```
  sudo cp ./share/com.googlecode.gfeedline.gschema.xml.in /usr/share/glib-2.0/schemas/com.googlecode.gfeedline.gschema.xml

  sudo glib-compile-schemas /usr/share/glib-2.0/schemas
```

You can install with the setup script.
```
  sudo python ./setup.py install --force
```

Or, you can launch without installation.

```
  ./gfeedline
```