#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import uuid
import tweepy
from settings import *
from datetime import datetime
from hanzo.warctools import WarcRecord
from hanzo.warctools.warc import warc_datetime_str

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

