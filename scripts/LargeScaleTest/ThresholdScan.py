#!/usr/bin/env python
__author__ = "A.Collu"
__version__ = "2.0"
__status__ = "Prototype"

import os
import io
import sys
import shutil
import numpy as np

import ReadConfig
from UsefulFunctions import *

import time
from datetime import datetime

def ThresholdScan(output, Vset, PowerUnitID):
    # Config params
    config = ReadConfig.GetMostRecentConfig('/home/its/Desktop/PB-production/PB-production/scripts/LargeScaleTest/QualificationConfig/')
    step  = config["ThresholdScan_Thstep"]
    start = config["ThresholdScan_start"]
    end   = config["ThresholdScan_end"]
    voltages  = config["ThresholdScan_Vpoints"]

    header = "CH# Threshold[DAC] Vset[DAC]     V[V]     I[A]     R[ohm]     T[C]           LUstate          Timestamp"
    with open(output,"ab") as f:
        f.write(str(header) + "\n")

    OpenFtdi() # Starts communication with RDO board

    # To monitor temperature on the power board
    ConfigureRTD(PowerUnitID) 
    # This is necessary to be able to read ADCs 
    ConfigurePowerADC(PowerUnitID) 

    for Vset in voltages:
	    # Setting voltage of all positive voltage channels
	    SetPowerVoltageAll(Vset, PowerUnitID)

	    # Setting threshold to max value
	    LowerThresholdsToMin(PowerUnitID)
	    RaiseThresholdsToMax(PowerUnitID)
	    
	    # Switching on the channels in sequence to avoid sensing issues on the TDK supply
	    UnlatchPowerWithMask(PowerUnitID, 0x000F)
	    time.sleep(0.2)
	    UnlatchPowerWithMask(PowerUnitID, 0x00FF)
	    time.sleep(0.2)
	    UnlatchPowerWithMask(PowerUnitID, 0x0FFF)
	    time.sleep(0.2)
	    UnlatchPowerWithMask(PowerUnitID, 0xFFFF)
	    time.sleep(1)  

	    LUstate = 0          
	    print " "
	    print 'Threshold scan loop. Vset set to ' + str(Vset)
	    print "Printing results:"
	    #print "CH# Th[DAC] Vset[DAC] V[V] I[A]  R[ohm] T[C]"

	    flags = np.ones(16)
	    ListOfCommands       = []
	    DataBuffer           = []
	    ThresholdData        = [] # Contains all databytes read during the scan (encoded)
	    DecodedThresholdData = [] # Contains the state of the channels vs the various threshold settings

            ifloat = [0. for i in xrange(16)]
            vfloat = [0. for i in xrange(16)]
            for i in range(10):
                ifl, vfl, idi, vd = ReadPowerADC(PowerUnitID)
                ifloat = [ifloat[i] + ifl[i] for i in xrange(len(ifl))]
                vfloat = [vfloat[i] + vfl[i] for i in xrange(len(vfl))]
            ifloat = [ifloat[i]/10. for i in xrange(len(ifloat))]
            vfloat = [vfloat[i]/10. for i in xrange(len(vfloat))]
            
	    # Scan thresholds and check when channels latch
            thresholdList = []
	    for j in range (0, 4096, step):
		LinkType  = ThresPowerLink
		threshold = (4095 - j)
                if (j % 64 == 0) or IsNearThreshold(threshold, ifloat[0]) or IsNearThreshold(threshold, ifloat[1]):
                    thresholdList.append(threshold)
                else:
                    continue
                    
		I2CData   = [0x3F, threshold/16, (threshold%16)<<4]
		## Set thresholds
		for I2CAddress in ThresPowerAddress: 
		    AppendWriteToDevice(ListOfCommands, I2CLink(PowerUnitID, LinkType), I2CAddress, *I2CData)
		AppendSleep(ListOfCommands, 20000) # 100 ms sleep default
		## Get channels status
		for I2CAddress in IOExpanderPowerAddress:
		    LinkType     = IOExpanderPowerLink
		    AppendReadFromDevice(ListOfCommands, DataBuffer, I2CLink(PowerUnitID, LinkType), I2CAddress, 1)    

		if (j % 250 == 0 and j != 0):
		    SendPacket(ListOfCommands, DataBuffer)
		    ThresholdData.extend(DataBuffer)
		    DataBuffer     = [] 
		    ListOfCommands = []

	    # Sending last commands and collecting data
	    SendPacket(ListOfCommands, DataBuffer)
	    ThresholdData.extend(DataBuffer)
	    
	    # Reformatting data
	    LUstatus = 0
	   
	    # Decoding channel state
	    for i in range (0, len(ThresholdData)):
		if (i%6 == 1 or i%6 == 4):
		    if i%6 == 4:
			LUstatus = LUstatus | (ThresholdData[i] << 8)
			DecodedThresholdData.append(LUstatus & 0xFFFF)
			LUstatus = 0
		    else:
			LUstatus = ThresholdData[i]

	    Rload = [0. for i in xrange(16)]
	    for channel in range(0,16):
		itrigger = -666
		lastLUstate = -999
		for i in range(len(thresholdList)):
		    LUstate = DecodedThresholdData[i]
		    if (not (int(LUstate) & 2**channel)):
			print 'Channel %i latched at threshold %i' %(channel, thresholdList[i])
			itrigger = thresholdList[i]
			lastLUstate = LUstate
			break

		Rload[channel] = vfloat[channel]/ifloat[channel]

		T = ReadRTD(PowerUnitID, 1)
                line = "%2d %10d %9d %13.4f %9.4f %8.4f %10.4f %022s %24s" \
                       % (channel, itrigger, Vset, vfloat[channel], ifloat[channel], Rload[channel], T, format(int(LUstate), '#016b'), str(datetime.now().strftime("%Y%m%dT%H%M%S%f")))
                with open(output,"ab") as f:
		    f.write(str(line) + "\n")
	    
    print " "
    # Making sure that channels are latched
    LowerThresholdsToMin(PowerUnitID)

    # Ends communication with RDO board
    CloseFtdi()

def IsNearThreshold(dacThreshold, current):
    currentDacValue = int(409.6 + 1228.8*current)
    return dacThreshold > (currentDacValue - 64) and dacThreshold < (currentDacValue + 64)
