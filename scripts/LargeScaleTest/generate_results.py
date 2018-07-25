#!/usr/bin/python

import subprocess

testTypes = {"Low": ["PreliminaryCheck", "TemperatureScan", "I2CTest", "LatchupTest", "BiasVoltageScan", "PowerVoltageScan", "ThresholdScan"], "Nominal": ["PreliminaryCheck", "BiasVoltageScan", "PowerVoltageScan", "ThresholdScan"], "High": ["PreliminaryCheck", "BiasVoltageScan", "PowerVoltageScan", "ThresholdScan"]}

def GenerateFiles():
    timestamp = "20180707T134545"
    boardId   = "45"
    config    = "7"
    tester    = "Fernando"

    powerUnitIds = ["Right", "Left"]
    loadTypes    = ["Low", "Nominal", "High"]
    for powerUnitId in powerUnitIds:
        for loadType in loadTypes:
            for testType in testTypes[loadType]:
                filename = BuildFilename(timestamp, boardId, powerUnitId, loadType, config, testType, tester)
                subprocess.call(["/bin/bash", "-c", "touch %s" %(filename)])

def BuildFilename(timestamp, boardId, powerUnitId, loadType, config, testType, tester):
    filename = "../RESULTS/%s_BoardID%s_PowerUnit%s_LoadType%s_Config%s_%s_%s.txt" %(timestamp, boardId, powerUnitId, loadType, config, testType, tester)
    return filename
