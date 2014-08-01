#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import tweepy
import logging
import argparse
from tweetarchive.settings import *
from tweetarchive import StreamListener
from warcwriterpool import WarcWriterPool

def screen_names_to_ids(auth, screen_names):
    api = tweepy.API(auth)
    chunks = [screen_names[x:x+100] for x in xrange(0, len(screen_names), 100)]
    ids = []
    for chunk in chunks:
        result_set = api.lookup_users(screen_names=chunk)
        ids += [str(u.id) for u in result_set]
    return ids

if __name__ == "__main__":
    auth = tweepy.OAuthHandler( TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET )
    auth.set_access_token( TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET )

    logger = logging.getLogger( "archiver" )
    logger.setLevel( logging.WARNING )
    logger.addHandler( logging.StreamHandler( sys.stdout ) )
    logging.root.setLevel( logging.WARNING )

    parser = argparse.ArgumentParser( description="Archiving tweets." )
    parser.add_argument( "-u", "--users", type=str, help="Comma-separated list of users to follow." )
    parser.add_argument( "-t", "--terms", type=str, help="Comma-separated list of terms to track." )
    args = parser.parse_args()

    users = []
    terms = []
    if args.users is not None:
        users = args.users.split( "," )
    if args.terms is not None:
        terms = args.terms.split( "," )
    if len( users + terms ) == 0:
        parser.print_help()
        sys.exit( 1 )

    w = WarcWriterPool( gzip=True )
    try:
        if len(users) > 0:
            users = screen_names_to_ids(auth, users)
        stream = tweepy.Stream( auth=auth, listener=StreamListener( writer=w ) )
        stream.filter( follow=users, track=terms )
    except KeyboardInterrupt as k:
        w.cleanup()
        sys.exit( 0 )

