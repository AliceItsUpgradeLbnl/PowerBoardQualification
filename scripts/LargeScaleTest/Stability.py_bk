#!/usr/bin/env python
__author__ = "M.Arratia"
__version__ = "1.0"
__status__ = "Prototype"

import os
import io
import sys
import csv
import time
from time import strftime, sleep
import datetime
import shutil
from definitions import WriteToDevice
from definitions import ReadFromDevice
from definitions import ReadRSFromDevice
from definitions import ReadRSFromDeviceToArray

import matplotlib.pyplot as plt #BREAKS MY CODE
import matplotlib.colors as colors
import matplotlib.cm as cmx
import numpy as np


#f = open("data_stability.csv", 'wt')
#try:
#    writer = csv.writer(f)
#    writer.writerow( ('Title 1', 'Title 2', 'Title 3') )
#    for i in range(10):
#        writer.writerow( (i+1, chr(ord('a') + i), '08/%02d/07' % (i+1)) )


Data_Channel = {}
for i in range(8):
    Data_Channel["Channel%i" %(i)] = []

def LUAddress(channel):
    return 0x20 #seems that the 0x20 works for both AD7997???

def Unlatch(channel):
    #Unlatches a given channel (must be integer)
    print "Unlatching channel %i" %channel 
    #if channel>3: channel = channel-4   
    WriteToDevice(LUAddress(channel) , 0xFF^ 2**channel) #ENABLE ONE CHANNEL
    WriteToDevice(LUAddress(channel) , 0xFF) #NEEDED to end the high-Z state of IO.
    time.sleep(0.5)
    return 0

def ReadLatchState(channel):
    LUstate = ReadFromDevice(LUAddress(channel), 1)
    print "Latchup State is: ", hex(LUstate)
    return  hex(LUstate)

def ReadADC():
    adcdeviceA = 0x21
    adcdeviceB = 0x23  
    DataA = ReadRSFromDeviceToArray(adcdeviceA, 16, 0x70)
    DataB = ReadRSFromDeviceToArray(adcdeviceB, 16, 0x70)
    del DataA[-1]
    del DataB[-1]
    Data = DataA+DataB
    V = [GetVoltageInVolts(Data[2*x]) for x in range(0,8)]
    I = [GetCurrentinAmps(Data[2*x+1]) for x in range(0,8)]
    print "V(volts) = %.3f, %.3f , %.3f , %.3f, %.3f, %.3f, %.3f, %.3f //// I(amps)  = %.3f, %.3f , %.3f , %.3f, %.3f, %.3f, %.3f, %.3f Total I: %.3f [A]" %(V[0], V[1],
V[2], V[3], V[4], V[5], V[6], V[7], I[0], I[1], I[2], I[3], I[4], I[5], I[6], I[7], sum(I))
     
    #for i in range(10): 
     #   writer.writerow( ( ) )
    for i in range(8):
        Data_Channel["Channel%i" %i].append(V[i])
    
    return I,V


def SetVoltage(channel, voltage):
    #Sets voltage of channel to voltage. Voltage must be in adc counts [range 0, 256?]
    if voltage > 256 or voltage < 0: 
        print "Please give voltage as an integer in range 0--256", voltage 
    print "Setting voltage of channel ",  channel, "to " ,  voltage , " [ADC counts]"
    if (channel < 4):
        potdevice = 0x2C
    else:
        potdevice = 0x2D
        channel = channel-4

    WriteToDevice(potdevice, channel, voltage)
    return 

def SetThresholdsLow():
    #Set LU thresholds to the minimum to trigger latch up state in ALL channels.
    WriteToDevice(0x31, 0x3F, 0x00, 0x00) #master board channels
    WriteToDevice(0x33, 0x3F, 0x00, 0x00) #slave board channels
    print "Setting all thresholds LOW (minimum)"

def SetThresholdsHigh():
    #Set LU thresholds to the maximum 
    WriteToDevice(0x31, 0x3F, 0xFF, 0xFF) #master board channels
    WriteToDevice(0x33, 0x3F, 0xFF, 0xFF) #slave board channels
    print "Setting all thresholds HIGH (maximum)"

def SetThresholdChannel(channel, thvalue):
    #channel must be integer 0--15. Threshold value must be 0--255.
    if channel < 4:
        thdevice = 0x31
        thchannel = 0x30 | channel
    elif channel < 8:
        thdevice = 0x33
        thchannel = 0x30 | channel-4
    WriteToDevice(thdevice, thchannel, thvalue, 0x00)

def DoADCconversion(adcdevice):
    WriteToDevice(adcdevice,0x02,0x00,0x10)

def GetCurrentinAmps(ADCvalue):
    Imon = (((ADCvalue>>2) % 1024)/1024.0*2.992/10.0/0.05) #I think this assumes a resistance of 0.050
    return Imon

def GetVoltageInVolts(ADCvalue):
    Vmon = (2.999/1024)*((ADCvalue>>2) % 1024)
    return Vmon


def AddressConfigRegADC():
    WriteToDevice(0x21, 0x02, 0x0f, 0xf8) #this is probably not necessary w/ 1 channel
    WriteToDevice(0x23, 0x02, 0x0f, 0xf8) #this is probably not necessary w/ 1 channel
    return 

def StabilityTest(channel, nreadings, voltage=220):
    print "Starting stability test on channel %d. Setting all channels to %d volts (ADC)"  %(channel,voltage)
    SetThresholdsLow() #Set Thresholds low to latch everything. 
    ReadLatchState(channel) #print latchup state.    
    SetThresholdsHigh() #Set Thresholds high to avoid latching. 
    SetVoltage(channel, voltage) #set the voltage of channel to 144 ADC counts.
    Unlatch(channel)             #Unlatch channel.
    AddressConfigRegADC() #address the config register of monitoring ADC.   
    ReadLatchState(channel)  #Read (and print) latch up state.

    for i in range(nreadings): 
         ReadADC()

    print "About to start enabling channels"
    for enabled_channel in range(0,8):
        #time.sleep(3)
        if enabled_channel == channel: continue #skip enabling the channel under test.
        print "-----------------------------"
        print "Enabling channel, ", enabled_channel
        SetVoltage(enabled_channel, voltage) #set the voltage of channel to 9 ADC counts.
        Unlatch(enabled_channel)
        ReadLatchState(enabled_channel) 
        for i in range(nreadings):  #measure n times the I,V of channel under test 
            ReadADC()
          #  SetVoltage(enabled_channel, 144+10*i) #set the voltage of channel to 9 ADC counts
    for disabled_channel in range(0,8):
        print "Disabling channel, ", disabled_channel
        SetThresholdChannel(disabled_channel, 0)
        ReadLatchState(disabled_channel)
        for i in range(nreadings):  #measure n times the I,V of channel under test
            ReadADC()        

    return 
    
##START MAIN
print "---------Stability Test------------------------"
startime = time.strftime("%Y-%m-%d_%H-%M-%S")
t1 = datetime.datetime.now()
StabilityTest(0,20) #test stability of channel x, n times

print Data_Channel
print len(Data_Channel)



jet = cm = plt.get_cmap('jet') 
cNorm  = colors.Normalize(vmin=0, vmax=8)
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

for i in range(8):
    colorVal = scalarMap.to_rgba(i)
    plt.plot(Data_Channel["Channel%i" %i], '-o', label ='#%i' %i, color=colorVal)



limup = Data_Channel["Channel0"][0]*1.02
limdo = Data_Channel["Channel0"][0]*0.98


plt.legend(loc='best', numpoints =1, ncol=2)
plt.xlabel('Reading number')
plt.ylabel('Voltage [V]')
plt.savefig('stabilitydata_0.pdf')

plt.ylim(limdo,limup)
plt.savefig('stabilitydata_1.pdf')



#plt.ylabel('some numbers')
#plt.savefig('$WINDOWS/prueba.pdf')
#LUstate = ReadFromDevice(0x20, 1)
#print "Latchup State is ", LUstate
