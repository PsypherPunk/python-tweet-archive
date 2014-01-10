python-tweet-archive
====================

Archive tweets to WARC files.

Only esoteric requirements are hanzo.warctools and tweepy, both of which which 
can be install via [Pip](http://www.pip-installer.org/en/latest/):

    pip install hanzo-warctools
    pip install tweepy

For OAuth authentication, a new app. will have to be registered at 
https://dev.twitter.com/ and the corresponding details updated in 
settings.py.

    usage: archiver.py [-h] [-u USERS] [-t TERMS]

    Archiving tweets.

    optional arguments:
      -h, --help            show this help message and exit
      -u USERS, --users USERS
                           Comma-separated list of users to follow.
      -t TERMS, --terms TERMS
                            Comma-separated list of terms to track.
