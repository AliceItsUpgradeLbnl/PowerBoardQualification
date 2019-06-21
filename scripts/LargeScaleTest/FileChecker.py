#!/usr/bin/python

import os
import sys
import subprocess

resultsFolder = "../RESULTS/"
powerUnitIds = ["Right", "Left"]
fileLengths = {"summary": 225, "TemperatureTest": 8, "LatchTest": 29, "BiasScan": 15, "VoltageScan": 417, "ThresholdScan": 97, "BiasCalibration": 15, "VoltageCalibration": 417}

def CheckBoardIdsFilesComplete(boardIdList):
    allComplete = True
    for boardId in boardIdList:
        thisBoardComplete = CheckBoardIdFilesComplete(boardId)
        allComplete = allComplete and thisBoardComplete
    return allComplete

def CheckBoardIdFilesComplete(boardId):
    if not CheckSummaryFile(boardId):
        return False    
    for load in ["Low", "Nominal", "High"]:
        if not CheckDataFiles(boardId, load):
            return False
    return True

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
    # Check that at least one and only one summary file exists for the entered power board id
    if len(listOfSummaryFiles) != 1:
        return False
    # Check that the length of the summary file for the entered power board id is of the right length
    if GetLengthOfFileInLines(resultsFolder + listOfSummaryFiles[0] + ".txt") != fileLengths["summary"]:
        return False
     
    return True 

def DeleteBoardFiles(boardId):
    DeleteBoardTxtFiles(boardId)
    DeleteBoardDatFiles(boardId)

def DeleteLoadFiles(boardId, load):
    if load == "High":
        DeleteBoardTxtFiles(boardId)
    DeleteBoardLoadDatFiles(boardId, load)
    

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

def DeleteBoardLoadDatFiles(boardId, load):
    listOfDatFilesInResultsDir = GetDatFiles()
    listOfBoardidFiles = GetBoardIdFiles(listOfDatFilesInResultsDir, boardId)
    listOfLoadFiles    = GetLoadTypeFiles(listOfBoardidFiles, load)
    listOfFilesToDelete = [(x + ".dat") for x in listOfLoadFiles]
    for fileToDelete in listOfFilesToDelete:
        subprocess.call(["/bin/bash", "-c", "rm -f " + resultsFolder + fileToDelete])

def GetLengthOfFileInLines(filename):
    return sum(1 for line in open(filename))

def GetListOfTestTypes(loadType):
    if loadType == 'Low':
        return ["TemperatureTest", "LatchTest", "BiasScan", "VoltageScan", "ThresholdScan"]
    elif loadType == 'High':
        return ["BiasScan", "VoltageScan", "ThresholdScan", "VoltageCalibration", "BiasCalibration"]
    elif loadType == 'Nominal':
        return ["BiasScan", "VoltageScan", "ThresholdScan"]

    print "Wrong load type provided to check files"
    sys.exit()

def CheckPowerUnitFiles(boardId, powerUnitId, loadType, listOfTestTypes):
    listOfDatFiles = GetDatFiles()
    listOfBoardIdMatchingFiles = GetBoardIdFiles(listOfDatFiles, boardId)
    searchList     = GetLoadTypeFiles(listOfBoardIdMatchingFiles, loadType)
    listOfPowerUnitMatchingFiles = GetPowerUnitFiles(searchList, powerUnitId)
    if len(listOfPowerUnitMatchingFiles) != len(listOfTestTypes):
        return False
    for x in listOfTestTypes:
        testFiles = GetTestTypeFiles(listOfPowerUnitMatchingFiles, x)
        # Checking that only one test file of this type exists
        if len(testFiles) != 1:
            return False
        # Check that this type of test file is of the reight length
        if (x != "TemperatureTest"):
            if GetLengthOfFileInLines(resultsFolder + testFiles[0] + ".dat") != fileLengths[x]:
                return False
        else:
            if GetLengthOfFileInLines(resultsFolder + testFiles[0] + ".dat") < fileLengths[x]:
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
