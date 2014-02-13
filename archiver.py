#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import uuid
import tweepy
import logging
import argparse
from settings import *
from datetime import datetime
from hanzo.warctools import WarcRecord
from warcwriterpool import WarcWriterPool
from hanzo.warctools.warc import warc_datetime_str

auth = tweepy.OAuthHandler(  TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET  )
auth.set_access_token(  TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET  )

logger = logging.getLogger( "archiver" )
logger.setLevel( logging.DEBUG )
logger.addHandler( logging.StreamHandler( sys.stdout ) )

parser = argparse.ArgumentParser( description="Archiving tweets." )
parser.add_argument( "-u", "--users", type=str, help="Comma-separated list of users to follow." )
parser.add_argument( "-t", "--terms", type=str, help="Comma-separated list of terms to track." )
args = parser.parse_args()

class StreamListener( tweepy.StreamListener ):
	def __init__( self, writer ):
		self.writer = writer

	def on_status( self, tweet ):
		logger.info( "Ran on_status" )

	def on_error( self, status_code ):
		logger.error( "Error: " + repr( status_code ) )

	def on_data( self, data ):
		parsed = json.loads( data )
		try:
			user = parsed[ "user" ][ "screen_name" ]
			id = parsed[ "id" ]
			url = "https://twitter.com/%s/statuses/%s" % ( user, id )
			headers = [
				( WarcRecord.TYPE, WarcRecord.RESOURCE ),
				( WarcRecord.URL, url ),
				( WarcRecord.CONTENT_TYPE, "application/json" ),
				( WarcRecord.DATE, warc_datetime_str( datetime.now() ) ),
				( WarcRecord.ID, "<urn:uuid:%s>" % uuid.uuid1() ),
			]
			self.writer.write_record( headers, "application/json", data )
		except KeyError:
			logger.error( "KeyError: " + data )

if __name__ == "__main__":
	users = []
	terms = []
	if args.users is not None:
		users = args.users.split( "," )
	if args.terms is not None:
		terms = args.terms.split( "," )
	if len( users + terms ) == 0:
		parser.print_help()
		sys.exit( 1 )

	w = WarcWriterPool( gzip=False )
	try:
		stream = tweepy.Stream( auth=auth, listener=StreamListener( writer=w ) )
		stream.filter( follow=users, track=terms )
	except KeyboardInterrupt as k:
		w.cleanup()
		sys.exit( 0 )

