#!/usr/bin/env python

import PowerboardTestData as PbData

temporaryFile = "../JUNK/ThresholdScan_PowerUnitRight.txt"

PowerUnitID = "Right"
load = "High"
summaryFile = "summaryFile"

tsData = PbData.ThresholdScan(PowerUnitID, load, summaryFile) 
tsData.readFile(temporaryFile)
passed = not tsData.visualizeAndCheck(True, True)

