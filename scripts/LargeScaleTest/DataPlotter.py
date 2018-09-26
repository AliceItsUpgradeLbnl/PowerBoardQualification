#!/usr/bin/python

import PowerboardTestData as PbData
import ROOT

def PlotVoltageScanData(inputFile, load):
    vsData = PbData.VoltageScan(load) 
    vsData.readFile(inputFile)

    vsHasProblem = False
    plotOption = 2
    if (plotOption == 1):
        vsHasProblem = vsData.visualizeAndCheck()
    elif (plotOption == 2):
        vsHasProblem = vsData.visualizeAndCheck(True, True)

    return vsHasProblem

def PlotBiasScanData(inputFile, load):
    bvsData = PbData.BiasScan(load)
    bvsData.readFile(inputFile)
    bvsHasProblem = bvsData.visualizeAndCheck(True)

    return bvsHasProblem

def PlotThresholdScanData(inputFile, load):
    return
