import datetime
import glob
import os

import dbinteractions as itsdb
from dbconstants import PROJECT_ID, PB_COMP_ID, PU_L_COMP_ID, PU_R_COMP_ID, HE_COMP_ID, ELEC_ACT_ID, QUAL_ACT_ID, OPEN_ID, CLOSED_ID, CATEGORY_ID, USER_ID, LOCATION, ELEC_TESTS_FILENAME, SUMMARY_FILES_DIR


# function to retrieve serialized file from filename
def getFile(filename):
    with open(filename, 'rb') as f:
        return f.read()


def one(iterable):
    if len(iterable) == 0:
        raise ValueError('not enough values to unpack (expected 1, got 0)')
    if len(iterable) > 1:
        raise ValueError('too many values to unpack (expected 1)')
    return iterable[0]


# function to retrieve DB ID from component ID
def getCompDbId(compId):
    allcomps = itsdb.ComponentRead(projectID=PROJECT_ID, componentTypeID=PB_COMP_ID).Response
    try:
        compDbId = one(filter(lambda c: c.ComponentID == compId, allcomps)).ID
    # allcomps is None instead of [] when empty
    except (ValueError, TypeError):
        compDbId = -1

    return compDbId


# function to add component and subcomponents to DB
def addPbToDb(pbId):
    pbDbId = itsdb.ComponentCreate(
        componentTypeID=PB_COMP_ID,
        componentID=pbId,
        supplierComponentID=pbId,
        description='',
        lotID='',
        packageID='',
        userID=USER_ID).Response.ID

    pulDbId = itsdb.ComponentCreate(
        componentTypeID=PU_L_COMP_ID,
        componentID='{0} PU-L'.format(pbId),
        supplierComponentID='{0} PU-L'.format(pbId),
        description='',
        lotID='',
        packageID='',
        userID=USER_ID).Response.ID
    itsdb.ComponentCompositionCreate(
        rootID=pbDbId,
        ID=pulDbId,
        position='',
        userID=USER_ID)

    purDbId = itsdb.ComponentCreate(
        componentTypeID=PU_R_COMP_ID,
        componentID='{0} PU-R'.format(pbId),
        supplierComponentID='{0} PU-R'.format(pbId),
        description='',
        lotID='',
        packageID='',
        userID=USER_ID).Response.ID
    itsdb.ComponentCompositionCreate(
        rootID=pbDbId,
        ID=purDbId,
        position='',
        userID=USER_ID)

    heDbId = itsdb.ComponentCreate(
        componentTypeID=HE_COMP_ID,
        componentID='{0} HE'.format(pbId),
        supplierComponentID='{0} HE'.format(pbId),
        description='',
        lotID='',
        packageID='',
        userID=USER_ID).Response.ID
    itsdb.ComponentCompositionCreate(
        rootID=pbDbId,
        ID=heDbId,
        position='',
        userID=USER_ID)


# function to add electrical test activity to DB
def addElecTest(pbId):
    timestamp = str(datetime.datetime.now())
    activity = itsdb.ActivityCreate(
        activityTypeID=ELEC_ACT_ID,
        locationID=elecLocationId,
        lotID='',
        activityName='{0} Electrical Test'.format(pbId),
        startDate=timestamp,
        endDate=timestamp,
        position='',
        resultID=elecPassId,
        statusID=OPEN_ID,
        userID=USER_ID)
    activityId = activity.Response.ID

    # associate components with activity
    for elecCompId in elecCompIds:
        itsdb.ActivityComponentAssign(
            componentID=getCompDbId(pbId),
            activityID=activityId,
            actTypeCompTypeID=elecCompId,
            userID=USER_ID)

    # close activity
    itsdb.ActivityChange(
        ID=activityId,
        activityTypeID=ELEC_ACT_ID,
        locationID=elecLocationId,
        lotID='',
        activityName='{0} Electrical Test'.format(pbId),
        startDate=timestamp,
        endDate=timestamp,
        position='',
        resultID=elecPassId,
        statusID=CLOSED_ID,
        userID=USER_ID)


# function to add qualification test activity to DB
def addQualTest(pbId, summaryfilename, timestamp):
    # add qualification test
    activity = itsdb.ActivityCreate(
        activityTypeID=QUAL_ACT_ID,
        locationID=qualLocationId,
        lotID='',
        activityName='{0} Qualification Test'.format(pbId),
        startDate=timestamp,
        endDate=timestamp,
        position='',
        resultID=qualPassId,
        statusID=OPEN_ID,
        userID=USER_ID)
    activityId = activity.Response.ID

    # upload summary file
    filename = os.path.basename(summaryfilename)
    itsdb.ActivityAttachmentCreate(
        activityID=activityId,
        attachmentCategoryID=CATEGORY_ID,
        file=getFile(summaryfilename),
        fileName=filename,
        userID=USER_ID)

    # associate components with activity
    for qualCompId in qualCompIds:
        itsdb.ActivityComponentAssign(
            componentID=getCompDbId(pbId),
            activityID=activityId,
            actTypeCompTypeID=qualCompId,
            userID=USER_ID)

    # close activity
    itsdb.ActivityChange(
        ID=activityId,
        activityTypeID=QUAL_ACT_ID,
        locationID=qualLocationId,
        lotID='',
        activityName='{0} Qualification Test'.format(pbId),
        startDate=timestamp,
        endDate=timestamp,
        position='',
        resultID=qualPassId,
        statusID=CLOSED_ID,
        userID=USER_ID)

    qualTestsInDb[pbId] = qualTestsInDb.get(pbId, 0) + 1


# set up some IDs from database
elecActType = itsdb.ActivityTypeReadAll(activityTypeID=ELEC_ACT_ID).Response
elecPassId = one(filter(lambda r: r.Name == 'PASSED', elecActType.Result.ActivityTypeResultFull)).ID
elecLocationId = one(filter(lambda l: l.Name == LOCATION, elecActType.Location.ActivityTypeLocation)).ID
elecCompIds = [c.ID for c in elecActType.ActivityTypeComponentType.ActivityTypeComponentTypeFull]

qualActType = itsdb.ActivityTypeReadAll(activityTypeID=QUAL_ACT_ID).Response
qualPassId = one(filter(lambda r: r.Name == 'PASSED', qualActType.Result.ActivityTypeResultFull)).ID
qualLocationId = one(filter(lambda l: l.Name == LOCATION, qualActType.Location.ActivityTypeLocation)).ID
qualCompIds = [c.ID for c in qualActType.ActivityTypeComponentType.ActivityTypeComponentTypeFull]

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
        qualTestsInDb[pbId] = qualTestsInDb.get(pbId, 0) + 1

with open(ELEC_TESTS_FILENAME, 'r') as elecFile:
    # loop through Electrical Test Record file
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
