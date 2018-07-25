#!/usr/bin/python
from UsefulFunctions import *

def I2CTest(PowerUnitID):
    passed = True

    OpenFtdi()

    # Digital potentiometers
    print "Checking digipots for bias"
    CheckPotentiometersBias(PowerUnitID)
    print "Checking digipots for power"
    CheckPotentiometersPower(PowerUnitID)

    # Check IO expanders
    print "Checking IO expanders for bias"
    GetBiasLatchStatus(PowerUnitID)
    print "Checking IO expanders for power"
    GetPowerLatchStatus(PowerUnitID)

    # Check Temperature reading circuits
    ConfigureRTD(PowerUnitID)
    print "Checking RTDs"
    configurations = ReadRTDConfiguration(PowerUnitID)
    for configuration in configurations: 
        if configuration != 0xC0: # Default configuration 
	    passed = False

    # Check ADCs
    print "Checking ADCs"
    ReadPowerADC(PowerUnitID)
    ReadBiasADC(PowerUnitID)

    print "Checking DACs"
    state = []
    SetThresholdAll(PowerUnitID, 0) 
    for i in [0, 4, 8, 12]:
        print "Checking threshold IC " + str(i/4)
        state.append((GetPowerLatchStatus(PowerUnitID) >> i))
        SetThreshold(i, 4095, PowerUnitID) 
    	UnlatchPower(i, PowerUnitID)  
        time.sleep(0.2)
        state.append((GetPowerLatchStatus(PowerUnitID) >> i))
        SetThreshold(i, 0, PowerUnitID) 
        time.sleep(0.2)
        state.append((GetPowerLatchStatus(PowerUnitID) >> i))
	if state != [0, 1, 0]:
	    passed = False
        state = []

    print "Checking bias control"
    ConfigureBiasADC(PowerUnitID) 
    SetBiasVoltage(125, PowerUnitID)     
    time.sleep(0.5)
    if (ReadBiasADC(PowerUnitID) > -4.):
	passed = False
    SetBiasVoltage(0, PowerUnitID)     
    time.sleep(0.5)
    if (ReadBiasADC(PowerUnitID) < -2.):
	passed = False

    CloseFtdi()

    return passed
