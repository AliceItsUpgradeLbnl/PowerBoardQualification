#!/usr/bin/python

import os
import sys
import subprocess

resultsFolder = "RESULTS/"
powerUnitIds = ["Right", "Left"]

def CheckFiles(boardId, loadType):
    testFilesExist = True 
    listOfTestTypes = GetListOfTestTypes(loadType)
    for powerUnitId in powerUnitIds:
        testFilesExist = testFilesExist and CheckPowerUnitFiles(boardId, powerUnitId, loadType, listOfTestTypes)

    return testFilesExist

def DeleteBoardFiles(boardId):
    listOfTxtFilesInResultsDir = GetTxtFiles()
    listOfBoardidFiles = GetBoardIdFiles(listOfTxtFilesInResultsDir, boardId)
    listOfFilesToDelete = [(x + ".txt") for x in listOfBoardidFiles]
    for fileToDelete in listOfFilesToDelete:
        subprocess.call(["/bin/bash", "-c", "rm -f " + resultsFolder + fileToDelete])

def GetListOfTestTypes(loadType):
    if loadType == 'Low':
        return ["TemperatureScan", "LatchupTest", "BiasVoltageScan", "PowerVoltageScan", "ThresholdScan"]
    elif loadType == 'Nominal' or loadType == 'High':
        return ["BiasVoltageScan", "PowerVoltageScan", "ThresholdScan"]

    print "Wrong load type provided to check files"
    sys.exit()

def CheckPowerUnitFiles(boardId, powerUnitId, loadType, listOfTestTypes):
    listOfTxtFiles = GetTxtFiles()
    listOfBoardIdMatchingFiles = GetBoardIdFiles(listOfTxtFiles, boardId)
    searchList     = GetLoadTypeFiles(listOfBoardIdMatchingFiles, loadType)
    listOfPowerUnitMatchingFiles = GetPowerUnitFiles(searchList, powerUnitId)
    for x in listOfTestTypes:
        if not len(GetTestTypeFiles(listOfPowerUnitMatchingFiles, x)):
            return False

    return True

def GetResultFiles():
    return os.listdir(resultsFolder) 

def GetTxtFiles():
    listOfFilesInResultsDir = GetResultFiles()
    return [x.split(".")[0] for x in listOfFilesInResultsDir if x.split(".")[-1] == "txt"]

def GetBoardIdFiles(listOfFiles, boardId):
    return [x for x in listOfFiles if (x.split("_")[1] == "BoardID" + str(boardId))]

def GetPowerUnitFiles(listOfFiles, powerUnitId):
    if powerUnitId == None:
        return listOfFiles
    return [x for x in listOfFiles if x.split("_")[2] == ("PowerUnit" + powerUnitId)]

def GetLoadTypeFiles(listOfFiles, loadType):
    if loadType == None:
        return listOfFiles
    return [x for x in listOfFiles if x.split("_")[3] == ("LoadType" + loadType)]

def GetTestTypeFiles(listOfFiles, testType):
    if testType == None:
        return listOfFiles
    return [x for x in listOfFiles if x.split("_")[5] == testType]

def GetMatchingFiles(boardId, powerUnitId = None, loadType = None, testType = None):
    listOfTxtFiles = GetTxtfiles()
    return GetTestTypeFiles(GetLoadTypeFiles(GetPowerUnitFiles(GetBoardIdFiles(listOfTxtFiles, boardId), powerUnitId), loadType), testType)
