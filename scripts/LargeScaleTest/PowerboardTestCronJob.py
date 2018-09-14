#!/usr/bin/env python

import os
from datetime import date, timedelta, datetime
from PowerboardTestDB import fillDBFromFiles, fillConfig
from stat import S_IREAD, S_IRGRP, S_IROTH

# set this to false to stop running the job
runJob = True
daysPast = 1
datadirectory = "/home/its/Desktop/PB-production/PB_production/scripts/RESULTS/"
configdirectory = "/home/its/Desktop/PB-production/PB_production/scripts/LargeScaleTest/ScanConfig/"

if runJob:
	# find yesterday's date and format it correctly
	yesterdate = date.today() - timedelta(daysPast)
	yesterday = yesterdate.strftime("%Y%m%d")

	# look for files starting with yesterday's date
	newFiles = []
	for filename in os.listdir(datadirectory):
		if filename.startswith(yesterday):
			newFiles.append(filename)

	# group files by timestamp
	testGroups = {}
	for filename in newFiles:
		# get the timestamp
		timestamp = filename.split("_")[0]
		# use it as the key in the dictionary of filenames
		# initialize the array if it doesn't already exist
		if timestamp not in testGroups:
			testGroups[timestamp] = []
		# add this file to the appropriate group
		testGroups[timestamp].append(filename)

	# save each test group to the database in order of timestamp
	for timestamp in sorted(testGroups):
		fillDBFromFiles(testGroups[timestamp], datadirectory)

	print datetime.today(), "Files:", len(newFiles), "Groups: ", len(testGroups)


	# look for config files created in the last 24 hours
	cutoff = datetime.now() - timedelta(daysPast)
	newConfigs = []
	for filename in os.listdir(configdirectory):
		if filename.endswith('~'):
			continue
		lastModified = datetime.fromtimestamp(os.stat(configdirectory + filename).st_mtime)
		if lastModified > cutoff:
			# strip off 'config'
			configId = filename[6:]
			with open(configdirectory + filename) as f:
				result = f.read()
				fillConfig(configId, result)
				newConfigs.append(configId)
				os.chmod(configdirectory + filename, S_IREAD|S_IRGRP|S_IROTH)
	if len(newConfigs) > 0:
		print datetime.today(), "Configs:", ", ".join(newConfigs)
