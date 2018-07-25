#!/usr/bin/python

from __future__ import division
import os
import io
import sys
import time
from definitions import *
import math
import datetime

ENaddress = (0x26, 0x25)
DACaddress = (0x32, 0x50)

def BiasScan():
        stepsize = 10
        WriteToDevice(int(ENaddress[board]), 0x80) 

	for VAL in range(0, 255, int(stepsize)):
		print VAL
		time.sleep(1)
		WriteToDevice(int(DACaddress[board]), 0x3F, VAL, 0x00)
		time.sleep(5)

	WriteToDevice(int(DACaddress[board]), 0x3F, 0xFF, 0x00)
	time.sleep(5)
	WriteToDevice(int(ENaddress[board]), 0xFF) #shutdown bias

	print "DONE"
	return 0
