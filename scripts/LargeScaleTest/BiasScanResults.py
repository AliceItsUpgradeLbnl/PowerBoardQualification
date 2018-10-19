#!/usr/bin/python

import Statistics as st
import os

resultsFolder = "/home/its/Desktop/PB-production/PB-production/scripts/RESULTS/"

def BiasScanAnalysis():
    dictOfBiasScanFiles  = GetBiasResultFiles()
    numberOfTestedBoards = len(dictOfBiasScanFiles)
    for PowerBoardID in dictOfBiasScanFiles: 
        #if not PowerBoardID == str(6):
        #    continue
        print "PowerBoardID " + str(PowerBoardID)
	for PowerUnitID in dictOfBiasScanFiles[PowerBoardID]:
            print "PowerUnitID " + str(PowerUnitID)
	    for Load in dictOfBiasScanFiles[PowerBoardID][PowerUnitID]:
		bsData = st.BiasScan() 
		bsData.readFile(resultsFolder + dictOfBiasScanFiles[PowerBoardID][PowerUnitID][Load])
		vint, vslope, iint, islope = bsData.visualizeAndCheck()
		dictOfBiasScanFiles[PowerBoardID][PowerUnitID][Load] = iint
                if Load == "High":
                    print "Offset " + str(iint)
            
        if dictOfBiasScanFiles[PowerBoardID]["Right"]["High"] > -0.0075 and dictOfBiasScanFiles[PowerBoardID]["Left"]["High"] > -0.0075:
	    print "Grade for this power board is: Inner Layers grade"
        else:
            print "Grade for this power board is: Outer Layers grade"


def GetBiasResultFiles():
   PowerUnitIDCollectables = ["Right", "Left"]
   LoadCollectables = ["Low", "Nominal", "High"]
   datFiles = [x for x in os.listdir(resultsFolder) if x.split(".")[-1] == "dat"]
   biasFiles = [x for x in datFiles if x.split("_")[3] == "BiasCalibration"] 
   boardFiles = {}
   for x in biasFiles:
       PowerBoardID = int(x.split("_")[0].split("-")[1])
       PowerUnitID  = x.split("_")[1].split("-")[1]
       Load         = x.split("_")[2].split("-")[1]
       if PowerBoardID not in boardFiles:
           boardFiles[PowerBoardID] = {}
       if PowerUnitID not in boardFiles[PowerBoardID]:
           if PowerUnitID not in PowerUnitIDCollectables:
               continue
           boardFiles[PowerBoardID][PowerUnitID] = {}
       if Load not in boardFiles[PowerBoardID][PowerUnitID]:
           if Load not in LoadCollectables:
               continue
           boardFiles[PowerBoardID][PowerUnitID][Load] = x
   return boardFiles

BiasScanAnalysis()
