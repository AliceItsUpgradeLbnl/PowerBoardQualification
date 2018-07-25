#!/usr/bin/python

from __future__ import division
import os
import io
import sys
import time
from definitions import WriteToDevice
from definitions import ReadFromDevice
from definitions import ReadRSFromDevice
from definitions import ReadRSFromDeviceToArray
import math
import datetime

#------------------------------------------ Main ----------------------------------------

#os.system("clear")
#print "-------------------- Test 4: output voltages/currents scan -----------------------\n"


ADCaddress = (0x21, 0x23, 0x22, 0x24)
POTaddress = (0x2C, 0x2D, 0x2E, 0x2F)
THaddress = (0x31, 0x33, 0x43, 0x51)
ENaddress = (0x20, 0x26)
boardtype = ("Master", "Slave")

def unlatch():
    for i in range(0, len(THaddress), 1):
       WriteToDevice(int(THaddress[i]), 0x3F, 0xFF, 0xFF)  #raise threshold to unlatch

    return 0

def enable(board,chMask,channel):
        board = int(board)
        ENadd = int(ENaddress[board])

        unlatch()

        enMask = (~chMask & 0xFF)

        WriteToDevice(int(ENaddress[board]), int(enMask)) # Enable the Outputs
        WriteToDevice(int(ENaddress[board]), 0xFF) # Enable the Latch Read Back

        print "Channel %d enabled" %channel

        return 0

def GetDAC(board,channel,v):
	
	DAC = int(v)

        if (DAC>255):
		DAC = 255
  	if (DAC<0):
		DAC = 0 

        print "DAC Value = %d" %int(DAC)

        WriteToDevice(int(POTaddress[board*2 + int(channel/4)]), int(channel%4), DAC)

        time.sleep(0.5) 
	return 0

def ReadADC(board,channel):
        WriteToDevice(int(ADCaddress[board*2 + int(channel/4)]), 0x02, 0x0f, 0xf8)
        ReadValues = [0,0,0,0,0,0,0,0,0]
        ReadValues = ReadRSFromDeviceToArray(int(ADCaddress[board*2+int(channel/4)]), 16, 0x70)
        v_ch = (((2.992/1024)*((ReadValues[int(channel%4)*2]>>2) % 1024)))
        print "Channel %d Voltage Read = %d" %(channel, v_ch)
        i_ch = ((((ReadValues[int(channel%4)*2+1]>>2) % 1024)/1024*2.992/10/0.05))
        print "Channel %d Current Read = %d" %(channel, i_ch)
	if i_ch==0:
		return -1
        r_load = v_ch/i_ch
	return r_load

def SetV(board,channel,voltage):
	#if board==0:
        #	print "MASTER"
	#else:
        #	print "SLAVE"
	
	chMask = 1<<channel

	#voltage = float(voltage)

	board = int(board)
	ENadd = int(ENaddress[board])
	
	#enable(board,chMask,channel)

	GetDAC(board,channel,voltage)

	#r_load = ReadADC(board,channel)
	#if r_load == -1:
	#	print "No current reading, so exiting"
	#	return -1	
	
	#v_set = voltage*((r_load + 0.058)/r_load)
	
	#GetDAC(board,channel,float(v_set))

	#ReadADC(board,channel)
	
	print "DONE"
	return 0;
