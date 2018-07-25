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

def I2C():
 # Define I2C link address
 I2CLink         = 0xA
 print "-------------------------- Test I2C ------------------------------\n"
 OpenFtdi()
 print "Raise threshold - Master"
 WriteToDevice(I2CLink, 0x31, 0x3F, 0xFF, 0xFF) #raising threshold 
 WriteToDevice(I2CLink, 0x33, 0x3F, 0xFF, 0xFF) 

 print "Raise threshold - Slave"
 WriteToDevice(I2CLink, 0x43, 0x3F, 0xFF, 0xFF) 
 WriteToDevice(I2CLink, 0x51, 0x3F, 0xFF, 0xFF) 

 print "---- LU enable ----"
 print "Read Master LU State:  %X" %(ReadFromDevice(0x20, 1))

 print "Enable Master"
 WriteToDevice(I2CLink, 0x20, 0x00)
 WriteToDevice(I2CLink, 0x20, 0xFF)

 print "Re-Read Master LU State:  %X \n" %(ReadFromDevice( I2CLink, 0x20, 1))

 print "Read Slave LU State:  %X" %(ReadFromDevice( I2CLink, 0x27, 1))

 print "Enable Slave"
 WriteToDevice( I2CLink, 0x27, 0x00)
 WriteToDevice( I2CLink, 0x27, 0xFF)

 print "Re-Read Slave LU State:  %X \n" %(ReadFromDevice( I2CLink, 0x27, 1))

 print "---- Other I/O ----"
 print "Read back state - Master"
 print "%X" %(ReadFromDevice( I2CLink, 0x26, 1))

 print "Read back state - Slave"
 print "%X \n" %(ReadFromDevice( I2CLink, 0x25, 1))

 print "---- POT ----"
 print "Write: 0x34 0x35 0x36 0x37"
 WriteToDevice( I2CLink, 0x2c, 0x00, 0x34)
 WriteToDevice( I2CLink,0x2c, 0x01, 0x35)
 WriteToDevice( I2CLink,0x2c, 0x02, 0x36)
 WriteToDevice( I2CLink, 0x2c, 0x03, 0x37)
 print "Read: %X %X %X %X" %(ReadRSFromDevice( I2CLink, 0x2c, 1, 0x00), ReadRSFromDevice( I2CLink, 0x2c, 1, 0x01), ReadRSFromDevice( I2CLink, 0x2c, 1, 0x02), ReadRSFromDevice( I2CLink, 0x2c, 1, 0x03))

 print "Write: 0x44 0x45 0x46 0x47"
 WriteToDevice(0x2d, 0x00, 0x44)
 WriteToDevice(0x2d, 0x01, 0x45)
 WriteToDevice(0x2d, 0x02, 0x46)
 WriteToDevice(0x2d, 0x03, 0x47)
 print "Read: %X %X %X %X" %(ReadRSFromDevice(0x2d, 1, 0x00), ReadRSFromDevice(0x2d, 1, 0x01), ReadRSFromDevice(0x2d, 1, 0x02), ReadRSFromDevice(0x2d, 1, 0x03))

 print "Write: 0x54 0x55 0x56 0x57"
 WriteToDevice(0x2e, 0x00, 0x54)
 WriteToDevice(0x2e, 0x01, 0x55)
 WriteToDevice(0x2e, 0x02, 0x56)
 WriteToDevice(0x2e, 0x03, 0x57)
 print "Read: %X %X %X %X" %(ReadRSFromDevice(0x2e, 1, 0x00), ReadRSFromDevice(0x2e, 1, 0x01), ReadRSFromDevice(0x2e, 1, 0x02), ReadRSFromDevice(0x2e, 1, 0x03))

 print "Write: 0x64 0x65 0x66 0x67"
 WriteToDevice(0x2f, 0x00, 0x64)
 WriteToDevice(0x2f, 0x01, 0x65)
 WriteToDevice(0x2f, 0x02, 0x66)
 WriteToDevice(0x2f, 0x03, 0x67)
 print "Read: %X %X %X %X \n" %(ReadRSFromDevice(0x2f, 1, 0x00), ReadRSFromDevice(0x2f, 1, 0x01), ReadRSFromDevice(0x2f, 1, 0x02), ReadRSFromDevice(0x2f, 1, 0x03))

 print "---- ADC monitor ----"
 print "Write: 0x390"
 WriteToDevice(0x21, 0x02, 0x03, 0x90)
 print "Read:  %X" %(ReadRSFromDevice(0x21, 2, 0x02))

 print "Write: 0xAC0"
 WriteToDevice(0x23, 0x02, 0x0A, 0xC0)
 print "Read:  %X" %(ReadRSFromDevice(0x23, 2, 0x02))

 print "Write: 0xBD0"
 WriteToDevice(0x22, 0x02, 0x0B, 0xD0)
 print "Read:  %X" %(ReadRSFromDevice(0x22, 2, 0x02))

 print "Write: 0xC30"
 WriteToDevice(0x24, 0x02, 0x0C, 0x30)
 print "Read:  %X \n" %(ReadRSFromDevice(0x24, 2, 0x02))

 print "Relatch Master"
 WriteToDevice(0x31, 0x3F, 0x00, 0x00)  #drop threshold to relatch 
 WriteToDevice(0x33, 0x3F, 0x00, 0x00)  #drop threshold to relatch 

 print "Relatch Slave"
 WriteToDevice(0x43, 0x3F, 0x00, 0x00)  #drop threshold to relatch 
 WriteToDevice(0x51, 0x3F, 0x00, 0x00)  #drop threshold to relatch 

 print 'This is the end of the I2C addresability test'
 return 0


#print 'hello'
#I2C()

