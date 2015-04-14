#!/bin/python
#! -- encoding: utf8 -- 
import pycurl
import sys
import os
import re
import time
try:
	from io import BytesIO
except ImportError:
	from StringIO import StringIO as BytesIO


headers = {}
def header_function(header_line):
	# HTTP standard specifies that headers are encoded in iso-8859-1.
	# On Python 2, decoding step can be skipped.
	# On Python 3, decoding step is required.
	header_line = header_line.decode('iso-8859-1')

	# Header lines include the first status line (HTTP/1.x ...).
	# We are going to ignore all lines that don't have a colon in them.
	# This will botch headers that are split on multiple lines...
	if ':' not in header_line:
		return

	# Break the header line into header name and value.
	name, value = header_line.split(':', 1)

	# Remove whitespace that may be present.
	# Header lines include the trailing newline, and there may be whitespace
	# around the colon.
	name = name.strip()
	value = value.strip()

	# Header names are case insensitive.
	# Lowercase name here.
	name = name.lower()

	# Now we can actually record the header name and value.
	headers[name] = value

completeness = re.compile(re.escape("</html>"))

def fetchUrl(url):
	response = 0
	body = None
	encoding = None
	while response != 200:
		try:
			buffer = BytesIO()
			c = pycurl.Curl()
			c.setopt(c.URL, url)
			c.setopt(c.WRITEFUNCTION, buffer.write)
			c.setopt(c.FOLLOWLOCATION, True)
			c.setopt(c.HEADERFUNCTION, header_function)
			c.perform()
			response = c.getinfo(c.RESPONSE_CODE)
			c.close()
			body = buffer.getvalue()
			match = re.search('charset=(\S+)', headers['content-type'].lower())
			if match:
				encoding = match.group(1)
			else:
				pass
			if encoding is None:
				encoding = 'utf-8'
			bodydecode = body.decode(encoding, "replace")
			complete = completeness.search(bodydecode)
			if response != 200:
				print "warning: code = %d, refetching ..."%response
				time.sleep(1)
			if not complete:
				print "warning: %s not complete, refetching ..."%link
				response = 800
		except UnicodeDecodeError:
			print "warning: UnicodeDecodeError, refetching"
			response = 801
		finally:
			# If you still need to crawl our site, please issue at most one query every five seconds. Thanks for cooperation!
			time.sleep(5)
	return body,encoding

def saveStr(string, filename):
	directory = os.path.join(*(filename.split('/')[:-1]))
	if not os.path.isfile(directory) and not os.path.isdir(directory):
		os.makedirs(directory)
	with open(filename, 'w') as F:
		F.write(string)
	

if __name__ == "__main__":
	if len(sys.argv) < 4:
		sys.exit("Usage: python %s [domain] [listUrl] [listFilename] (start page num) (end page num)")
	elif len(sys.argv) < 6:
		domain = sys.argv[1]
		url = sys.argv[2]
		filename = sys.argv[3]
		link = domain + url
		path = domain + filename
		string,encoding = fetchUrl(link)
		saveStr(string, path)
	else:
		domain = sys.argv[1]
		listUrl = sys.argv[2]
		listFilename = sys.argv[3]
		startIndex = int(sys.argv[4])
		endIndex = int(sys.argv[5])
	 	for i in range(startIndex, endIndex+1):
			link = domain + listUrl%(i)
			path = domain + listFilename%(i)
			print "fetching: %s"%link
			string,encoding = fetchUrl(link)
			saveStr(string, path)

