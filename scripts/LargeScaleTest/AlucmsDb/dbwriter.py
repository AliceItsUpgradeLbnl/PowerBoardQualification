import datetime
import os
import sqlite3 as lite

import dbinteractions as itsdb
from dbconstants import PROJECT_ID, PB_COMP_ID, PU_L_COMP_ID, PU_R_COMP_ID, HE_COMP_ID, ELEC_ACT_ID, QUAL_ACT_ID, OPEN_ID, CLOSED_ID, CATEGORY_ID, USER_ID, LOCATION, STAGING_DB


# retrieve serialized file from filename
def getFile(filename):
    with open(filename, 'rb') as f:
        return f.read()


# return the single item of an iterable
def one(iterable):
    if len(iterable) == 0:
        raise ValueError('not enough values to unpack (expected 1, got 0)')
    if len(iterable) > 1:
        raise ValueError('too many values to unpack (expected 1)')
    return iterable[0]


# retrieve DB ID from component ID for PB
def getCompDbId(compId):
    allcomps = itsdb.ComponentRead(projectID=PROJECT_ID, componentTypeID=PB_COMP_ID).Response
    try:
        compDbId = one(filter(lambda c: c.ComponentID == compId, allcomps)).ID
    # allcomps is None instead of [] when empty
    except (ValueError, TypeError):
        compDbId = -1

    return compDbId


# set up some IDs from database
elecActType = itsdb.ActivityTypeReadAll(activityTypeID=ELEC_ACT_ID).Response
elecPassId = one(filter(lambda r: r.Name == 'PASSED', elecActType.Result.ActivityTypeResultFull)).ID
elecLocationId = one(filter(lambda l: l.Name == LOCATION, elecActType.Location.ActivityTypeLocation)).ID
elecCompIds = [c.ID for c in elecActType.ActivityTypeComponentType.ActivityTypeComponentTypeFull]

qualActType = itsdb.ActivityTypeReadAll(activityTypeID=QUAL_ACT_ID).Response
qualPassId = one(filter(lambda r: r.Name == 'PASSED', qualActType.Result.ActivityTypeResultFull)).ID
qualLocationId = one(filter(lambda l: l.Name == LOCATION, qualActType.Location.ActivityTypeLocation)).ID
qualCompIds = [c.ID for c in qualActType.ActivityTypeComponentType.ActivityTypeComponentTypeFull]


# check SQL database to see if this step has already been done
def isStepComplete(con, tableName, names, values):
    condition = ' AND '.join(['{0}=?'.format(name) for name in names])
    command = 'SELECT * FROM {0} WHERE {1}'.format(tableName, condition)
    return con.execute(command, tuple(values)).fetchone() is not None


# function to add component and subcomponents to DB
def addPbToDb(pbId):
    con = lite.connect(STAGING_DB)
    if not isStepComplete(con, 'Component', ['ComponentTypeId', 'ComponentId'], [PB_COMP_ID, pbId]):
        pbDbId = itsdb.ComponentCreate(
            componentTypeID=PB_COMP_ID,
            componentID=pbId,
            supplierComponentID=pbId,
            description='',
            lotID='',
            packageID='',
            userID=USER_ID).Response.ID
        con.execute('INSERT INTO Component VALUES(?,?)', (PB_COMP_ID, pbId))
        con.commit()

    pulId = '{0} PU-L'.format(pbId)
    if not isStepComplete(con, 'Component', ['ComponentTypeId', 'ComponentId'], [PU_L_COMP_ID, pulId]):
        pulDbId = itsdb.ComponentCreate(
            componentTypeID=PU_L_COMP_ID,
            componentID=pulId,
            supplierComponentID=pulId,
            description='',
            lotID='',
            packageID='',
            userID=USER_ID).Response.ID
        con.execute('INSERT INTO Component VALUES(?,?)', (PU_L_COMP_ID, pulId))
        con.commit()

    if not isStepComplete(con, 'Composition', ['ParentId', 'ChildId'], [pbDbId, pulDbId]):
        itsdb.ComponentCompositionCreate(
            rootID=pbDbId,
            ID=pulDbId,
            position='',
            userID=USER_ID)
        con.execute('INSERT INTO Composition VALUES(?,?)', [pbDbId, pulDbId])
        con.commit()

    purId = '{0} PU-R'.format(pbId)
    if not isStepComplete(con, 'Component', ['ComponentTypeId', 'ComponentId'], [PU_R_COMP_ID, purId]):
        purDbId = itsdb.ComponentCreate(
            componentTypeID=PU_R_COMP_ID,
            componentID=purId,
            supplierComponentID=purId,
            description='',
            lotID='',
            packageID='',
            userID=USER_ID).Response.ID
        con.execute('INSERT INTO Component VALUES(?,?)', (PU_R_COMP_ID, purId))
        con.commit()

    if not isStepComplete(con, 'Composition', ['ParentId', 'ChildId'], [pbDbId, purDbId]):
        itsdb.ComponentCompositionCreate(
            rootID=pbDbId,
            ID=purDbId,
            position='',
            userID=USER_ID)
        con.execute('INSERT INTO Composition VALUES(?,?)', [pbDbId, purDbId])
        con.commit()

    heId = '{0} HE'.format(pbId)
    if not isStepComplete(con, 'Component', ['ComponentTypeId', 'ComponentId'], [HE_COMP_ID, heId]):
        heDbId = itsdb.ComponentCreate(
            componentTypeID=HE_COMP_ID,
            componentID=heId,
            supplierComponentID=heId,
            description='',
            lotID='',
            packageID='',
            userID=USER_ID).Response.ID
        con.execute('INSERT INTO Component VALUES(?,?)', (HE_COMP_ID, heId))
        con.commit()

    if not isStepComplete(con, 'Composition', ['ParentId', 'ChildId'], [pbDbId, heDbId]):
        itsdb.ComponentCompositionCreate(
            rootID=pbDbId,
            ID=heDbId,
            position='',
            userID=USER_ID)
        con.execute('INSERT INTO Composition VALUES(?,?)', [pbDbId, pulDbId])
        con.commit()

    con.close()


# function to add electrical test activity to DB
def addElecTest(pbId):
    timestamp = str(datetime.datetime.now())
    con = lite.connect(STAGING_DB)

    activityName = '{0} Electrical Test'.format(pbId)

    row = con.execute('SELECT ActivityId FROM Activity WHERE ActivityName=?', (activityName,)).fetchone()
    if row:
        activityId = row[0]
    else:
        activity = itsdb.ActivityCreate(
            activityTypeID=ELEC_ACT_ID,
            locationID=elecLocationId,
            lotID='',
            activityName=activityName,
            startDate=timestamp,
            endDate=timestamp,
            position='',
            resultID=elecPassId,
            statusID=OPEN_ID,
            userID=USER_ID)
        activityId = activity.Response.ID
        con.execute('INSERT INTO Activity VALUES(?,?,?,?)', (activityId, activityName, '', 'OPEN'))
        con.commit()

    # associate components with activity
    compDbId = getCompDbId(pbId)
    for elecCompId in elecCompIds:
        if not isStepComplete(con, 'ActivityComponent', ['ActivityId', 'ComponentDbId', 'ActComptypeId'], [activityId, compDbId, elecCompId]):
            itsdb.ActivityComponentAssign(
                componentID=compDbId,
                activityID=activityId,
                actTypeCompTypeID=elecCompId,
                userID=USER_ID)
            con.execute('INSERT INTO ActivityComponent VALUES(?,?,?)', (activityId, compDbId, elecCompId))
            con.commit()

    # close activity
    itsdb.ActivityChange(
        ID=activityId,
        activityTypeID=ELEC_ACT_ID,
        locationID=elecLocationId,
        lotID='',
        activityName=activityName,
        startDate=timestamp,
        endDate=timestamp,
        position='',
        resultID=elecPassId,
        statusID=CLOSED_ID,
        userID=USER_ID)
    con.execute('UPDATE Activity SET Status=? WHERE ActivityId=?', ('CLOSED', activityId))
    con.commit()

    con.close()


# function to add qualification test activity to DB
def addQualTest(pbId, summaryfilename, timestamp):
    con = lite.connect(STAGING_DB)

    activityName = '{0} Qualification Test'.format(pbId)

    row = con.execute('SELECT ActivityId FROM Activity WHERE Filename=? AND ActivityName=?', (summaryfilename, activityName)).fetchone()
    if row:
        activityId = row[0]
    else:
        activity = itsdb.ActivityCreate(
            activityTypeID=QUAL_ACT_ID,
            locationID=qualLocationId,
            lotID='',
            activityName=activityName,
            startDate=timestamp,
            endDate=timestamp,
            position='',
            resultID=qualPassId,
            statusID=OPEN_ID,
            userID=USER_ID)
        activityId = activity.Response.ID
        con.execute('INSERT INTO Activity VALUES(?,?,?,?)', (activityId, activityName, summaryfilename, 'OPEN'))
        con.commit()

    # upload summary file
    filename = os.path.basename(summaryfilename)
    if not isStepComplete(con, 'ActivityAttachment', ['ActivityId', 'Filename'], [activityId, filename]):
        itsdb.ActivityAttachmentCreate(
            activityID=activityId,
            attachmentCategoryID=CATEGORY_ID,
            file=getFile(summaryfilename),
            fileName=filename,
            userID=USER_ID)
        con.execute('INSERT INTO ActivityAttachment VALUES(?,?)', (activityId, filename))
        con.commit()

    # associate components with activity
    compDbId = getCompDbId(pbId)
    for qualCompId in qualCompIds:
        if not isStepComplete(con, 'ActivityComponent', ['ActivityId', 'ComponentDbId', 'ActCompTypeId'], [activityId, compDbId, qualCompId]):
            itsdb.ActivityComponentAssign(
                componentID=compDbId,
                activityID=activityId,
                actTypeCompTypeID=qualCompId,
                userID=USER_ID)
            con.execute('INSERT INTO ActivityComponent VALUES(?,?,?)', (activityId, compDbId, qualCompId))
            con.commit()

    # close activity
    itsdb.ActivityChange(
        ID=activityId,
        activityTypeID=QUAL_ACT_ID,
        locationID=qualLocationId,
        lotID='',
        activityName=activityName,
        startDate=timestamp,
        endDate=timestamp,
        position='',
        resultID=qualPassId,
        statusID=CLOSED_ID,
        userID=USER_ID)
    con.execute('UPDATE Activity SET Status=? WHERE ActivityId=?', ('CLOSED', activityId))
    con.commit()

    con.close()
