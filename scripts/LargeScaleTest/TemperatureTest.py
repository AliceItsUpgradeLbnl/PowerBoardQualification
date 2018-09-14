#!/usr/bin/python
import time

from UsefulFunctions import *
from math import sqrt

def TemperatureTest(output, PowerUnitID = 1, Vset=125):
    # Writing header to output file
    header = "Vavg[V] Itot[A] T[C]"
    with open(output,"ab") as f:
        f.write(str(header) + "\n")

    # Starts communication with RDO board
    OpenFtdi()

    # Configuring all the required devices
    ConfigureRTD(PowerUnitID) # Configure RTD to be able to read it
    ConfigurePowerADC(PowerUnitID) # Configure power ADC to be able to read voltages/currents 
    SetPowerVoltageAll(Vset, PowerUnitID) 

    # Lowering thresholds to latch enabled channels, raising threshold
    LowerThresholdsToMin(PowerUnitID) 
    time.sleep(0.5)
    RaiseThresholdsToMax(PowerUnitID) #to avoid latching
    UnlatchPowerAll(PowerUnitID)   # Unlatch all channels
    time.sleep(0.5)
  
    # Defining some initial variables
    boardSensorID  = 1
    aux1SensorID   = 2
    aux2SensorID   = 3
    Tboardfirst    = 0
    Tboardlast     = 0
    Taux1last      = 0 
    Taux2last      = 0 
    Triggered      = False   
    LUinitialstate = GetPowerLatchStatus(PowerUnitID)
    passed         = (LUinitialstate == 0b1111111111111111)

    TboardfirstSamples = [ReadRTD(PowerUnitID, boardSensorID) for x in range(10)]
    Taux1firstSamples  = [ReadRTD(PowerUnitID, aux1SensorID) for x in range(10)]
    Taux2firstSamples  = [ReadRTD(PowerUnitID, aux2SensorID) for x in range(10)]
    Tboardfirst = sum(TboardfirstSamples)/10.
    TboardfirstRms = sqrt(sum([(x - TboardfirstRms)^2 for x in TboardfirstSamples])/10.)
    Taux1first  = sum(Taux1firstSamples)/10.
    Taux1firstRms = sqrt(sum([(x - Taux1firstRms)^2 for x in Taux1firstSamples])/10.)
    Taux2first  = sum(Taux2firstSamples)/10.
    Taux2firstRms = sqrt(sum([(x - Taux2firstRms)^2 for x in Taux2firstSamples])/10.)
    if any([x > 0.1 for x in [TboardfirstRms, Taux1firstRms, Taux2firstRms]]):
        passed = False
    if any([abs(x - 25.) > 5. for x in [Tboardfirst, Taux1first, Taux2first]]):
        passed = False
    
    print ' '
    print 'Printing results:' 
    print "Vavg[V]     Itot[A]     Tboard[C]     Taux1[C]     Taux2[C]     LUstate"
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
            
	else:
	    line = "%8.5f %11.5f %12.5f %13.5f %12.5f %21s" % (Vavg, Itot, Tboard, Taux1, Taux2, str(bin(LUstate)) )
            print line

    with open(output,"ab") as f:
        f.write(str(line) + "\n")

    print ' '
    LowerThresholdsToMin(PowerUnitID)

    # Stops communication with RDO board
    CloseFtdi()

    # Test is passed if the last temperature of the board is 70C and the other two temperatures are within 5 degrees of 25C
    passed = passed and (Tboardlast > 60.) and (Tboardlast < 70.) 

    return passed
