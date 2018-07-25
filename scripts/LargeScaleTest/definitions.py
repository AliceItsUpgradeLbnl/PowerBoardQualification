#!/usr/bin/python

#---------------------------------------------------------------------------
# Definitions file for ALICE ITS Power Board test environment
# Lawrence Berkeley National Laboratory
# Author: Alberto Collu
# Created: 10-14-2015
# Last edited: 4-14-2017 (Alberto Collu) 
# Description: This file contains the function definitions for the test
#              environment for the Production Power Board
#
# I2Clink mapping in hexadecimal (see application in Append* functions)
#    0-5 : Unused 
#    6   : Digital potentiometers on ADC_DAC board (for beam tests)
#    7   : Unused
#    8   : I2C devices on DUT via single ended lines (for beam tests) 
#    9   : Unused
#    A   : I2C devices on Power Unit 1 via the differential main channel (for PB lab tests)
#    B   : I2C devices on Power Unit 1 via the differentia; auxiliary channel (for PB production lab tests)
#    C-D : Unused
#    E   : I2C devices on Power Unit 2 via the differential main channel (for PB lab tests)
#    F   : I2C devices on Power Unit 2 via the differential auxiliary channel (for PB production lab tests)
#---------------------------------------------------------------------------

import os
import io
import sys
import time
import math
import ftdIOmodule

# serial numbers of the ftdi dev/port on the RDO board 
ftdiSerial     = "FTWUOJEW"
ftdiSerialFull = "FTWUOJEWA"

# firmware headers/trailers
SPIHEADERMSP   = 0xADC
I2CHEADERMSP   = 0xABC
OPTRAILER      = 0xFEEDBEEF

# Write to I2C slave device:
# I2CLink = I2C channel used to communicate with the slaves
# Address = slave address
# args = bytes to send after slave address
def WriteToDevice (I2CLink, I2CAddress, *args):

    ListOfCommands = []
    DataBuffer = [] 

    if len(args) == 1:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 2:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 3:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[2])<<8 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | len(args))
        ListOfCommands.append(command)
    else:
        return -1

    SendPacket(ListOfCommands, DataBuffer)       

    return 0

# Read from I2C slave device:
# I2Clink = I2C link ID (please check the I2C link options at the beginning of this file)
# I2CAddress = slave address of the target device
# NumOfBytes = num of bytes to read from slave device
# args = bytes to send after slave address
def ReadFromDevice(I2CLink, I2CAddress, NumOfBytes, *args):
    if (NumOfBytes > 31):
      print "Error: The number of bytes to read exceeds 31"
      return -1

    ListOfCommands = []
    DataBuffer = [None] * (NumOfBytes/2 + NumOfBytes%2 + 2)

    if len(args) == 0:
        command = str(192<<16 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 1:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 2:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 3:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[2])<<8 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    else:
        return -1

    SendPacket(ListOfCommands, DataBuffer)

    DecodedData = []
    DecodeI2CData(DataBuffer, 0, DecodedData, 2, 0xFFFF, 1)  
     
    return DecodedData 

# Read from I2C slave device (with reapeated start):
# I2Clink = I2C link ID (please check the I2C link options at the beginning of this file)
# I2CAddress = slave address of the target device
# NumOfBytes = num of bytes to read from slave device
# args = bytes to send after slave address
def ReadRSFromDevice(I2CLink, I2CAddress, NumOfBytes, *args):
    if (NumOfBytes > 31):
      print "Error: The number of bytes to read exceeds 31"
      return -1

    ListOfCommands = []
    DataBuffer = [None] * (NumOfBytes/2 + NumOfBytes%2 + 2)

    if len(args) == 0:
        command = str(192<<16 | 1<<7 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 1:
        command = str(192<<16 | int(args[0])<<8 | 1<<7 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 2:
        command = str(192<<16 | int(args[0])<<8 | 1<<7 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 3:
        command = str(192<<16 | int(args[0])<<8 | 1<<7 |  int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[2])<<8 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    else:
        return -1

    SendPacket(ListOfCommands, DataBuffer)

    DecodedData = []
    DecodeI2CData(DataBuffer, 0, DecodedData, 2, 0xFFFF, 1)
 
    return DecodedData

def OpenFtdi ():
    return ftdIOmodule.open_ftdi(ftdiSerialFull)

def CloseFtdi ():
    return ftdIOmodule.close_ftdi()

# Append a hardware sleep to the command list (to use in packed based readout)
# ListOfCommands = Reference to an external list of commands (list to append to the commands for this op)
# sleepTime = sleep time in us. Odd numbers will be rounded
def AppendSleep (ListOfCommands, sleepTime):
    if (sleepTime):
        command = str(1<<30 | (0x00FFFFFF & int(sleepTime)/2))
    else:
        command = str(1<<30 | 1)

    ListOfCommands.append(command)
       
    return 0

# Append a write-to-I2C-slave-device command sequence to a command list (to use in packed based readout):
# ListOfCommands = Reference to an external list of commands (list to append to the commands for this op)
# I2Clink = I2C link ID (please check the I2C link options at the beginning of this file)
# I2CAddress = slave address of the target device
# args = bytes to send after slave address
def AppendWriteToDevice (ListOfCommands, I2CLink, I2CAddress, *args):
    if len(args) == 1:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 2:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 3:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[2])<<8 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | len(args))
        ListOfCommands.append(command)
    else:
        return -1
       
    return 0

# Append a read-from-I2C-slave-device command sequence to a command list (it does not return data, this is done by SendPacket):
# ListOfCommands = Reference to an external list of commands (list to append to the commands for this op)
# I2Clink = I2C link ID (please check the I2C link options at the beginning of this file)
# I2CAddress = slave address of the target device
# NumOfBytes = num of bytes to read from slave device
# args = bytes to send after slave address
def AppendReadFromDevice(ListOfCommands, DataBuffer, I2CLink, I2CAddress, NumOfBytes, *args):
    if (NumOfBytes > 31):
      print "Error: The number of bytes to read exceeds 31"
      return -1

    if len(args) == 0:
        command = str(192<<16 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 1:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 2:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 3:
        command = str(192<<16 | int(args[0])<<8 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[2])<<8 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    else:
        return -1

    ResizeList(DataBuffer, NumOfBytes/2 + NumOfBytes%2 + 2)
       
    return 0

# Append a read-from-I2C-slave-device (with reapeated start) to a command list (it does not return data, this is done by SendPacket):
# ListOfCommands = Reference to an external list of commands (list to append to the commands for this op)
# I2Clink = I2C link ID (please check the I2C link options at the beginning of this file)
# I2CAddress = slave address of the target device
# NumOfBytes = num of bytes to read from slave device
# args = bytes to send after slave address
def AppendReadRSFromDevice(ListOfCommands, DataBuffer, I2CLink, I2CAddress, NumOfBytes, *args):
    if (NumOfBytes > 31):
      print "Error: The number of bytes to read exceeds 31"
      return -1

    if len(args) == 0:
        command = str(192<<16 | 1<<7 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 1:
        command = str(192<<16 | int(args[0])<<8 | 1<<7 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 2:
        command = str(192<<16 | int(args[0])<<8 | 1<<7 | int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    elif len(args) == 3:
        command = str(192<<16 | int(args[0])<<8 | 1<<7 |  int(I2CAddress))
        ListOfCommands.append(command)
        command = str(256<<16 | int(args[2])<<8 | int(args[1]))
        ListOfCommands.append(command)
        command = str(128<<16 | I2CLink<<7 | NumOfBytes<<2 | len(args))
        ListOfCommands.append(command)
    else:
        return -1

    ResizeList(DataBuffer, NumOfBytes/2 + NumOfBytes%2 + 2)

    return 0

# Sends a packet of commands (InputList) and receives a buffer of data (OutputList)
def SendPacket(InputList, OutputList):
    return ftdIOmodule.sendPacket(InputList, OutputList)

# Reads one or more times all the 32 ADC channels on the ADC board 
def ReadADCs(DataBuffer, NumberOfSamplesPerChannel = None):
    if (numberOfSamplesPerChannel == None):
        ListOfCommands = []
        ListOfCommands.append(0x008000F8)
        SizeList(DataBuffer, 14)
    elif (numberOfSamplesPerChannel <= 100):
        ListOfCommands = []
        for i in range (0, numberOfSamplesPerChannel):
            ListOfCommands.append(0x008000F8)
            ListOfCommands.append(str(1<<30 | 0x1388)) # adding 10ms delay between samples
        SizeList(DataBuffer, NumberOfSamplesPerChannel*14)
    else:
        print "Error: number of ADC samples exceeds 100"
        return -1
     
    SendPacket(ListOfCommands, DataBuffer)

    return 0 


# Decodes a one or more I2C data packets received from the firmware
# InputDataBuffer     : buffer of data as received from the firmware (32-bit format)
# InputReadPointer    : position of the first 32-bit data to start decoding from
# OutputDataBuffer    : buffer containing the decoded data (output of this function)
# DataWordSizeInBytes : Size in bytes of the datawords to extract from the input buffer
# DataWordMask        : mask to apply to the extracted data word bytes
# RepeatNTimes        : number of I2C packets to decode  
def DecodeI2CData(InputDataBuffer, InputReadPointer, OutputDataBuffer, DataWordSizeInBytes, DataWordMask, RepeatNTimes):
    if (InputReadPointer >= len(InputDataBuffer) - 1): # At least one header and trailer must be in the buffer
        print "Error: InputReadPointer incompatible with the length of InputDataBuffer" 
        return -1

    if (InputReadPointer < 0):
        print "Error: InputReadPointer cannot be lower than 0"
        return -1

    if ((DataWordSizeInBytes < 1) | (DataWordSizeInBytes > 2)):
        print "Error: size of the datawords in bytes is not in the allowed range (1-2)"
        return -1

    if (DataWordMask > ((1<<DataWordSizeInBytes*8) - 1)):
        print "Error: data word mask is wider than the data word size"
        return -1


    NumDataWordsPerInputWord = 2/DataWordSizeInBytes     
    i = 0
    NumOfI2CTransactions = RepeatNTimes

    while (RepeatNTimes):

        if (InputDataBuffer[InputReadPointer]>>20 != I2CHEADERMSP | InputDataBuffer[InputReadPointer]>>20 != SPIHEADERMSP):
            print "Error: I2C/SPI header is wrong. Expected: ABCXXXXX or ADCXXXXX, Received: " + InputDataBuffer[InputReadPointer] 
            return -1

        InputReadPointer+=1

        while (InputDataBuffer[InputReadPointer] != OPTRAILER):
            inputWord = InputDataBuffer[InputReadPointer] 
            j = NumDataWordsPerInputWord

            while (j):
                OutputDataBuffer.append( (inputWord & DataWordMask) >> int(math.log(GetNumberOfShiftsToFirstHighBit(DataWordMask), 2)) )
                inputWord = inputWord >> DataWordSizeInBytes*8
                j-=1
                i+=1
            
            InputReadPointer+=1

        InputReadPointer+=1
        RepeatNTimes-=1

    return 0


# Writes a buffer of data to file
def AppendDataBufferToFile(DataBuffer, Filename):
	f = open(Filename, "ab") 

	i = 0
	while i < len(DataBuffer):
		binaryString = bytearray([DataBuffer[i] & 0xFF, DataBuffer[i]>>8 & 0xFF, DataBuffer[i]>>16 & 0xFF, DataBuffer[i]>>24 & 0xFF])
		f.write(binaryString)
		i+=1
		

# Returns the number of right shifts necessary to bring the first high bit of a number in position 0
def GetNumberOfShiftsToFirstHighBit(Number):
    if (Number%2):
        return 1

    return Number & (~Number << 1)    

# Empties a list and appends "size" elements
def SizeList(List, size):
    List[:] = []
    for x in range (0, size):
      List.append(None)

    return 0

# Appends "increment" empty elements to a list
def ResizeList(List, increment):
    for x in range (0, increment):
      List.append(None)

    return 0
