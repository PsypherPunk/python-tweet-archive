python-tweet-archive
====================

Archive tweets to WARC files.

This relies on [python-warcwriterpool](https://github.com/ukwa/python-warcwriterpool) which should be installed beforehand.

To install simply clone the repo:

    git clone https://github.com/ukwa/python-tweet-archive.git

For OAuth authentication, a new app. will have to be registered at
https://dev.twitter.com/ and the corresponding details updated in
settings.py. After that, to install run:

    pip install ./python-tweet-archive

This should handle the dependencies.After that you can simply run it from a command line:

    usage: archiver.py [-h] [-u USERS] [-t TERMS]

    Archiving tweets.

    optional arguments:
      -h, --help            show this help message and exit
      -u USERS, --users USERS
                           Comma-separated list of users to follow.
      -t TERMS, --terms TERMS
                            Comma-separated list of terms to track.

