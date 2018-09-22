#!/usr/bin/env python
import os
import io
import sys
import time
from time import strftime, sleep
import datetime
import shutil
from Definitions import *

# I2C links for the various power board devices
BridgeTempLink      = "main"
ADCLink             = "main"
PotPowerLink        = "main"
ThresPowerLink      = "main"
IOExpanderPowerLink = "aux"
ADCBiasLink         = "main"
PotBiasLink         = "main"
IOExpanderBiasLink  = "main"

# I2C addresses for the various power board devices
BridgeTempAddress      = (0x28)
ADCAddress             = (0x1D, 0x1F, 0x35, 0x37)
ADCBiasAddress         = (0x1E)
PotPowerAddress        = (0x2C, 0x2D, 0x2E, 0x2F)
ThresPowerAddress      = (0x52, 0x60, 0x70, 0x72) 
IOExpanderPowerAddress = (0x38, 0x39) 
PotBiasAddress         = (0x29)
IOExpanderBiasAddress  = (0x38) 

class prettyfloat(float):
    def __repr__(self):
        return "%0.6f" % self

# Define I2C link address
def I2CLink(PowerUnitID, LinkType):
    if   ((PowerUnitID == 1) & (LinkType == "aux")):
        return 0xB
    elif ((PowerUnitID == 1) & (LinkType == "main")):
        return 0xA
    elif ((PowerUnitID == 2) & (LinkType == "aux")):
        return 0xF
    elif ((PowerUnitID == 2) & (LinkType == "main")):
        return 0xE
    else:
        print "Wrong power unit ID or link type provided, exiting..."
        sys.exit(1)

def RaiseThresholdsToMax(PowerUnitID):
    print 'Raising all thresholds to maximum value ...' 

    LinkType = ThresPowerLink
    I2CData = [0x3F, 0xFF, 0xFF]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), ThresPowerAddress[0], *I2CData)    
    WriteToDevice(I2CLink(PowerUnitID, LinkType), ThresPowerAddress[1], *I2CData)
    WriteToDevice(I2CLink(PowerUnitID, LinkType), ThresPowerAddress[2], *I2CData)   
    WriteToDevice(I2CLink(PowerUnitID, LinkType), ThresPowerAddress[3], *I2CData)

def LowerThresholdsToMin(PowerUnitID):
    print 'Lowering all thresholds to minimum value ...' 

    LinkType = ThresPowerLink
    I2CData = [ 0x3F, 0x00, 0x00]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), ThresPowerAddress[0], *I2CData)
    WriteToDevice(I2CLink(PowerUnitID, LinkType), ThresPowerAddress[1], *I2CData)
    WriteToDevice(I2CLink(PowerUnitID, LinkType), ThresPowerAddress[2], *I2CData)
    WriteToDevice(I2CLink(PowerUnitID, LinkType), ThresPowerAddress[3], *I2CData)

def SetThreshold(channel, value, PowerUnitID): 
    #print 'Setting thresholds for channel #%d' % (channel)
    if (channel > 15):
        print 'Channel #%d does not exist' % (channel)
    if (value >= (1<<12)):
        print 'DAC value is higher than allowed: %h' % (value)

    LinkType = ThresPowerLink
    WriteToDevice(I2CLink(PowerUnitID, LinkType), ThresPowerAddress[channel/4], (3<<4 | channel%4), value/16, ((value%16<<4)))

def SetThresholdAll(PowerUnitID, value): 
    #print 'Setting all thresolds'
    if (value >= (1<<12)):
        print 'DAC value is higher than allowed: %h' % (value)

    LinkType = ThresPowerLink
    for channel in range (0, 16):
        WriteToDevice(I2CLink(PowerUnitID, LinkType), ThresPowerAddress[channel/4], (3<<4 | channel%4), value/16, ((value%16<<4)))

def ConfigurePowerADC(PowerUnitID):
    print "Configuring Power ADCs..."    

    LinkType = ADCLink
    for SlaveAddress in ADCAddress:
    	I2CData = [0x0, 0x0] # Setting the start bit of the configuration register to 0 (to be able to set the conversion rate register)
    	WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)    
        I2CData = [0x7, 0x1] # Setting the conversion rate register
        WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)    
        I2CData = [0xB, 0x2] # Setting the advanced configuration register
        WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)    
        I2CData = [0x0, 0x1] # Setting the configuration register
        WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)   

def ConfigureBiasADC(PowerUnitID):
    print "Configuring Bias ADCs..."

    LinkType = ADCBiasLink
    SlaveAddress = ADCBiasAddress
    I2CData = [0x0, 0x0] # Setting the start bit of the configuration register to 0 (to be able to set the conversion rate register)
    WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)    
    I2CData = [0x7, 0x1] # Setting the conversion rate register
    WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)    
    I2CData = [0xB, 0x2] # Setting the advanced configuration register
    WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)    
    I2CData = [0x0, 0x1] # Setting the configuration register
    WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)    

def ReadPowerADC(PowerUnitID):
    #print "Reading the ADC channels for power..."

    LinkType = ADCLink
    NumOfBytesToRead = 2
    V = []
    I = []
    V_ADC = []
    I_ADC = []
    for SlaveAddress in ADCAddress:
        for channel in range(0, 8):
            I2CData = [0x20 + channel]
            WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)
            ADCValue = ReadFromDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, NumOfBytesToRead)
            if channel%2:
                I.append( (((ADCValue[0]>>4)/4096.)*2.56 - 0.25)/(0.005*150) ) #*1.00294 +0.013083 )
                I_ADC.append( (ADCValue[0]>>4)/4096.)
            else:
                V.append( ((ADCValue[0]>>4)/4096.)*2.56*6./5. ) # In the new power boards the dynamic range has been increased
                V_ADC.append( (ADCValue[0]>>4)/4096. )
    #print I
    #print V
    return I,V, I_ADC ,V_ADC

def ReadPowerChannelVoltage(channel, PowerUnitID):
    #print "Reading channel voltage..."

    LinkType = ADCLink
    NumOfBytesToRead = 2
    SlaveAddress = ADCAddress[channel/4]
    I2CData = [0x20 + ((channel%4) * 2)]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)
    ADCValue = ReadFromDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, NumOfBytesToRead)
    return ((ADCValue[0]>>4)/4096.) * 3.072

def ReadPowerChannelVoltages(PowerUnitID):
    #print "Reading channel voltages..."

    voltages = []
    for channel in range(0, 16):
        voltages.append(ReadPowerChannelVoltage(channel, PowerUnitID))

    return voltages

def ReadPowerChannelCurrent(channel, PowerUnitID):
    #print "Reading channel current..."

    LinkType = ADCLink
    NumOfBytesToRead = 2
    SlaveAddress = ADCAddress[channel/4]
    I2CData = [0x20 + ((channel%4) * 2) + 1]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)
    ADCValue = ReadFromDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, NumOfBytesToRead)
    return (((ADCValue[0]>>4)/4096.) * 2.56 - 0.25)/(0.005 * 150)

def ReadPowerChannelCurrents(PowerUnitID):
    #print "Reading channel currents..."

    currents = []
    for channel in range(0, 16):
        currents.append(ReadPowerChannelCurrent(channel, PowerUnitID))

    return currents

def ReadBiasADC(PowerUnitID):
    #print "Reading the ADC channels for bias..."

    LinkType = ADCBiasLink
    NumOfBytesToRead = 2
    Array = []
    SlaveAddress = ADCBiasAddress
    for channel in range(0, 8):
        I2CData = [0x20 + channel]
        WriteToDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, *I2CData)
        ADCValue = ReadFromDevice(I2CLink(PowerUnitID, LinkType), SlaveAddress, NumOfBytesToRead)
        Array.append( ((ADCValue[0]>>4)/4096.)*2.56 )
  
    I = Array[0]
    V = Array[2]*(-2.)
    return I,V

def SetPowerVoltageAll(voltage, PowerUnitID):
    for channel in range (0, 16):
        #print 'Setting voltage %f to channel %i, power unit #%i' %(voltage, channel, PowerUnitID)
        SetPowerVoltage(channel, voltage, PowerUnitID)

def SetPowerVoltage(channel, voltage, PowerUnitID=1):
    #print 'Setting power voltage of channel %d to %d [DAC]' %(channel, voltage) 
    if (channel > 15):
        print 'Channel #%d for power does not exist' %(channel)

    LinkType = PotPowerLink
    WriteToDevice(I2CLink(PowerUnitID, LinkType), PotPowerAddress[channel/4], channel%4, int(voltage))

def SetBiasVoltage(voltage, PowerUnitID=1):
    #print 'Setting bias voltage to %d [DAC]' %(voltage) 

    LinkType = PotBiasLink
    I2CData = [0x11, int(voltage)]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), PotBiasAddress, *I2CData) 

# Goes through and returns if there are no issues
def CheckPotentiometersPower(PowerUnitID):
    LinkType = PotPowerLink
    for Address in PotPowerAddress:
    	ReadFromDevice(I2CLink(PowerUnitID, LinkType), Address, 1)

# Goes through and returns if there are no issues
def CheckPotentiometersBias(PowerUnitID):
    LinkType = PotBiasLink
    ReadFromDevice(I2CLink(PowerUnitID, LinkType), PotBiasAddress, 1)

def GetPowerLatchStatus(PowerUnitID):
    #print 'Reading status of power channels...'
    LinkType = IOExpanderPowerLink
    LUstate = (ReadFromDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[0], 1))[0]
    LUstate = LUstate | (ReadFromDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[1], 1))[0]<<8
    return LUstate

def GetBiasLatchStatus(PowerUnitID):
    #print 'Reading status of bias channels...'
    LinkType = IOExpanderBiasLink
    LUstate = (ReadFromDevice(I2CLink(PowerUnitID, LinkType), IOExpanderBiasAddress, 1))[0]
    return bin(LUstate)

def UnlatchPowerAll(PowerUnitID):
    #print 'Unlatching ALL power channels'
    LinkType = IOExpanderPowerLink
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[0], 0xFF) 
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[1], 0xFF) 

    
def UnlatchBiasAll(PowerUnitID):
    #print 'Unlatching ALL bias channels'
    LinkType = IOExpanderBiasLink
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderBiasAddress, 0x00) 

def UnlatchBiasWithMask(mask, PowerUnitID):
    #print 'Unlatching ALL bias channels'
    LinkType = IOExpanderBiasLink
    mask = 0xFF - mask
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderBiasAddress, mask) 

def UnlatchPower(channel,PowerUnitID):
    #print 'Unlatching power channel #%d' %(channel)
    if (channel > 15):
        print "Channel %d for power does not exist" % (channel)
    LinkType = IOExpanderPowerLink
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[channel/8], 0x1 << (channel%8)) 

def UnlatchPowerWithMask(PowerUnitID, mask):
    print 'Unlatching power channel mask %d' %(mask)

    LinkType = IOExpanderPowerLink
    if (mask & 0xFF):
        WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[0], mask & 0xFF) 
    if ((mask>>8) & 0xFF):
        WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[1], (mask>>8) & 0xFF) 

def UnlatchPowerAllSpecial(PowerUnitID):
    #unlatches channels in blocks needed to avoid voltage drop that triggers overtemperature circuit. 
    LinkType = IOExpanderPowerLink
    sleep = 0.020
    print ' Unlatching first 2 channels' 
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[0], 0x03)
    time.sleep(sleep)
    print ' Unlatching first 4 channels' 
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[0], 0x0F)
    time.sleep(sleep)
    print ' Unlatching first 6 channels'
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[0], 0x3F)
    time.sleep(sleep)
    print ' Unlatching first 8 channels'
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[0], 0xFF)
    time.sleep(sleep)
    print ' Unlatching first 10 channels'
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[1], 0x03)
    time.sleep(sleep)
    print ' Unlatching first 12 channels'
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[1], 0x0F)
    time.sleep(sleep)
    print ' Unlatching first 14 channels'
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[1], 0x3F)
    time.sleep(sleep)
    print ' Unlatching first 16 channels'
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[1], 0xFF)

def UnlatchBias(channel,PowerUnitID):
    #print 'Unlatching bias channel #%d' %(channel)
    if (channel > 8):
        print 'Channel #%d for bias does not exist' % (channel)
    LinkType = IOExpanderBiasLink
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderBiasAddress, int(0xFF^2**channel)) 

def DisablePowerAll(PowerUnitID):
    #print 'Disabling ALL power channels'
    LinkType = IOExpanderPowerLink
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[0], 0x00) 
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderPowerAddress[1], 0x00) 

def DisableBiasAll(PowerUnitID):
    #print 'Disabling ALL bias channels'
    LinkType = IOExpanderBiasLink
    WriteToDevice(I2CLink(PowerUnitID, LinkType), IOExpanderBiasAddress, 0xFF) 

def ConfigureRTD(PowerUnitID):
    print "Configuring RTDs..."

    LinkType = BridgeTempLink
    I2CData = [0x1, 0x80, 0xC2]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, *I2CData)
    I2CData = [0x2, 0x80, 0xC2]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, *I2CData)
    I2CData = [0x4, 0x80, 0xC2]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, *I2CData)

def ReadRTDConfiguration(PowerUnitID):
    configurations = []
    LinkType = BridgeTempLink
    I2CData = [0x1, 0x00, 0xFF]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, *I2CData)
    configurations.append(ReadFromDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, 2)[0] & 0xFF)
    I2CData = [0x2, 0x00, 0xFF]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, *I2CData)
    configurations.append(ReadFromDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, 2)[0] & 0xFF)
    I2CData = [0x4, 0x00, 0xFF]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, *I2CData)
    configurations.append(ReadFromDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, 2)[0] & 0xFF)

    return configurations

def ReadRTD(PowerUnitID, SensorID):
    #print "Reading from RTD..."
    if SensorID < 1 or SensorID > 3:
	print "Wrong SensorID provided while attempting to read from a temperature sensor"
	sys.exit()

    LinkType = BridgeTempLink
    I2CData = [0x1 << (SensorID - 1), 0x1, 0xFF]
    NumOfBytesToRead = 2
    WriteToDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, *I2CData)
    time.sleep(0.06)
    ResistanceValue = ReadFromDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, NumOfBytesToRead)
    I2CData = [0x1 << (SensorID - 1), 0x2, 0xFF]
    WriteToDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, *I2CData)
    time.sleep(0.06)
    ResistanceValue[0] = ((ResistanceValue[0] & 0xFF) << 7) | ((0xFF & ReadFromDevice(I2CLink(PowerUnitID, LinkType), BridgeTempAddress, NumOfBytesToRead)[0])>>1)
    TemperatureValue = (ResistanceValue[0] - 8192.)/31.54

    return TemperatureValue
