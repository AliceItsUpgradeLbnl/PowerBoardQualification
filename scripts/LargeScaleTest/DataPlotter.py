#!/usr/bin/python

import PowerboardTestData as PbData
#import ROOT

def PlotPowerVoltageScanData(inputFile, PowerUnitID, load):
    vsData = PbData.VoltageScan(PowerUnitID = PowerUnitID, load = load, summary = "dummy") 
    vsData.readFile(inputFile)

    vsHasProblem = False
    plotOption = 2
    if (plotOption == 1):
        vsHasProblem = vsData.visualizeAndCheck()
    elif (plotOption == 2):
        vsHasProblem = vsData.visualizeAndCheck(showFits = True, displayData = True, saveToFile = False)

    return vsHasProblem

def PlotBiasVoltageScanData(inputFile, PowerUnitID, load):
    bvsData = PbData.BiasScan(PowerUnitID = PowerUnitID, load = load, summary = "dummy")
    bvsData.readFile(inputFile)
    bvsHasProblem = bvsData.visualizeAndCheck(displayData = True, saveToFile = False)

    return bvsHasProblem

def PlotThresholdScanData(inputFile, PowerUnitID, load):
    tsData = PbData.ThresholdScan(PowerUnitID = PowerUnitID, load = load, summary = "dummy") 
    tsData.readFile(inputFile)
    tsHasProblem = tsData.visualizeAndCheck(showFits = True, displayData = True, saveToFile = False)
 
    return tsHasProblem

