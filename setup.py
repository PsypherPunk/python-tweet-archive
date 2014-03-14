from distutils.core import setup

setup(
	name="python-tweet-archive",
	version="1.0.1",
	author="PsypherPunk",
	author_email="psypherpunk@gmail.com",
	packages=[ "tweetarchive" ],
	description="Tweet archiver.",
	long_description=open( "README.md" ).read(),
	install_requires=[
		"hanzo-warctools",
		"tweepy",
		"python-warcwriterpool",
	],
	data_files=[
		( "/usr/local/bin", [ "archiver.py" ] ),
	]
)
