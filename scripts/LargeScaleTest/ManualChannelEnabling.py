#!/usr/bin/env python

from UsefulFunctions import *
from BkPrecision168xInterface import BkPrecision168xInterface
from PowerUtils import *
import sys

if len(sys.argv) != 3:
    print "Wrong number of passed arguments"
    sys.exit()

testType = sys.argv[1]
channel = int(sys.argv[2])
PowerUnitID = 1

biasPs = BkPrecision168xInterface()
biasPs.SetVoltage(5.0)
biasPs.SetCurrentUpperLimit(10)
biasPs.SetOutputOn()

set_volt_TDK(PowerUnitID - 1, 3.3)
set_status_TDK(PowerUnitID - 1, "ON")


OpenFtdi() # Starts communication with RDO board

RaiseThresholdsToMax(PowerUnitID)

SetPowerVoltageAll(200, PowerUnitID)

time.sleep(5)

if testType == 'bias':
    UnlatchBias(channel, PowerUnitID)
elif testType == 'power':
    UnlatchPower(channel, PowerUnitID)
else:
    print "Invalid test or channel"
    exit()

ConfigurePowerADC(PowerUnitID)
ConfigureBiasADC(PowerUnitID)
RaiseThresholdsToMax(PowerUnitID)

try:
    while(True):
        if testType == "bias":
            print ReadBiasADC(PowerUnitID)
        if testType == "power":
            print ReadPowerADC(PowerUnitID) 
        time.sleep(1.)
except KeyboardInterrupt:
    DisableBiasAll(PowerUnitID)
    DisablePowerAll(PowerUnitID)
    CloseFtdi() 
    biasPs.SetOutputOff()
    set_status_TDK(PowerUnitID - 1, "OFF")
    sys.exit()

CloseFtdi() 
