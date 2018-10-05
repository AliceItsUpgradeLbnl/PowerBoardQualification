#!/usr/bin/python

import Statistics as st
import os

resultsFolder = "/home/its/Desktop/powerboard_8channel_tests/PB_8-channel/scripts/TXTFILES/"

def BiasScanAnalysis():
    dictOfBiasScanFiles  = GetBiasResultFiles()
    numberOfTestedBoards = len(dictOfBiasScanFiles)
    for PowerBoardID in dictOfBiasScanFiles: 
        if not PowerBoardID == str(9):
            continue
        print "PowerBoardID " + str(PowerBoardID)
	for PowerUnitID in dictOfBiasScanFiles[PowerBoardID]:
            print "PowerUnitID " + str(PowerUnitID)
	    for Load in dictOfBiasScanFiles[PowerBoardID][PowerUnitID]:
		bsData = st.BiasScan() 
		bsData.readFile(resultsFolder + dictOfBiasScanFiles[PowerBoardID][PowerUnitID][Load])
		vint, vslope, iint, islope = bsData.visualizeAndCheck()
		dictOfBiasScanFiles[PowerBoardID][PowerUnitID][Load] = iint
                if Load == "1":
                    print "Offset " + str(iint)
            


def GetBiasResultFiles():
   PowerUnitIDCollectables = ["1", "2"]
   LoadCollectables = ["1", "2", "3"]
   txtFiles = [x for x in os.listdir(resultsFolder) if x.split(".")[-1] == "txt"]
   biasFiles = [x for x in txtFiles if x.split("_")[6] == "BiasVoltageScan"] 
   boardFiles = {}
   for x in biasFiles:
       PowerBoardID = x.split("_")[1].split("ID")[1]
       PowerUnitID  = x.split("_")[3].split("ID")[1]
       Load         = x.split("_")[4].split("Type")[1]
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
