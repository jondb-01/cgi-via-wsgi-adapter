#!/usr/bin/env python

import os, sys

def test_with_cgi():
	import cgi, cgitb, os
	cgitb.enable()

	print "Content-type: text/plain\n"

	form = cgi.FieldStorage()


	print "Hello",

	sys.stderr.write("Hello world.\nnewline")
	#exit(1)

	if 'name' in form:
		print form['name'].value

	print
	print '-' * 10

	if 'headers' in form:
		for k, v in sorted(os.environ.items()):
			print "%s: %s" % (k, v)


def test_input():
	print "Content-type: text/plain\n"
	print "input-output"
	print sys.stdin.read()


def test_statuses():
	print "status: 302"
	print "Location: http://www.tooln.net/\n"


test_with_cgi()
