# GFeedLine Themes #

GFeedline supports user custom themes which use HTML+CSS.
The default 'Default' theme files are in /usr/share/gfeedline/html/theme/Default.

# User Common Custom CSS #

You can add your common custom CSS to the following file.

```
 ~/.config/gfeedline/theme/custom.css
```

# Creating custom themes #

User custom theme directory is in ~/.config/gfeedline/theme.
You can put your own custom theme in the directory.

For example, you could create 'New' theme.

```
 % cp -a /usr/share/gfeedline/html/theme/Default ~/.config/gfeedline/theme/New
```

All theme files are:

  * bubble.html
  * default.css
  * image.html
  * linkbox.html
  * retweet.html
  * status.html

You can chaged the HTML & CSS files in your custom theme directory.
It is possible to delete theme files not modified.
These HTML files include python templates.
Some substitute keywords (ex: $username) are available.