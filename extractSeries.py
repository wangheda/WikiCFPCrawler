#!/bin/python

import sys
import os
from bs4 import BeautifulSoup as Soup
from extractData import toUTF8
import re
import json

eventRegex = re.compile("eventid=(?P<eventid>\d+)")

def getTitle(StringSoup):
	title = StringSoup.select("h2")
	if title:
		title = title[0].string.strip()
		return title
	else:
		sys.exit("getTitle: error")

def getConfIDs(StringSoup):
	section = StringSoup.select("div.contsec")
	if section:
		section = section[0]
		links = section.select('a[href^="/cfp/servlet/event.showcfp?eventid="]')
		if links:
			confIDs = []
			for link in links:
				name = link.string
				eventid = eventRegex.search(link["href"]).group("eventid")
				confIDs.append((eventid,name))
			return confIDs
	return None

if __name__=="__main__":
	numberRegex = re.compile("^\d+$")
	cleanedSeriesLines = []
	cleanedSeriesFile = open("cleaned/series.tsv", "w")
	for item in os.listdir("www.wikicfp.com/cfp/program"):
		if numberRegex.match(item):
			itemID = int(item)
			print itemID
			filecontent = open("www.wikicfp.com/cfp/program/%d"%itemID).read()
			soup = Soup(filecontent)
			itemTitle = getTitle(soup)
			confIDs = getConfIDs(soup)
			if confIDs and itemTitle:
				for confID, confName in confIDs:
					confID = int(confID)
					seriesString = "%d\t%d\t%s\t%s\n"%(confID, itemID, confName, itemTitle)
					cleanedSeriesLines.append(toUTF8(seriesString))
	cleanedSeriesFile.writelines(cleanedSeriesLines)
	cleanedSeriesFile.close()


				
