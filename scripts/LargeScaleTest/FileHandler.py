#!/usr/bin/python

import os
import sys
import subprocess

resultsFolder = "RESULTS/"
powerUnitIds = ["Right", "Left"]

def CheckDataFiles(boardId, loadType):
    testFilesExist = True 
    listOfTestTypes = GetListOfTestTypes(loadType)
    for powerUnitId in powerUnitIds:
        testFilesExist = testFilesExist and CheckPowerUnitFiles(boardId, powerUnitId, loadType, listOfTestTypes)

    return testFilesExist

def CheckSummaryFile(boardId):
    listOfTxtFiles = GetTxtFiles()
    listOfBoardIdFiles = GetBoardIdFiles(listOfTxtFiles, boardId)
    listOfSummaryFiles = [x for x in listOfBoardIdFiles if x.split("_")[1] == "summary"]
    if len(listOfSummaryFiles) != 1:
        return False
    
    return True 

def DeleteBoardFiles(boardId):
    DeleteBoardTxtFiles(boardId)
    DeleteBoardDatFiles(boardId)

def DeleteBoardTxtFiles(boardId):
    listOfTxtFilesInResultsDir = GetTxtFiles()
    listOfBoardidFiles = GetBoardIdFiles(listOfTxtFilesInResultsDir, boardId)
    listOfFilesToDelete = [(x + ".txt") for x in listOfBoardidFiles]
    for fileToDelete in listOfFilesToDelete:
        subprocess.call(["/bin/bash", "-c", "rm -f " + resultsFolder + fileToDelete])

def DeleteBoardDatFiles(boardId):
    listOfDatFilesInResultsDir = GetDatFiles()
    listOfBoardidFiles = GetBoardIdFiles(listOfDatFilesInResultsDir, boardId)
    listOfFilesToDelete = [(x + ".dat") for x in listOfBoardidFiles]
    for fileToDelete in listOfFilesToDelete:
        subprocess.call(["/bin/bash", "-c", "rm -f " + resultsFolder + fileToDelete])

def GetListOfTestTypes(loadType):
    if loadType == 'Low':
        return ["TemperatureTest", "LatchTest", "BiasScan", "VoltageScan", "ThresholdScan"]
    elif loadType == 'Nominal' or loadType == 'High':
        return ["BiasScan", "VoltageScan", "ThresholdScan"]

    print "Wrong load type provided to check files"
    sys.exit()

def CheckPowerUnitFiles(boardId, powerUnitId, loadType, listOfTestTypes):
    listOfDatFiles = GetDatFiles()
    listOfBoardIdMatchingFiles = GetBoardIdFiles(listOfDatFiles, boardId)
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

def GetDatFiles():
    listOfFilesInResultsDir = GetResultFiles()
    return [x.split(".")[0] for x in listOfFilesInResultsDir if x.split(".")[-1] == "dat"]

def GetBoardIdFiles(listOfFiles, boardId):
    if boardId == None:
        return listOfFiles
    return [x for x in listOfFiles if x.split("_")[0] == ("PB-%04d" % boardId)]

def GetPowerUnitFiles(listOfFiles, powerUnitId):
    if powerUnitId == None:
        return listOfFiles
    return [x for x in listOfFiles if x.split("_")[1] == ("PU-" + powerUnitId)]

def GetLoadTypeFiles(listOfFiles, loadType):
    if loadType == None:
        return listOfFiles
    return [x for x in listOfFiles if x.split("_")[2] == ("Load-" + loadType)]

def GetTestTypeFiles(listOfFiles, testType):
    if testType == None:
        return listOfFiles
    return [x for x in listOfFiles if x.split("_")[3] == testType]

def GetMatchingFiles(boardId, powerUnitId = None, loadType = None, testType = None):
    listOfDatFiles = GetDatfiles()
    return GetTestTypeFiles(GetLoadTypeFiles(GetPowerUnitFiles(GetBoardIdFiles(listOfDatFiles, boardId), powerUnitId), loadType), testType)
