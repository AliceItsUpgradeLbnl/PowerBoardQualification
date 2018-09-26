#!/usr/bin/python

import subprocess

testTypes = {"Low": ["TemperatureTest", "LatchTest", "BiasScan", "VoltageScan", "ThresholdScan"], "Nominal": ["BiasScan", "VoltageScan", "ThresholdScan"], "High": ["BiasScan", "VoltageScan", "ThresholdScan"]}

def GenerateFiles():
    timestamp = "20180707T134545"
    boardId   = "0045"

    powerUnitIds = ["Right", "Left"]
    loadTypes    = ["Low", "Nominal", "High"]
    for powerUnitId in powerUnitIds:
        for loadType in loadTypes:
            for testType in testTypes[loadType]:
                filename = BuildFilename(boardId, powerUnitId, loadType, testType, timestamp)
                subprocess.call(["/bin/bash", "-c", "touch %s" %(filename)])

    summaryFile = "../RESULTS/PB-" + boardId + "_summary_" + timestamp + ".txt"
    subprocess.call(["/bin/bash", "-c", "touch %s" %(summaryFile)])
    

def BuildFilename(boardId, powerUnitId, loadType, testType, timestamp):
    filename = "../RESULTS/PB-%s_PU-%s_Load-%s_%s_%s.dat" %(boardId, powerUnitId, loadType, testType, timestamp)
    return filename

GenerateFiles()
