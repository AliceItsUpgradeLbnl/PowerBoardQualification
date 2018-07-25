#!/usr/bin/python
import time

from UsefulFunctions import *


def TemperatureTest(output, timestep=0.5, PowerUnitID=1, Vset=125):
    # Starts communication with RDO board
    OpenFtdi()

    # Configuring all the required devices
    ConfigureRTD(PowerUnitID) #configure RTD to be able to read it
    LowerThresholdsToMin(PowerUnitID) #to latch everything and erase whatever previous state
    RaiseThresholdsToMax(PowerUnitID) #to avoid latching
    SetPowerVoltageAll(Vset, PowerUnitID) #set power voltage
    UnlatchPowerAll(PowerUnitID)   # Unlatch all channels
    ConfigurePowerADC(PowerUnitID) # Configure power ADC to be able to read currents 
    time.sleep(1)
  
    # Defining some initial variables
    boardSensorID  = 1
    aux1SensorID   = 2
    aux2SensorID   = 3
    Tboardlast     = 0
    Taux1last      = 0 
    Taux2last      = 0 
    Triggered      = False   
    LUinitialstate = GetPowerLatchStatus(PowerUnitID)
    passed         = (LUinitialstate == 0b1111111111111111)

    print ' '
    print 'Printing results:' 
    print "Vavg[V]     Itot[A]     Tboard[C]     Taux1[C]     Taux2[C]     LUstate"
    while not Triggered:
        Tboard = ReadRTD(PowerUnitID, boardSensorID)
        Taux1  = ReadRTD(PowerUnitID, aux1SensorID)
        Taux2  = ReadRTD(PowerUnitID, aux2SensorID)
        I, V, I_ADC, V_ADC = ReadPowerADC(PowerUnitID)
        Itot = sum(I)
        Vavg = sum(V)/len(V)
        LUstate = GetPowerLatchStatus(PowerUnitID)
       
	if Vavg < 0.001:
            Triggered = True
	    Tboardlast = Tboard
	    Taux1last  = Taux1
	    Taux2last  = Taux2
            
	else:
	    line = "%8.5f %11.5f %12.5f %13.5f %12.5f %21s" % (Vavg, Itot, Tboard, Taux1, Taux2, str(bin(LUstate)) )
            print line

    with open(output,"ab") as f:
        f.write(str(line) + "\n")

    print ' '
    LowerThresholdsToMin(PowerUnitID)
    DisablePowerAll(PowerUnitID)

    # Stops communication with RDO board
    CloseFtdi()

    # Test is passed if the last temperature of the board is 70C and the other two temperatures are within 5 degrees of 25C
    passed = passed and (Tboardlast > 70.) and (abs(Taux1last - 25.) < 5.) and (abs(Taux2last - 25.) < 5.) and LUstate 

    return passed
