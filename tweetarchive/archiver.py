#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import uuid
import base64
import tweepy
import hashlib
import logging
import requests
from settings import *
from datetime import datetime
from contextlib import closing
from hanzo.warctools import WarcRecord
from warcwriterpool import warc_datetime_str

LOGGING_FORMAT="[%(asctime)s] %(levelname)s: %(message)s"
logging.basicConfig( format=LOGGING_FORMAT, level=logging.WARNING )
logger = logging.getLogger( "archiver" )

class StreamListener( tweepy.StreamListener ):
	def __init__( self, writer, media=False ):
		self.writer = writer
		self.media = media

	def httpheaders( self, original ):
		status_line = "HTTP/%s %s %s" % (
			".".join( str( original.version ) ),
			original.status,
			original.reason
		)
		headers = [ status_line ]
		try:
			headers.extend( "%s: %s" % header for header in original.msg._headers )
		except AttributeError:
			headers.extend( h.strip() for h in original.msg.headers )
		return "%s\r\n\r\n" % "\r\n".join( headers )

	def write_media( self, parsed ):
		"""Stored media as a 'response'; stores other URLs as URL-agnostic revisits."""
		for media in parsed[ "entities" ][ "media" ]:
			r = requests.get( media[ "media_url" ] )
			if r.ok:
				ruid = "<urn:uuid:%s>" % uuid.uuid1()
				cdate = warc_datetime_str( datetime.now() )
				rhash = "sha1:%s" % base64.b32encode( hashlib.sha1( r.content ).digest() )
				headers = [
					( WarcRecord.TYPE, WarcRecord.RESPONSE ),
					( WarcRecord.URL, media[ "media_url" ] ),
					( WarcRecord.DATE, cdate ),
					( WarcRecord.ID, ruid ),
					( "WARC-Payload-Digest", rhash ),
					( WarcRecord.CONTENT_TYPE, "application/http; msgtype=response" ),
				]
				block = "".join( [ self.httpheaders( r.raw._original_response ), r.content ] )
				self.writer.write_record( headers, "application/http; msgtype=response", block )
	
				for alt in [ "media_url_https", "url" ]:
					headers = [
						( WarcRecord.TYPE, "revisit" ),
						( WarcRecord.URL,  media[ alt ] ),
						( WarcRecord.DATE, cdate ),
						( "WARC-Profile", "http://netpreserve.org/warc/1.0/revisit/identical-payload-digest" ),
						( WarcRecord.ID, "<urn:uuid:%s>" % uuid.uuid1() ),
						( WarcRecord.REFERS_TO, ruid ),
						( WarcRecord.CONCURRENT_TO, ruid ),
						( "WARC-Payload-Digest", rhash ),
						( "WARC-Refers-To-Target-URI", media[ "media_url" ] ),
						( "WARC-Refers-To-Date", cdate ),
						( "WARC-Truncated", "length" ),
						( WarcRecord.CONTENT_TYPE, "application/http; msgtype=response" ),
					]
					with closing( requests.get( media[ alt ], stream=True, verify=False ) ) as r:
						block = self.httpheaders( r.raw._original_response )
					self.writer.write_record( headers, "application/http; msgtype=response", block )

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

			if self.media and parsed[ "entities" ].has_key( "media" ):
				self.write_media( parsed )
		except KeyError:
			logger.error( "KeyError: " + data )

