#!/usr/bin/python
import sys

from UsefulFunctions import *
from math import sqrt

from SummaryMethods import AppendTemperatureToSummaryFile

import time
from datetime import datetime

def CleanChauvenet(tempList, tempListMean):
    done = False
    while not done:
        for temp in tempList:
            if abs(temp - tempListMean) > 2.:
                tempList = [x for x in tempList if x != temp]
                continue
        done = True
    return tempList

def TemperatureTest(output, summary, PowerUnitID = 1, Vset=125, saveToFile = False):
    # Writing header to output file
    header = "Vavg[V]      Itot[A]     Tboard[C]     Taux1[C]     Taux2[C]     LUstate              Timestamp"
    with open(output,"ab") as f:
        f.write(str(header) + "\n")

    # Starts communication with RDO board
    OpenFtdi()

    # Configuring all the required devices
    ConfigureRTD(PowerUnitID) # Configure RTD to be able to read it
    ConfigurePowerADC(PowerUnitID) # Configure power ADC to be able to read voltages/currents 
    SetPowerVoltageAll(Vset, PowerUnitID) 
  
    # Defining some initial variables
    boardSensorID  = 1
    aux1SensorID   = 2
    aux2SensorID   = 3
    Tboardfirst    = 0
    Tboardlast     = 0
    Taux1last      = 0 
    Taux2last      = 0 
    Triggered      = False   
    TboardfirstSamples = [ReadRTD(PowerUnitID, boardSensorID) for x in range(10)]
    Taux1firstSamples  = [ReadRTD(PowerUnitID, aux1SensorID) for x in range(10)]
    Taux2firstSamples  = [ReadRTD(PowerUnitID, aux2SensorID) for x in range(10)]
    print TboardfirstSamples
    print Taux1firstSamples
    print Taux2firstSamples
    Tboardfirst = sum(TboardfirstSamples)/10.
    TboardfirstSamples = CleanChauvenet(TboardfirstSamples, Tboardfirst)
    TboardfirstRms = sqrt(sum([(x - Tboardfirst)**2 for x in TboardfirstSamples])/10.)
    Taux1first  = sum(Taux1firstSamples)/10.
    Taux1firstSamples = CleanChauvenet(Taux1firstSamples, Taux1first)
    Taux1firstRms = sqrt(sum([(x - Taux1first)**2 for x in Taux1firstSamples])/10.)
    Taux2first  = sum(Taux2firstSamples)/10.
    Taux2firstSamples = CleanChauvenet(Taux2firstSamples, Taux2first)
    Taux2firstRms = sqrt(sum([(x - Taux2first)**2 for x in Taux2firstSamples])/10.)

    print " " 
    print "Temperature RMS values: " + str([TboardfirstRms, Taux1firstRms, Taux2firstRms])

    # Lowering thresholds to latch enabled channels, raising threshold
    LowerThresholdsToMin(PowerUnitID) 
    time.sleep(0.5)
    RaiseThresholdsToMax(PowerUnitID) #to avoid latching
    UnlatchPowerAll(PowerUnitID)   # Unlatch all channels
    time.sleep(0.5)
    LUinitialstate = GetPowerLatchStatus(PowerUnitID)
    passed         = (LUinitialstate == 0b1111111111111111)

    print ' '
    print 'Printing results:' 
    print "Vavg[V]      Itot[A]     Tboard[C]     Taux1[C]     Taux2[C]     LUstate              Timestamp"
    while not Triggered:
        Tboard = ReadRTD(PowerUnitID, boardSensorID)
        Taux1  = ReadRTD(PowerUnitID, aux1SensorID)
        Taux2  = ReadRTD(PowerUnitID, aux2SensorID)
        I, V, I_ADC, V_ADC = ReadPowerADC(PowerUnitID)
        Vavg = sum(V)/len(V)
        Itot = sum(I)
        LUstate = GetPowerLatchStatus(PowerUnitID)
       
	if Vavg < 0.01:
            Triggered  = True
	    Tboardlast = Tboard
            
        line = "%8.5f %11.5f %12.5f %13.5f %12.5f %21s %24s" % (Vavg, Itot, Tboard, Taux1, Taux2, str(bin(LUstate)), str(datetime.now().strftime("%Y%m%dT%H%M%S%f")))
        print line
        with open(output,"ab") as f:
            f.write(str(line) + "\n")

    print ' '
    LowerThresholdsToMin(PowerUnitID)

    # Stops communication with RDO board
    CloseFtdi()

    # Test is passed if the last temperature of the board is 70C and the other two temperatures are within 5 degrees of 25C
    passed = passed and (Tboardlast > 60.) and (Tboardlast < 70.) 
    if abs(Tboardfirst - 25.) > 5.:
        passed = False
    if abs(Taux1first - 28.) > 5. or (Taux2first - 28.) > 5.:
        passed = False
    if any([x > 0.1 for x in [TboardfirstRms, Taux1firstRms, Taux2firstRms]]):
        passed = False

    initialState    = [Tboardfirst, Taux1first, Taux2first]   
    initialStateRms = [TboardfirstRms, Taux1firstRms, Taux2firstRms]   
    overtemperatureThreshold = Tboardlast
    puMapping = ["Right", "Left"]
    if saveToFile and passed:
        AppendTemperatureToSummaryFile(summary, puMapping[PowerUnitID - 1], initialState, initialStateRms, overtemperatureThreshold) 

    return passed
