import datetime
import glob
import os

import dbinteractions as itsdb
from dbconstants import PROJECT_ID, PB_COMP_ID, ELEC_ACT_ID, QUAL_ACT_ID, ELEC_TESTS_FILENAME, SUMMARY_FILES_DIR
from dbwriter import addPbToDb, addElecTest, addQualTest


# retrieve existing Power Board IDs
pbIdsInDb = []
pbComponents = itsdb.ComponentRead(projectID=PROJECT_ID, componentTypeID=PB_COMP_ID).Response
if pbComponents:
    for pbComponent in pbComponents:
        pbIdsInDb.append(pbComponent.ComponentID)

# retrieve existing electrical tests
elecTestsInDb = []
elecActivities = itsdb.ActivityRead(projectID=PROJECT_ID, activityTypeID=ELEC_ACT_ID).Response
if elecActivities:
    for elecActivity in elecActivities:
        pbId = elecActivity.Name[0:7]
        elecTestsInDb.append(pbId)

# retrieve existing qualification tests as dictionary (ID: number of tests)
qualTestsInDb = {}
qualActivites = itsdb.ActivityRead(projectID=PROJECT_ID, activityTypeID=QUAL_ACT_ID).Response
if qualActivites:
    for qualActivity in qualActivites:
        pbId = qualActivity.Name[0:7]
        if qualActivity.ActivityStatus.Code == 'CLOSED':
            qualTestsInDb[pbId] = qualTestsInDb.get(pbId, 0) + 1

# loop through Electrical Test Record file
with open(ELEC_TESTS_FILENAME, 'r') as elecFile:
    for line in elecFile:
        pbId = 'PB-' + line.rstrip('\n')
        # create board in DB if it doesn't exist and add to pbIds
        if pbId not in pbIdsInDb:
            print 'add {0} and sub-components to DB'.format(pbId)
            addPbToDb(pbId)
            pbIdsInDb.append(pbId)
        # add electrical test if it doesn't exist
        if pbId not in elecTestsInDb:
            print 'add {0} electrical test to DB'.format(pbId)
            addElecTest(pbId)
            elecTestsInDb.append(pbId)

# loop through summary files
summaryfilenames = sorted(glob.glob(os.path.join(SUMMARY_FILES_DIR, 'PB-*_summary_*.txt')))
summaryFilesInDirectory = {}
for summaryfilename in summaryfilenames:
    filename = os.path.basename(summaryfilename)
    fileinfo = filename.split('_')
    pbId = fileinfo[0]
    if pbId not in elecTestsInDb:
        print '{0} has no electrical test; not adding qual test'.format(pbId)
    else:
        timestamp = str(datetime.datetime.strptime(fileinfo[2][:-4], '%Y%m%dT%H%M%S'))

        summaryFilesInDirectory[pbId] = summaryFilesInDirectory.get(pbId, 0) + 1
        # if qualification test doesn't exist
        if summaryFilesInDirectory[pbId] > qualTestsInDb.get(pbId, 0):
            print 'add {0} qual test to DB'.format(pbId)
            addQualTest(pbId, summaryfilename, timestamp)
            qualTestsInDb[pbId] = qualTestsInDb.get(pbId, 0) + 1
