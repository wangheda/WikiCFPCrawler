#!/bin/python

import sys
import os
from bs4 import BeautifulSoup as Soup
import re
import json
from datetime import datetime

ownerRegex = re.compile("ownerid=(?P<userid>\d+)")
replaceRegex = []
with open("replace.txt") as F:
	for line in F:
		replaceRegex.append(re.compile(line.strip()))

def getInfoDict():
	itemInfoDict = {}
	seriesInfoDict = {}
	with open("cleaned/series.tsv") as F:
		for line in F:
			confID, seriesID, confName, SeriesName = line.strip().split("\t")
			itemInfoDict[int(confID)] = (int(seriesID), confName)
			seriesInfoDict[int(seriesID)] = SeriesName
	return itemInfoDict, seriesInfoDict

def getBrief(string):
	modified = True
	while modified:
		modified = False
		for regex in replaceRegex:
			string = string.strip()
			string2 = regex.sub("", string)
			if string != string2:
				modified = True
				string = string2
	return string

def getMetaData(StringSoup):
	data = StringSoup.select('span[typeof="v:Event"]')
	meta = {}
	if data:
		data = data[0]
		for span in data.select('span[property^="v:"]'):
			key = span["property"]
			value = span.get("content")
			if not value:
				value = span.string
			meta[key.strip()] = value.strip()
	box = StringSoup.select('table.gglu')
	if box:
		box = box[0]
		for tr in box.select('tr'):
			tr_head = tr.th.string
			tr_data = tr.td
			tr_event = tr_data.select('span[typeof="v:Event"]')
			if tr_event:
				tr_event = tr_event[0].select('span[property="v:startDate"]')
				if tr_event:
					tr_data = tr_event[0].get("content")
				else:
					tr_data = " "
			else:
				tr_data = tr_data.string
			meta[tr_head.strip()] = tr_data.strip()
	return meta

def getUserIDs(StringSoup):
	data = StringSoup.select('span#more_users a[href*="ownerid"]')
	userIDs = []
	for item in data:
		href = item["href"]
		owner = ownerRegex.search(href).group("userid")
		userIDs.append(int(owner))
	return userIDs

def getPosterID(itemID, StringSoup):
	data = StringSoup.select('span#more_users')
	userID = None
	if data:
		data = data[0]
		for item in data.previous_siblings:
			if item.name == u'a':
				if item["href"].startswith("/cfp/servlet/event.showlist?lownerid="):
					href = item["href"]
					owner = ownerRegex.search(href).group("userid")
					userID = int(owner)
	# print itemID, userID
	return userID

def getSeriesName(metaData):
	summary = metaData.get("v:summary")
	seriesName = getBrief(summary)
	if len(seriesName):
		return seriesName
	else:
		return None

def getConfName(metaData):
	confName = metaData.get("v:summary").strip()
	return confName


def getTimestamp(metaData):
	deadline = metaData.get("Submission Deadline")
	if deadline.strip() != "TBD":
		dt = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S")
		timestamp = (dt - datetime(1970,1,1)).total_seconds()
		return timestamp
	else:
		if metaData.has_key("v:startDate"):
			startDate = metaData.get("v:startDate")
			dt = datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S")
			timestamp = (dt - datetime(1970,1,1)).total_seconds()
			timestamp = timestamp - 3600*24*30*5 # 5 months before startDate 
			return timestamp
		else:
			return None

def toUTF8(string):
	if type(string) == str:
		return string
	elif type(string) == unicode:
		return string.encode("utf8")
	else:
		print type(string)
		sys.exit(1)

if __name__=="__main__":
	metaFile = open("origin/meta.txt", "w")
	metaLines = []
	relationFile = open("origin/tracked.txt", "w")
	relationLines = []
	postFile = open("origin/posted.txt", "w")
	postLines = []
	cleanedMetaFile = open("cleaned/meta.txt", "w")
	cleanedMetaLines = []
	cleanedItemFile = open("cleaned/item.txt", "w")
	cleanedItemLines = []
	cleanedRelationFile = open("cleaned/tracked.txt", "w")
	cleanedRelationLines = []
	cleanedPostFile = open("cleaned/posted.txt", "w")
	cleanedPostLines = []
	cleanedSeriesFile = open("cleaned/series.txt", "w")
	cleanedSeriesLines = []

	numberRegex = re.compile("^\d+$")

	metaDict = {}
	postDict = {}
	relationDict = {}
	seriesDict = {}

	additionalSeriesNumber = 100000
	itemInfoDict, seriesInfoDict = getInfoDict()

	count = 0
	for item in os.listdir("www.wikicfp.com/cfp/event"):
		count += 1
		print count
		if numberRegex.match(item):
			itemID = int(item)
			filecontent = open("www.wikicfp.com/cfp/event/%d"%itemID).read()
			soup = Soup(filecontent)
			metaData = getMetaData(soup)
			userIDs = getUserIDs(soup)
			metaDict[itemID] = metaData
			relationDict[itemID] = userIDs
			if metaData:
				metaData["itemID"] = itemID
				if userIDs:
					metaLines.append(json.dumps(metaData)+"\n")
					for userID in userIDs:
						relationLines.append("%d\t%d\t1\n"%(userID, itemID))
				ownerID = getPosterID(itemID, soup)
				if ownerID:
					postDict[itemID] = ownerID
					postLines.append("%d\t%d\t2\n"%(ownerID, itemID))
				# cleaned data
				seriesName = getSeriesName(metaData)
				timestamp = getTimestamp(metaData)
				if timestamp:
					if userIDs:
						cleanedMetaLines.append(json.dumps(metaData)+"\n")
						for userID in userIDs:
							cleanedRelationLines.append("%d\t%d\t1\n"%(userID, itemID))
					if ownerID:
						cleanedPostLines.append("%d\t%d\t2\n"%(ownerID, itemID))
					seriesNum = -1
					confName = ""
					if itemInfoDict.has_key(itemID):
						seriesNum, confName = itemInfoDict[itemID]
						seriesName = seriesInfoDict[seriesNum]
					else:
						confName = getConfName(metaData)
						if not seriesDict.has_key(seriesName):
							seriesNum = additionalSeriesNumber
							additionalSeriesNumber += 1
							seriesDict[seriesName] = seriesNum
							seriesInfoDict[seriesNum] = seriesName
						else:
						 	seriesNum = seriesDict[seriesName]
					cleanedItemString = "%d\t%d\t%d\t%s\n"%(itemID,seriesNum,timestamp,confName)
					cleanedItemLines.append(toUTF8(cleanedItemString))

	seriesIDList = list(seriesInfoDict.keys())
	seriesIDList.sort()
	for seriesID in seriesIDList:
		seriesString = "%d\t%s\n"%(seriesID,seriesInfoDict.get(seriesID))
		cleanedSeriesLines.append(toUTF8(seriesString))

	metaFile.writelines(metaLines)
	relationFile.writelines(relationLines)
	postFile.writelines(postLines)
	cleanedMetaFile.writelines(cleanedMetaLines)
	cleanedItemFile.writelines(cleanedItemLines)
	cleanedRelationFile.writelines(cleanedRelationLines)
	cleanedPostFile.writelines(cleanedPostLines)
	cleanedSeriesFile.writelines(cleanedSeriesLines)

	metaFile.close()
	relationFile.close()
	postFile.close()
	cleanedMetaFile.close()
	cleanedItemFile.close()
	cleanedRelationFile.close()
