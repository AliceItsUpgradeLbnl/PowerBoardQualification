#!/usr/bin/python

import Statistics as st

resultsFolder = "../RESULTS/"

dataFiles = GetVoltageScanFiles()



loads = ["Low", "Nominal", "High"]
resMeasured = {}

resMeasured["Low"] = [[] for i in range(32)]
resMeasured["Nominal"] = [[] for i in range(32)]
resMeasured["High"] = [[] for i in range(32)]

resMean = {}
resMean["Low"]     = 0.
resMean["Nominal"] = 0.
resMean["High"]    = 0.

resSigma = {}
resSigma["Low"]     = 0.
resSigma["Nominal"] = 0.
resSigma["High"]    = 0.

def VoltageScanAnalysis():
	for load in loads:
	    listOfPURVoltageScanFiles = GetResultFiles(PowerUnitID = "Right", load = load, test = "VoltageScan")
	    numberOfTestedBoards = len(listOfPURVoltageScanFiles)
	    for vscanFile in listOfPURVoltageScanFiles:
		vsData = st.VoltageScan() 
		vsData.readFile(vscanFile)
		vints, vslopes, ivslopes, iints, islopes = vsData.visualizeAndCheck()
		for i in range(0, 16):
		    resMeasured[load][i].append(ivslopes[i])
	    listOfPULVoltageScanFiles = GetResultFiles(PowerUnitID = "Left", load = load, test = "VoltageScan")
	    for vscanFile in listOfPULVoltageScanFiles:
		vsData = st.VoltageScan() 
		vsData.readFile(vscanFile)
		vints, vslopes, ivslopes, iints, islopes = vsData.visualizeAndCheck()
		for i in range(16, 32):
		    resMeasured[load][i].append(ivslopes[i - 16])

	    for i in range(32):
		resMean[load][i] = sum(resMeasured[load][i])/len(resMeasured[load][i])
	   
	    for i in range(32) :
		resSigma[load][i] = sum([(resMeasured[load][i][j] - resMean[load][i])**2 for j in range(len(resMeasured[load][i]))])/len(resMeasured[load][i])

def BiasScanAnalysis:
	for load in loads:
	    listOfPURBiasScanFiles = GetResultFiles(PowerUnitID = "Right", load = load, test = "BiasScan")
	    numberOfTestedBoards = len(listOfPURBiasScanFiles)
	    for bscanFile in listOfPURBiasScanFiles: 
		bsData = st.BiasScan() 
		bsData.readFile(bscanFile)
		vint, vslope, ivslope, iint, islope = bsData.visualizeAndCheck()
		resMeasured[load][0].append(ivslopes[0])
	    listOfPULBiasScanFiles = GetResultFiles(PowerUnitID = "Left", load = load, test = "BiasScan")
	    for bscanFile in listOfPULBiasScanFiles:
		bsData = st.VoltageScan() 
		bsData.readFile(bscanFile)
		vints, vslopes, ivslopes, iints, islopes = bsData.visualizeAndCheck()
		resMeasured[load][1].append(ivslopes[0])

            for i in range(2):
                resMean[load][i] = sum(resMeasured[load][i])/len(resMeasured[load][i])
	   
            for i in range(2):
	        resSigma[load][i] = sum([(resMeasured[load][i][j] - resMean[load][i])**2 for j in range(len(resMeasured[load][i]))])/len(resMeasured[load][i])

#def ThresholdScanAnalysis():
#	for load in loads:
#	    listOfPURThresholdScanFiles = GetResultFiles(PowerUnitID = "Right", load = load, test = "ThresholdScan")
#	    numberOfTestedBoards = len(listOfPURThresholdScanFiles)
#	    for tscanFile in listOfPURThresholdScanFiles:
#		tsData = st.VoltageScan() 
#		tsData.readFile(tscanFile)
#		iints, islopes = tsData.visualizeAndCheck()
#		for i in range(0, 16):
#		    resMeasured[load][i].append(ivslopes[i])
#	    listOfPULThresholdScanFiles = GetResultFiles(PowerUnitID = "Left", load = load, test = "ThresholdScan")
#	    for vscanFile in listOfPULVoltageScanFiles:
#		tsData = st.VoltageScan() 
#		tsData.readFile(tscanFile)
#		iints, islopes = tsData.visualizeAndCheck()
#		for i in range(16, 32):
#		    resMeasured[load][i].append(ivslopes[i - 16])
#
#	    for i in range(32):
#		resMean[load][i] = sum(resMeasured[load][i])/len(resMeasured[load][i])
#	   
#	    for i in range(32) :
#	        resSigma[load][i] = sum([(resMeasured[load][i][j] - resMean[load][i])**2 for j in range(len(resMeasured[load][i]))])/len(resMeasured[load][i])


def GetResultFiles(PowerUnitID, load, test):
    files = os.listdir(resultsFolder) 
    listOfDatFiles = [x.split(".")[0] for x in files if x.split(".")[-1] == "dat"]
    listOfLoadfiles = [x for x in listOfDatFiles if x.split("_")[2] == "Load-" + load]
    listOfPowerUnitfiles = [x for x in listOfLoadFiles if x.split("_")[1] == "PU-" + PowerUnitID]
    listOfTestFiles = [(resultsFolder + x) for x in listOfPowerUnitFiles if x.split("_")[3] == test]
    return listOfTestFiles
