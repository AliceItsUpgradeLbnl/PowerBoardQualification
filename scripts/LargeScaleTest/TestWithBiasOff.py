#!/usr/bin/env python

from UsefulFunctions import *
from BkPrecision168xInterface import BkPrecision168xInterface
from PowerUtils import *
import sys

#if len(sys.argv) != 3:
#    print "Wrong number of passed arguments"
#    sys.exit()

#testType = sys.argv[1]
#channel = int(sys.argv[2])
PowerUnitID = 2

biasPs = BkPrecision168xInterface()
biasPs.SetVoltage(5.0)
biasPs.SetCurrentUpperLimit(10)
biasPs.SetOutputOn()

set_volt_TDK(PowerUnitID - 1, 3.3)
set_status_TDK(PowerUnitID - 1, "ON")
time.sleep(4)
OpenFtdi() # Starts communication with RDO board
# Initial configuration of RTD
ConfigureRTD(PowerUnitID)

# Preparing list of commands to write to Bias and read from RTD
SensorID = 1
ListOfCommands = []
DataBuffer = []
# Gap is in us
def ReadWriteInterleaved(NumberOfReads, gap):
    for i in range(0, NumberOfReads):
        LinkType       = IOExpanderBiasLink
        channel = 1
        I2CAddress     = IOExpanderBiasAddress
        I2CData   = [0xFF & (1 << channel%8)]
        AppendWriteToDevice(ListOfCommands, I2CLink(PowerUnitID, LinkType), I2CAddress, *I2CData)
        AppendSleep(ListOfCommands, gap) 
        LinkType       = BridgeTempLink
        I2CData = [0x1 << (SensorID - 1), 0x1, 0xFF]
        NumOfBytesToRead = 2
        AppendWriteToDevice(ListOfCommands, I2CLink(PowerUnitID, LinkType), BridgeTempAddress, *I2CData)
        AppendReadFromDevice(ListOfCommands, DataBuffer, I2CLink(PowerUnitID, LinkType), BridgeTempAddress, NumOfBytesToRead)
        I2CData = [0x1 << (SensorID - 1), 0x2, 0xFF]
        AppendWriteToDevice(ListOfCommands, I2CLink(PowerUnitID, LinkType), BridgeTempAddress, *I2CData)
        AppendReadFromDevice(ListOfCommands, DataBuffer, I2CLink(PowerUnitID, LinkType), BridgeTempAddress, NumOfBytesToRead)
    SendPacket(ListOfCommands, DataBuffer)
    GetTemperatures(DataBuffer)

def GetTemperatures(DataBuffer):
    TemperatureData = [GetTemperature([DataBuffer[i*6 + 1], DataBuffer[i*6 + 4]]) for i in range(0, len(DataBuffer)/6)]
    print TemperatureData

def GetTemperature(DataBuffer):
    ResistanceValue = ((DataBuffer[0] & 0xFF) << 7) | ((0xFF & DataBuffer[1]) >> 1)
    TemperatureValue = (ResistanceValue - 8192.)/31.54
    return TemperatureValue

try:
    while(True):
        ReadWriteInterleaved(200, 0)
        biasPs.SetOutputOff()
        set_status_TDK(PowerUnitID - 1, "OFF")
        sys.exit()
except KeyboardInterrupt:
    CloseFtdi() 
    biasPs.SetOutputOff()
    set_status_TDK(PowerUnitID - 1, "OFF")
    sys.exit()

CloseFtdi() 
