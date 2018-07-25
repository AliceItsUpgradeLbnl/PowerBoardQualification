#!/usr/bin/env python
__author__ = "G. Contin, M.Arratia"
__version__ = "2.0"
__status__ = "Prototype"

import os
import io
import sys
import time
from time import strftime, sleep
import datetime
import shutil
import numpy as np

from UsefulFunctions import *

def thresholdScanAll(output, step, start, end, Vset, PowerUnitID):

    OpenFtdi() # Starts communication with RDO board

    ConfigureRTD(PowerUnitID) # To monitor temperature on the power board

    # Setting threshold to max value
    LowerThresholdsToMin(PowerUnitID)
    RaiseThresholdsToMax(PowerUnitID)
    SetPowerVoltageAll(Vset, PowerUnitID)

    # Switching on the channels in sequence to avoid sensing issues on the TDK supply
    UnlatchPowerWithMask(PowerUnitID, 0x000F)
    time.sleep(0.2)
    UnlatchPowerWithMask(PowerUnitID, 0x00FF)
    time.sleep(0.2)
    UnlatchPowerWithMask(PowerUnitID, 0x0FFF)
    time.sleep(0.2)
    UnlatchPowerWithMask(PowerUnitID, 0xFFFF)
    time.sleep(0.2)

    LUstate = 0          
    ConfigurePowerADC(PowerUnitID) #this is necessary to be able to read ADCs
    print " "
    print 'Threshold scan loop. Vset set to ' + str(Vset)
    print "Printing results:"
    #print "CH# Th[DAC] Vset[DAC] V[V] I[A]  R[ohm] T[C]"

    flags = np.ones(16)
    DataBuffer = [] 
    ListOfCommands       = []
    ThresholdData        = []
    DecodedThresholdData = []

    # Scan thresholds and check when channels latch
    for j in range (0, 251):
        LinkType  = ThresPowerLink
        threshold = (255 - j) << 4
        I2CData   = [0x3F, threshold/16, (threshold%16)<<4]
        ## Set thresholds
        for I2CAddress in ThresPowerAddress: 
            AppendWriteToDevice(ListOfCommands, I2CLink(PowerUnitID, LinkType), I2CAddress, *I2CData)
        AppendSleep(ListOfCommands, 20000) # 20 ms sleep default
        ## Get channels status
        for I2CAddress in IOExpanderPowerAddress:
            LinkType     = IOExpanderPowerLink
            AppendReadFromDevice(ListOfCommands, DataBuffer, I2CLink(PowerUnitID, LinkType), I2CAddress, 1)    
        ## Read data out
        AppendSleep(ListOfCommands, 20000) # 20 ms sleep default
        for I2CAddress in ADCAddress:
            for channel in range(0,8):
                I2CData = [0x20 + channel]
                LinkType = ADCLink
                NumOfBytesToRead = 2
                AppendWriteToDevice(ListOfCommands, I2CLink(PowerUnitID, LinkType), I2CAddress, *I2CData)
                AppendReadFromDevice(ListOfCommands, DataBuffer, I2CLink(PowerUnitID, LinkType), I2CAddress, NumOfBytesToRead)

        if (j % 25 == 0 and j != 0):
            SendPacket(ListOfCommands, DataBuffer)
            ThresholdData.extend(DataBuffer)
            DataBuffer     = [] 
            ListOfCommands = []

    # Reformatting data
    LUstatus = 0
   
    for i in range (0, len(ThresholdData)):
        if (i%102 == 1 or i%102 == 4):
            if i%2 == 0:
                LUstatus = LUstatus | (ThresholdData[i] << 8)
                DecodedThresholdData.append(LUstatus & 0xFFFF)
            else:
                LUstatus = ThresholdData[i]
        
  
    Voltages = [[] for x in xrange(16)]
    Currents = [[] for x in xrange(16)]
    
    j = 0
    for i in range (0, len(ThresholdData)):
        if (((i%102 - 1)%3 == 0) & (i%102 != 1) & (i%102 != 4)):
            if j%2:
                Currents[j/2].append((((ThresholdData[i]>>4 & 0xFFF)/4096.)*2.56 - 0.25)/(0.005*150) *1.00294 +0.013083 )
            else:
                Voltages[j/2].append(((ThresholdData[i]>>4 & 0xFFF)/4096.)*2.56)
         
            j = j + 1
        if (j == 32):
            j = 0

    Vlast = [0 for i in xrange(16)]
    Ilast = [0 for i in xrange(16)]
    Rload = [0 for i in xrange(16)]
    for channel in range(0,16):
        itrigger = -666
        lastLUstate = -999
        for i in range(10, 251):
            LUstate = DecodedThresholdData[i]
            if ((int(LUstate) & 2**channel) != 2**channel ):
                print 'Channel %i latched in iteration %i' %(channel, i)
                itrigger = i
                lastLUstate = LUstate
                break
       
        didItGoToZero = False
        Ilast[channel] = -999.
        Vlast[channel] = -999.
        for i in range(251):
            Vread = Voltages[channel][i]
            Iread = Currents[channel][i]
            if(Vread==0):
                print 'Channel %i voltage went to zero in iteration %i' %(channel, i)
                didItGoToZero = True
                break
            Vlast[channel] = Vread
            Ilast[channel] = Iread
            
        if(Iread!=0): rload = Vlast[channel]/Ilast[channel]
                
        if not didItGoToZero:
            Vlast[channel] = -999
            Ilast[channel] = -999
        T = ReadRTD(PowerUnitID, 1)
        line = "%d %5d %5d %10.2f %8.4f %8.4f %8.4f %s" % (channel, itrigger, Vset, Vlast[channel], Ilast[channel], Rload[channel], T, str(bin(LUstate)) )
        with open(output,"ab") as f:
            f.write(str(line) + "\n")
    
    # Set the thresholds low to latch all unlatched channels (this should not be necessary if the board works properly), and then re-raise the thresholds for next test
    print " "
    LowerThresholdsToMin(PowerUnitID)
    RaiseThresholdsToMax(PowerUnitID)                

    # Ends communication with RDO board
    CloseFtdi()

    return 
