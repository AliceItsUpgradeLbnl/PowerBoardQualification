#!/usr/bin/env python

from UsefulFunctions import *
import sys


if len(sys.argv) != 3:
    print "Wrong number of passed arguments"
    sys.exit()

testType = sys.argv[1]
channel = int(sys.argv[2])
PowerUnitID = 2

OpenFtdi() # Starts communication with RDO board

RaiseThresholdsToMax(PowerUnitID)

if testType == 'bias':
    UnlatchBias(channel, PowerUnitID)
elif testType == 'power':
    UnlatchPower(channel, PowerUnitID)
else:
    print "Invalid test or channel"
    exit()

#ConfigurePowerADC(PowerUnitID)
#ConfigureBiasADC(PowerUnitID)

#try:
#    while(True):
#        if testType == "bias":
#            pass
#            #print ReadBiasADC(PowerUnitID)
#        if testType == "power":
#            pass
#            print ReadPowerADC(PowerUnitID) 
#        time.sleep(1.)
#except KeyboardInterrupt:
##    DisableBiasAll(PowerUnitID)
#    DisablePowerAll(PowerUnitID)
#    CloseFtdi() 
#    biasPs.SetOutputOff()
#    set_status_TDK(PowerUnitID - 1, "OFF")
#    sys.exit()

CloseFtdi() 
