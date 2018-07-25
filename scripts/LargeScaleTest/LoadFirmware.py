#!/usr/bin/python

#---------------------------------------------------------------------------
# Addressability script file for the ALICE ITS Power Board 2-module version
# Lawrence Berkeley National Laboratory
# Author: Alberto Collu
# Created: 10-14-2015
# Last edited: 10-14-2015 (Alberto Collu) 
# Description: this script load the firmware in the FPGA on the PIXEL RDO board
#---------------------------------------------------------------------------

import sys
import os
import shutil
import subprocess

def LoadFirmware():
	os.system('clear')
	print "========================================================================================="
	print "                            Start loading firmware ........."
	print "========================================================================================="
	print " "
	print " "
        subprocess.call(['/bin/bash', '-i', '-c', "/home/its/Desktop/PB-production/firmware/scripts/loadfirmware.sh"])
	print " "
	print " "
	print "========================================================================================="
	print "                            Firmware successfully loaded!"
	print "========================================================================================="
	return

LoadFirmware()
