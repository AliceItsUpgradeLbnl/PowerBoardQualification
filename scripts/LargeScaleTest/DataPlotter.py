#!/usr/bin/python

import PowerboardTestData as PbData
import ROOT

def PlotPowerVoltageScanData(inputFile):
    vsData = PbData.VoltageScan() 
    vsData.readFile(inputFile)

    vsHasProblem = False
    plotOption = 2
    if (plotOption == 1):
        vsHasProblem = vsData.visualizeAndCheck()
    elif (plotOption == 2):
        vsHasProblem = vsData.visualizeAndCheck(True, True)

    return vsHasProblem

def PlotBiasVoltageScanData(inputFile):
    bvsData = PbData.BiasVoltageScan()
    bvsData.readFile(inputFile)
    bvsHasProblem = bvsData.visualizeAndCheck(True)

    return bvsHasProblem

def PlotThresholdScanData(inputFile):
    return