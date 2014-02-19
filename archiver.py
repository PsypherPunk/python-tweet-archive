#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import tweepy
import logging
import argparse
from tweetarchive.settings import *
from tweetarchive import StreamListener
from warcwriterpool import WarcWriterPool

if __name__ == "__main__":
	auth = tweepy.OAuthHandler( TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET )
	auth.set_access_token( TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET )

	logger = logging.getLogger( "archiver" )
	logger.setLevel( logging.DEBUG )
	logger.addHandler( logging.StreamHandler( sys.stdout ) )

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
		stream = tweepy.Stream( auth=auth, listener=StreamListener( writer=w ) )
		stream.filter( follow=users, track=terms )
	except KeyboardInterrupt as k:
		w.cleanup()
		sys.exit( 0 )

