#!/usr/bin/python

from __future__ import division
import os
import io
import sys
import time
from definitions import WriteToDevice
from definitions import ReadFromDevice
from definitions import ReadRSFromDevice
import math
import datetime

#------------------------------------------ Main ----------------------------------------

#os.system("clear")
#print "-------------------- Test 4: output voltages/currents scan -----------------------\n"

def mean(data):
    total = float(sum(data))
    return total/(len(data))

def variance(data):
# Use the Computational Formula for Variance.
    n = float(len(data))
    ss = float(sum(x**2 for x in data) - (sum(data)**2)/n)
    if ss == 0 or (n-1) == 0:
        return 0.0
    return float(ss/(n-1))

def standard_deviation(data):
    var = variance(data)
    if var < 0.:
        var = 0.
    return math.sqrt(var)


ADCaddress = (0x21, 0x23, 0x22, 0x24)
POTaddress = (0x2C, 0x2D, 0x2E, 0x2F)
THaddress = (0x31, 0x33, 0x43, 0x51)
ENaddress = (0x20, 0x27)

testpoints = ("CH0_V", "CH0_I", "CH1_V", "CH1_I", "CH2_V", "CH2_I", "CH3_V", "CH3_I", "CH4_V", "CH4_I", "CH5_V", "CH5_I", "CH6_V", "CH6_I", "CH7_V", "CH7_I")

boardtype = ("Master", "Slave")

def relatch(board):
    board = int(board)

    WriteToDevice(int(THaddress[board*2]), 0x3F, 0x00, 0x00)  #drop threshold to relatch
    time.sleep(0.5)
    WriteToDevice(int(THaddress[board*2+1]), 0x3F, 0x00, 0x00)  #drop threshold to relatch
    print "Latching channels"

    return 0

def unlatch(board):
    board = int(board)

    WriteToDevice(int(THaddress[board*2]), 0x3F, 0xFF, 0xFF)  #raise threshold to unlatch
    time.sleep(0.5)
    WriteToDevice(int(THaddress[board*2+1]), 0x3F, 0xFF, 0xFF)  #raise threshold to unlatch

    return 0


def enable(board,chMask):
	board = int(board)
	ENadd = int(ENaddress[board])

	#unlatch(board)

	enMask = (~chMask & 0xFF)

   	WriteToDevice(int(ENaddress[board]), int(enMask)) # Enable the Outputs
	time.sleep(0.5)
   	WriteToDevice(int(ENaddress[board]), 0xFF) # Enable the Latch Read Back

	print "Channels Enabled"

	return 0

#def ReadChannel(channel,flag):
#	if flag==0:
		
#	else:
	


#------------------- Scan the channels --------------------
def SetCh(board,channel,nor,stepsize,tapp,TestFlag):
   if board==0:
	print "MASTER" 
   else:
	print "SLAVE"

   chMask = 0
   chnlist = list()

   fname = list()
   fpointer = list()

   v_ch = list()
   curr_ch = list()

   print "Number of Reads = %d, Step size = %d" %(int(nor),int(stepsize))
   nor = int(nor)

   DB = list()
   if int(stepsize)==0:
	DB.append(120)
   else:
	stepping = int(stepsize)
   	for pv in range(0x00, 0xFF, int(stepping)):
		DB.append(int(pv))
	if DB[(len(DB)-1)]< (0xFF):
		DB.append(int(0xFF))

   print len(DB)

   board = int(board)
   ENadd = int(ENaddress[board])

   ADCadd = list()
   POTadd = list()
   THadd = list()

   lflag = 0
   hflag = 0

   AH = 0

   for ich in range (0, 8):
     if channel[ich]==1:
	chMask = chMask | 1<<ich
	chnlist.append(int(ich))

	for j in range(0, 2):
		fname.append("txtfiles/%s_ScanVI_data%s_%s.txt" % (boardtype[board], tapp, testpoints[ich*2 + j]))
		fpointer.append("file_%s" % (testpoints[ich*2 + j]))
		if os.path.exists(fname[AH]): # Delete data file with this name if found
			os.remove(fname[AH])
		try:  # Create new data file
			fpointer[AH] = open(fname[AH],'a+')
			print "Created file:  %s" %(fname[AH])
		except:
			print('Failed attempt to create a data file. Exiting script %s...' % (sys.argv[0]))
			exit()
		AH += 1

	WriteToDevice(int(THaddress[board*2 + int(ich/4)]), (3<<4 | (ich%4)<<0), 0xFF, 0xFF)  #raise threshold so scan can be completed

	if (int((ich/4))==0 and lflag==0):
		WriteToDevice(int(ADCaddress[board*2]), 0x03, 0xC0) # Write cycle time register
		lflag = 1
	if (int((ich/4))==1 and hflag==0):
		WriteToDevice(int(ADCaddress[board*2 + 1]), 0x03, 0xC0) # Write cycle time register		
		hflag = 1
	
   #enMask = (~chMask & 0xFF)

   #WriteToDevice(int(ENaddress[board]), int(enMask)) # Enable the Outputs
   #WriteToDevice(int(ENaddress[board]), 0xFF) # Enable the Latch Read Back

   unlatch(board)
   enable(board,chMask)


   #-------------- ADC conversion register test --------------
   if(TestFlag == 1):
	   WriteToDevice(int(ADCaddress[board*2]), 0x02, 0x0F, 0xF0)
	   WriteToDevice(int(ADCaddress[board*2]+1), 0x02, 0x0F, 0xF0)
	   print "Test Flag enabled" 
   #----------------------------------------------------------

   #for DB in range(0x00, 0xFF, int(stepsize)):  # Iterate on DB with set step size (default 10)
   for PV in range(0x00, len(DB), 1):  # Iterate on DB with set step size (default 10)

	#print "Testing with input %s" %(DB[PV])

	print "        "

	#for p in range(0, len(chnlist), 1):
	for p in range(0, 8, 1):
		WriteToDevice(int(POTaddress[board*2 + int(p/4)]), int(p%4), DB[PV])

	for c in range(0, len(chnlist), 1):  #loop through selected channels
	
		fpointer[c*2].write(str(DB[PV]) + " ")
		fpointer[c*2+1].write(str(DB[PV]) + " ")
		fpointer[c*2].write(str(nor) + " ")
		fpointer[c*2+1].write(str(nor) + " ")

		print "Channel %d: input = %d" %(chnlist[c],DB[PV])

		print ("Voltage: "),
		for nr in range(0, nor, 1):  #iterate over the number of selected reads & read the selected channels voltage
			ReadValue = ReadRSFromDevice(int(ADCaddress[board*2 + int(chnlist[c]/4)]), 2, (1<<7 | int((chnlist[c]%4)*2)<<4))  
			v_ch.append(((2.992/1024)*((ReadValue>>2) % 1024)))
			fpointer[c*2].write(str(v_ch[nr]) + " ")
			print (v_ch[nr]),
		
		#write the mean, sd, variance of the voltage
		fpointer[c*2].write(str(mean(v_ch)) + ' ')
		fpointer[c*2].write(str(standard_deviation(v_ch)) + '\n')
		print " Mean = %s  SD = %s" %(str(mean(v_ch)),str(standard_deviation(v_ch)))

		print ("Current: "),
		for nr in range(0, nor, 1):  #iterate over the number of selected reads & read the selected channels current
			ReadValue = ReadRSFromDevice(int(ADCaddress[board*2 + int(chnlist[c]/4)]), 2, (1<<7 | int((chnlist[c]%4)*2+1)<<4)) 
 			curr_ch.append((((ReadValue>>2) % 1024)/1024*2.992/10/0.05))
			fpointer[c*2+1].write(str(curr_ch[nr]) + " ")
			print (curr_ch[nr]),

		#write the mean, sd, variance of the current
		fpointer[c*2+1].write(str(mean(curr_ch)) + ' ')
		fpointer[c*2+1].write(str(standard_deviation(curr_ch)) + '\n')
		
		print " Mean = %s  SD = %s" %(str(mean(curr_ch)),str(standard_deviation(curr_ch)))

		#reset the lists for the next POT value
		v_ch = list()
		curr_ch = list()
	


   for i in range(0, len(chnlist), 1):
	fpointer[i].close()

   print "        "
   relatch(board)
   print "DONE" 
   
   return 0

