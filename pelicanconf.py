#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Stéphane Travostino'
SITENAME = u'Stéphane Travostino'
SITEURL = 'http://combo.cc'

PATH = 'content'
ARTICLE_PATHS = ['articles']
ARTICLE_SAVE_AS = 'articles/{slug}.html'
ARTICLE_URL = 'articles/{slug}.html'

TIMEZONE = 'Europe/London'

DEFAULT_LANG = u'en'

DEFAULT_DATE_FORMAT = '%B %d, %Y'

THEME = 'themes/combo'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
MENUITEMS = (('Github', 'https://github.com/1player'),)

# Social widget
#SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

TYPOGRIFY = True
