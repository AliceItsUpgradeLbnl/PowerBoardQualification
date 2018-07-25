#!/usr/bin/python

#----------------------------------------------------------------------------------------
# Title: Template test script for the ALICE ITS Power Board 8-module version
# Institution: Lawrence Berkeley National Laboratory
# Author: Alberto Collu
# Created: 11-09-2016
# Last edited: 11-09-2016 (Alberto Collu)
# Description: This script is used to generate I2C write and read commands for the ITS power board 8-channel
#----------------------------------------------------------------------------------------

import os
import io
import sys
import time
from definitions import WriteToDevice
from definitions import ReadFromDevice
from definitions import ReadRSFromDevice

#------------------------------------------ Main ----------------------------------------

THaddress = (0x31, 0x33, 0x43, 0x51)
boardtype = ("Master", "Slave")

def SetThresh(board,channel,value):
	if board==0:
        	print "MASTER"
	else:
        	print "SLAVE"

   	print "Threshold set to 0x%X" %int(value)

	for ich in range (0, 8):
		if channel[ich]==1:
			print "Channel %d" %ich
			WTF = int(3<<4 | (ich%4)<<0)
			print "address %X" %WTF
			WriteToDevice(int(THaddress[board*2 + int(ich/4)]), (3<<4 | (ich%4)<<0), int(value), int(value))


	#WriteToDevice(int(THaddress[board*2]), 0x3F, int(value), int(value))  #drop threshold to relatch
	#WriteToDevice(int(THaddress[board*2+1]), 0x3F, int(value), int(value))  #drop threshold to relatch

	print "DONE"
	return 0
