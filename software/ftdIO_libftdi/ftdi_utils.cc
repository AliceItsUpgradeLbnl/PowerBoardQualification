// C++ includes
#include <iostream>
using namespace std;

#ifdef _FTD2XX
#ifdef _WIN32
#include <windows.h>
#endif

// FTDI D2xx include
#include "ftd2xx.h"
#else
#include <ftdi.h>
typedef ftdi_context *FT_HANDLE;
typedef int FT_STATUS;
enum {
	FT_OK,
	FT_INVALID_HANDLE,
	FT_DEVICE_NOT_FOUND,
	FT_DEVICE_NOT_OPENED,
	FT_IO_ERROR,
	FT_INSUFFICIENT_RESOURCES,
	FT_INVALID_PARAMETER,
	FT_INVALID_BAUD_RATE,

	FT_DEVICE_NOT_OPENED_FOR_ERASE,
	FT_DEVICE_NOT_OPENED_FOR_WRITE,
	FT_FAILED_TO_WRITE_DEVICE,
	FT_EEPROM_READ_FAILED,
	FT_EEPROM_WRITE_FAILED,
	FT_EEPROM_ERASE_FAILED,
	FT_EEPROM_NOT_PRESENT,
	FT_EEPROM_NOT_PROGRAMMED,
	FT_INVALID_ARGS,
	FT_NOT_SUPPORTED,
	FT_OTHER_ERROR,
	FT_DEVICE_LIST_NOT_READY,
};
#endif

FT_STATUS open_ftdi(const char *serial, FT_HANDLE *fthandle)
{
  int retval;
  unsigned char Mode, Mask, LatencyTimer;

  // open a device with a specific serial number (last argument to open)
#ifdef _FTD2XX
  if ((retval = FT_OpenEx((PVOID)serial, FT_OPEN_BY_SERIAL_NUMBER, fthandle)) != FT_OK) {
  //if ((retval = FT_OpenEx((PVOID)"FTWBKCW9A", FT_OPEN_BY_SERIAL_NUMBER, &ftdi)) != FT_OK) {
    cerr << "opening device with serial " << serial << " failed with error " << retval << endl;
    return retval;
  }
#else
  if ((*fthandle = ftdi_new()) == (ftdi_context *)NULL) {
    cerr << "ftdi_new failed" << endl;
    return -1;
  }

  // open a device with a specific serial number (last argument to open)
  if ((retval = ftdi_usb_open_desc(*fthandle, 0x0403, 0x6010, NULL, serial)) < 0) {
    cerr << "opening device with serial " << serial << " failed with error " << retval << endl; 
    cerr << ftdi_get_error_string(*fthandle) << endl;
    ftdi_free(*fthandle);
    return retval;
  }
#endif

  // Set default parameters:
  Mode = 0x00; Mask = 0xff; //reset mode
  LatencyTimer = 16; // our default setting is 16

#ifdef _FTD2XX
  if((retval = FT_SetBitMode(*fthandle, Mask, Mode)) != FT_OK) return (retval);
  if((retval = FT_SetLatencyTimer(*fthandle, LatencyTimer)) != FT_OK) return (retval);
  if((retval = FT_SetUSBParameters(*fthandle, 0x10000, 0x10000)) != FT_OK) return (retval);
#else
  if((retval = ftdi_set_bitmode(*fthandle, Mask, Mode)) != FT_OK) return (retval);
  if((retval = ftdi_set_latency_timer(*fthandle, LatencyTimer)) != FT_OK) return (retval);
#endif

  return retval;
}

FT_STATUS close_ftdi(FT_HANDLE *fthandle)
{
  int retval = FT_OK;
  if (*fthandle != (FT_HANDLE)NULL) {
#ifdef _FTD2XX
    if ((retval = FT_Close(*fthandle)) == FT_OK)
      *fthandle = (FT_HANDLE)NULL;
    else
      cerr << "unable to close ftdi device: error " << retval << endl;
#else
    if ((retval = ftdi_usb_close(*fthandle)) < 0) {
      cerr << "unable to close ftdi device: error " << retval << endl;
      cerr << ftdi_get_error_string(*fthandle) << endl;
    }

    ftdi_free(*fthandle);
#endif
  }
  return retval;
}

FT_STATUS writeReg(FT_HANDLE fthandle, unsigned short address, unsigned short data, unsigned int & trailer)
{
  int ftStatus;
  unsigned int TxIntBuffer[3];
  unsigned int BytesWritten;

  // Write transaction format:
  // First 32bit word: upper 16 bits = 0xAAAA, lower 8 bits: number of words to follow
  TxIntBuffer[0] = 0xAAAA0001;
  // Second 32bit word:	TX[31] = 0 : WRITE
  //			TX[27:16] = 12bit register address
  //			TX[15: 0] = 16bit data word to write
  TxIntBuffer[1] = ((address<<16) & 0x0FFF0000) | (unsigned int)data;
  // Third 32bit word: switch firmware to read mode
  //			a single 32bit word with upper 16 bits = 0xAAAB,
  //			lower 16 bits: number of 32bit words to read (1, trailer)
  TxIntBuffer[2] = 0xAAAB0001;

  // Now send  the array
#ifdef _FTD2XX
  ftStatus = FT_Write(fthandle, TxIntBuffer, 12, &BytesWritten);
  if (ftStatus == FT_OK) {
    // FT_Write OK
    if (BytesWritten != 12)
      cerr << "FT_Write wrote " << BytesWritten << " expected 12" << endl;
    }
  else {
    // FT_Write Failed
    cerr << "Write failed with status " << ftStatus << endl;
    return(ftStatus);
  }

#else
  BytesWritten = ftdi_write_data(fthandle, (unsigned char *)TxIntBuffer, 12);
  if (BytesWritten != 12) {
    cerr << "ftdi_write_data returned " << BytesWritten << endl;
    ftStatus = BytesWritten;
    return (ftStatus);
  }
#endif

  unsigned char *RxBuffer = (unsigned char *)trailer;

#ifdef _FTD2XX
  unsigned int BytesReceived;
  unsigned int RxBytes;
  // Second: do a FTDI read transaction for the desired bytes
  // check the receive queue first:
  int timeout = 4;
  FT_GetQueueStatus(fthandle, &RxBytes);
  while ((RxBytes != 4) && (timeout-- > 0)) {
#ifdef _WIN32
    Sleep(4);
#else
    usleep(4000);
#endif
    FT_GetQueueStatus(fthandle, &RxBytes);
  }
  // if no data available, return error
  if (RxBytes != 4) return (FT_OTHER_ERROR);
  // This call will block until "expectedBytes" bytes have been received
  ftStatus = FT_Read(fthandle, RxBuffer, 4, &BytesReceived);
  if (ftStatus == FT_OK) {
    // FT_Read OK
    if (BytesReceived != 4) {
      cerr << "Read " << BytesReceived << "trailer bytes out of 4:" << endl;
        for (int i=0; i<(int)BytesReceived; i++) {
          cerr << dec << i << ": " << hex << showbase << (unsigned int)RxBuffer[i] << endl;
        }
    }
  }
  else {
    // FT_Read Failed
    cerr << "Read trailer failed with status " << ftStatus << endl;
  }

#else
  ftStatus = ftdi_read_data(fthandle, RxBuffer, 4);
  if (ftStatus == 4) { 
    // FT_Read OK 
    ftStatus = FT_OK;
  }
  else { 
    // ftdi_read_data Failed 
    cerr << "Read trailer failed with status " << ftStatus << endl;
    cerr << ftdi_get_error_string(fthandle) << endl;
  } 
#endif

   return(ftStatus);
}

FT_STATUS readReg(FT_HANDLE fthandle, unsigned short address, unsigned long long &data)
{
  int ftStatus;
  unsigned int TxIntBuffer[3];
  unsigned int BytesWritten;

  // "Read" transaction format:
  // First: do a write transaction to set the address to read:

  // First 32bit word: upper 16 bits = 0xAAAA, lower 8 bits: number of words to follow
  TxIntBuffer[0] = 0xAAAA0001;
  // Second 32bit word:	TX[31] = 1 : READ
  //						TX[27:16] = 12bit register address
  TxIntBuffer[1] = ((address<<16) & 0x0FFF0000) | 0x80000000;
  // Third 32bit word: switch firmware to read mode
  //			a single 32bit word with upper 16 bits = 0xAAAB,
  //			lower 16 bits: number of 32bit words to read (2, data + trailer)
  TxIntBuffer[2] = 0xAAAB0002;

  // Now send  the array
#ifdef _FTD2XX
  ftStatus = FT_Write(fthandle, TxIntBuffer, 12, &BytesWritten);
  if (ftStatus == FT_OK) {
    // FT_Write OK
    if (BytesWritten != 12)
      cerr << "FT_Write wrote " << BytesWritten << " expected 12" << endl;
    }
  else {
    // FT_Write Failed
    cerr << "Write address failed with status " << ftStatus << endl;
    return(ftStatus);
  }
#else
  BytesWritten = ftdi_write_data(fthandle, (unsigned char *)TxIntBuffer, 12);
  if (BytesWritten != 12) {
    cerr << "ftdi_write_data returned " << BytesWritten << endl;
    ftStatus = BytesWritten;
    return (ftStatus);
  }
#endif

  unsigned char *RxBuffer = (unsigned char *)&data;

#ifdef _FTD2XX
  unsigned int BytesReceived;
  unsigned int RxBytes;
  // Second: do a FTDI read transaction for the desired bytes
  // check the receive queue first:
  int timeout = 4;
  FT_GetQueueStatus(fthandle, &RxBytes);
  while ((RxBytes != 8) && (timeout-- > 0)) {
#ifdef _WIN32
    Sleep(4);
#else
    usleep(4000);
#endif
    FT_GetQueueStatus(fthandle, &RxBytes);
  }
  // if no data available, return error
  if (RxBytes != 8) return (FT_OTHER_ERROR);
  // This call will block until "expectedBytes" bytes have been received
  ftStatus = FT_Read(fthandle, RxBuffer, 8, &BytesReceived);
  if (ftStatus == FT_OK) {
    // FT_Read OK
    if (BytesReceived != 8) {
      cerr << "Read " << BytesReceived << " bytes:" << endl;
        for (int i=0; i<(int)BytesReceived; i++) {
          cerr << dec << i << ": " << hex << showbase << (unsigned int)RxBuffer[i] << endl;
        }
    }
  }
  else {
    // FT_Read Failed
    cerr << "Read failed with status " << ftStatus << endl;
  }

#else
  ftStatus = ftdi_read_data(fthandle, RxBuffer, 8);
  if (ftStatus == 8) { 
    // FT_Read OK 
    ftStatus = FT_OK;
  }
  else { 
    // ftdi_read_data Failed 
    cerr << "Read failed with status " << ftStatus << endl;
    cerr << ftdi_get_error_string(fthandle) << endl;
  } 
#endif

  return(ftStatus);
}

FT_STATUS SendPacket(FT_HANDLE fthandle,
	    unsigned int   numWordsToWrite,
	    unsigned int   writeDataBuffer[],
	    unsigned int   numWordsToRead,
	    unsigned int   readDataBuffer[])
{
  int ftStatus;
  unsigned int TxIntBuffer[numWordsToWrite + 2]; // Must include header and trailer 

  // Limit num of words to write and read to a 16-bit integer for now:
  numWordsToWrite = numWordsToWrite & 0xFFFF;
  numWordsToRead  = numWordsToRead  & 0xFFFF;

  // Creating a buffer with the input data + header and trailer
  TxIntBuffer[0] = 0xAAAA0000 | numWordsToWrite;
  for (unsigned int i = 0; i < numWordsToWrite - 1; i++)
  {
    TxIntBuffer[i + 1] = writeDataBuffer[i];
  }
  TxIntBuffer[numWordsToWrite + 1] = 0xAAAB0000 | numWordsToRead;

  // Calculating total packet bytes (to write and to read, with header and trailer for the received data)
  unsigned int totalNumBytesToWrite = numWordsToWrite*4 + 8;
  unsigned int totalNumBytesToRead  = numWordsToRead*4  + 8;

  unsigned int BytesWritten;

  // Now send the array
#ifdef _FTD2XX
  ftStatus = FT_Write(fthandle, TxIntBuffer, totalNumBytesToWrite, &BytesWritten);
  if (ftStatus == FT_OK) {
    // FT_Write OK
    if (BytesWritten != totalNumBytesToWrite)
      cerr << "FT_Write wrote " << BytesWritten << " expected " << totalNumBytesToWrite << endl;
    }
  else {
    // FT_Write Failed
    cerr << "Write command packet failed with status " << ftStatus << endl;
    return(ftStatus);
  }
#else
  BytesWritten = ftdi_write_data(fthandle, (unsigned char *)TxIntBuffer, totalNumBytesToWrite);
  if (BytesWritten != totalNumBytesToWrite) {
    cerr << "ftdi_write_data returned " << BytesWritten << endl;
    ftStatus = BytesWritten;
    return (ftStatus);
  }
#endif

  unsigned char *RxBuffer = (unsigned char *)readDataBuffer;

#ifdef _FTD2XX
  unsigned int BytesReceived;
  unsigned int RxBytes;
  // Second: do a FTDI read transaction for the desired bytes
  // check the receive queue first:
  int timeout = 4;
  FT_GetQueueStatus(fthandle, &RxBytes);
  while ((RxBytes != totalNumBytesToRead) && (timeout-- > 0)) {
#ifdef _WIN32
    Sleep(4);
#else
    usleep(4000);
#endif
    FT_GetQueueStatus(fthandle, &RxBytes);
  }
  // if no data available, return error
  if (RxBytes != totalNumBytesToRead) return (FT_OTHER_ERROR);
  // This call will block until "expectedBytes" bytes have been received
  ftStatus = FT_Read(fthandle, RxBuffer, totalNumBytesToRead, &BytesReceived);
  if (ftStatus == FT_OK) {
    // FT_Read OK
    if (BytesReceived != totalNumBytesToRead) {
      cerr << "Read " << BytesReceived << " bytes:" << endl;
        for (int i = 0; i < (int)BytesReceived; i++) {
          cerr << dec << i << ": " << hex << showbase << (unsigned int)RxBuffer[i] << endl;
        }
    }
  }
  else {
    // FT_Read Failed
    cerr << "Read data output from command packet failed with status " << ftStatus << endl;
  }

#else
  ftStatus = ftdi_read_data(fthandle, RxBuffer, totalNumBytesToRead);
  if (ftStatus == (int) totalNumBytesToRead) { 
    // FT_Read OK 
    ftStatus = FT_OK;
  }
  else { 
    // ftdi_read_data Failed 
    cerr << "Read data output from command packet failed with status " << ftStatus << endl;
    cerr << ftdi_get_error_string(fthandle) << endl;
  } 
#endif

  return(ftStatus);
}

FT_STATUS writeMem(FT_HANDLE fthandle,
		   unsigned short address,
		   unsigned int *datap,
		   int count)
{
  int ftStatus;
  unsigned int *TxIntBuffer = new unsigned int[65536];
  unsigned int BytesWritten;
  unsigned int numBytesToWrite;
  int numCmdWords;
  int num32BWords;
  int numFullTX;
  int remainder;
  int i,j,k;

  // where to write the memory address
  unsigned int memAddrRegAddress = 17 << 16;
  // unsigned int memLsb16Address = 18 << 16;
  // unsigned int memMsb16Address = 19 << 16;
  unsigned int memLsb16Address = 19 << 16;
  unsigned int memMsb16Address = 20 << 16;

  // max words per PXL USB protocol "write" packet is 65535
  // since each command word contains 16 bits of payload, this
  // limits the number of 32bit words per "write" packet to 32767
  remainder = count % 32767;
  numFullTX = count / 32767;
  if (remainder == 0) numFullTX -= 1; // first 32767 taken care off by sending first packet with address

  // send remainder (or first full 32767 words) first with address:
  if(remainder == 0)
    num32BWords = 32767;
  else
    num32BWords = remainder;
  numCmdWords = num32BWords * 2 + 1; // 2 command words per 32bit word plus one command word for address
  numBytesToWrite = numCmdWords*4 + 4; // 4 bytes per command word plus 4 bytes for header word

  // First 32bit word: upper 16 bits = 0xAAAA, lower 8 bits: number of words to follow
  TxIntBuffer[0] = 0xAAAA0000 + numCmdWords;
  // Second 32bit word:	memory address register
  //			TX[31] = 0 : WRITE
  //			TX[27:16] = 12bit register address
  //			TX[15: 0] = 16bit data word to write
  TxIntBuffer[1] = memAddrRegAddress | (unsigned int)address;

  k = 0;
  // All following words: LSB16B into register address 18,
  //			MSB16B into register address 19
  for(i=0; i<num32BWords; i++) {
    TxIntBuffer[i*2+2] = memLsb16Address | (datap[k] & 0xFFFF); // LSB16
    TxIntBuffer[i*2+3] = memMsb16Address | (datap[k] >>16); // MSB16
    k++;
  }


  // Now send  the array
#ifdef _FTD2XX
  ftStatus = FT_Write(fthandle, TxIntBuffer, numBytesToWrite, &BytesWritten);
  if (ftStatus == FT_OK) {
    // FT_Write OK
    if (BytesWritten != numBytesToWrite)
      cerr << "FT_Write wrote " << BytesWritten << " expected " << numBytesToWrite << endl;
    }
  else {
    // FT_Write Failed
    cerr << "Write failed with status " << ftStatus << endl;
  }
#else
  BytesWritten = ftdi_write_data(fthandle, (unsigned char *)TxIntBuffer, numBytesToWrite);
  if (BytesWritten != numBytesToWrite) {
    cerr << "ftdi_write_data returned " << BytesWritten << endl;
    ftStatus = BytesWritten;
    return (BytesWritten);
  }
  else { 
    ftStatus = FT_OK;
  }
#endif

  // if more than 32767 32bit words:
  if (numFullTX > 0) {
    // following transactions are with 32767 32bit words
    // memory address needs no longer be sent for those,
    // since the memory address auto-increments in firmware
    num32BWords = 32767;
    numCmdWords = num32BWords * 2; // 2 command words per 32bit word
    numBytesToWrite = numCmdWords*4 + 4; // 4 bytes per command word plus 4 bytes for header word
    TxIntBuffer[0] = 0xAAAA0000 + numCmdWords;
    for (j=0; j<numFullTX; j++) {
      for(i=0; i<num32BWords; i++) {
        TxIntBuffer[i*2+1] = memLsb16Address | (datap[k] & 0xFFFF); // LSB16
        TxIntBuffer[i*2+2] = memMsb16Address | (datap[k] >>16); // MSB16
	    k++;
      }

      // Now send  the array
#ifdef _FTD2XX
      ftStatus = FT_Write(fthandle, TxIntBuffer, numBytesToWrite, &BytesWritten);
      if (ftStatus == FT_OK) {
        // FT_Write OK
        if (BytesWritten != numBytesToWrite)
          cerr << "FT_Write wrote " << BytesWritten << " expected " << numBytesToWrite << endl;
        }
      else {
        // FT_Write Failed
        cerr << "Write failed with status " << ftStatus << endl;
      }
#else
      BytesWritten = ftdi_write_data(fthandle, (unsigned char *)TxIntBuffer, numBytesToWrite);
      if (BytesWritten != numBytesToWrite) {
	cerr << "ftdi_write_data returned " << BytesWritten << endl;
	ftStatus = BytesWritten;
      }
#endif
    }
  }

  return(ftStatus);
}

FT_STATUS readMem(FT_HANDLE fthandle,
	    unsigned short address,
	    unsigned int *datap,
	    int count,
	    int &wordsReceived)
{
  int ftStatus;
  unsigned int TxIntBuffer[6];
  unsigned int BytesWritten;
  unsigned int RxBytes, BytesReceived, TotalBytesReceived;
  unsigned int numWordsToRead;
  int numBytesToRead;
  unsigned char *cPtr;

  cPtr = (unsigned char *)datap;

  // limit count to 16bits for now:
  numWordsToRead = (unsigned int)count & 0xFFFF;
  numBytesToRead = numWordsToRead * 4;

  // where to write the memory address
  unsigned int memCntRegAddress = 16 << 16;
  unsigned int memAddrRegAddress = 17 << 16;
  // unsigned int memMsb16Address = 19 << 16;
  unsigned int memMsb16Address = 20 << 16;

  // First 32bit word: upper 16 bits = 0xAAAA, lower 8 bits: number of words to follow (3)
  TxIntBuffer[0] = 0xAAAA0003;
  // next command word:	memory count register
  //			TX[31] = 0 : WRITE
  //			TX[27:16] = 12bit register address
  //			TX[15: 0] = 16bit count
  TxIntBuffer[1] = memCntRegAddress | numWordsToRead;
  // next command word:	memory address register
  //			TX[31] = 0 : WRITE
  //			TX[27:16] = 12bit register address
  //			TX[15: 0] = 16bit memory address
  TxIntBuffer[2] = memAddrRegAddress | (unsigned int)address;

  // next 32bit word: MSB16B data register to read
  //			TX[31] = 1 : READ
  //			TX[27:16] = 12bit register address
  TxIntBuffer[3] = memMsb16Address | 0x80000000;
  // final 32bit word: switch firmware to read mode
  //			a single 32bit word with upper 16 bits = 0xAAAB,
  //			lower 16 bits: number of 32bit words to read
  TxIntBuffer[4] = 0xAAAB0000 | numWordsToRead;


  // Now send the array
#ifdef _FTD2XX
  ftStatus = FT_Write(fthandle, TxIntBuffer, 20, &BytesWritten);
  if (ftStatus == FT_OK) {
    // FT_Write OK
    if (BytesWritten != 20)
      cerr << "FT_Write wrote " << BytesWritten << " expected 20" << endl;
    }
  else {
    // FT_Write Failed
    cerr << "Write failed with status " << ftStatus << endl;
    return(ftStatus);
  }
#else
  BytesWritten = ftdi_write_data(fthandle, (unsigned char *)TxIntBuffer, 20);
  if (BytesWritten != 20) {
    cerr << "ftdi_write_data returned " << BytesWritten << endl;
    ftStatus = BytesWritten;
    return (ftStatus);
  }
#endif


#ifdef _FTD2XX
  unsigned int EventDWord, TxBytes;
  // wait until some bytes are ready to be read
  FT_GetStatus(fthandle, &RxBytes, &TxBytes, &EventDWord);
  while (RxBytes == 0) {
#ifdef _WIN32
    Sleep(4);
#else
    usleep(4000);
#endif
    FT_GetStatus(fthandle, &RxBytes, &TxBytes, &EventDWord);
  }
#endif
  RxBytes = numBytesToRead;


  // Second: do a FTDI read transaction for the desired bytes
  // This call will block until "expectedBytes" bytes have been received,
  // so only read available bytes
  TotalBytesReceived = 0;
#ifdef _FTD2XX
  ftStatus = FT_Read(fthandle, cPtr, RxBytes, &BytesReceived);
  if (ftStatus == FT_OK) {
    // FT_Read OK
    TotalBytesReceived = BytesReceived;
    wordsReceived = (int)TotalBytesReceived/4;

  }
  else {
    // FT_Read Failed
    cerr << "Read failed with status " << ftStatus << endl;
    return ftStatus;
  }
#else
  ftStatus = ftdi_read_data(fthandle, cPtr, RxBytes);
  if (ftStatus >= 0) { 
    // FT_Read OK 
    BytesReceived = ftStatus;
    if (BytesReceived != RxBytes) {
      cerr << "Read " << ftStatus << " bytes:" << endl;
      // for (int i=0; i<ftStatus; i++) {
      // 	cerr << dec << i << ": " << hex << showbase << (unsigned int)RxBuffer[i] << endl;
      // }
    }
    else {
      TotalBytesReceived = ftStatus;
      wordsReceived = (int)TotalBytesReceived/4;
    }
  }
  else { 
    // ftdi_read_data Failed 
    cerr << "Read failed with status " << ftStatus << endl;
    cerr << ftdi_get_error_string(fthandle) << endl;
    return ftStatus;
  } 

#endif

  if ((int)TotalBytesReceived == numBytesToRead) return FT_OK;

#ifdef _FTD2XX
  // otherwise check if there are more bytes to read
  cPtr += BytesReceived;
  FT_GetStatus(fthandle, &RxBytes, &TxBytes, &EventDWord);
  if (RxBytes > 0) {
    ftStatus = FT_Read(fthandle, cPtr, RxBytes, &BytesReceived);
    if (ftStatus == FT_OK) {
      // FT_Read OK
      TotalBytesReceived += BytesReceived;
      wordsReceived = (int)TotalBytesReceived/4;
    }
    else {
      // FT_Read Failed
      cerr << "Read failed with status " << ftStatus << endl;
      return ftStatus;
    }
  }
#endif

  return ftStatus;
}

FT_STATUS readFifo32(FT_HANDLE fthandle, unsigned int numofwords, unsigned int* data[1][14])
{

// fthandle = Device handle
// numofwords = Number of 32-bit words to receive (value provided)
// data = Buffer where the data received will be stored (pointer provided)
 
  int ftStatus = 0 ;
#ifdef _FTD2XX
  unsigned int BytesReceived;
  unsigned int RxBytes;
  unsigned char *RxBuffer;
  unsigned int WordsRead = 0;  // counter for 32-bit words received

  // Do a FTDI read transaction for the desired bytes
  // check the receive queue first:
  int timeout = 4;
  while (WordsRead < numofwords) {
    FT_GetQueueStatus(fthandle, &RxBytes);
    while ((RxBytes < 4) && (timeout-- > 0)) {
      #ifdef _WIN32
      Sleep(4);
      #else
      usleep(4000);
      #endif
      FT_GetQueueStatus(fthandle, &RxBytes);
    }
    // if no data available, return error
    if (RxBytes != 4) return (FT_OTHER_ERROR);
    RxBuffer = (unsigned char *)&data[WordsRead];
    // This call will block until "expectedBytes" bytes have been received
    ftStatus = FT_Read(fthandle, RxBuffer, 4, &BytesReceived);
    WordsRead++;
  }
#endif
  return(ftStatus);
}


FT_STATUS readFifo(FT_HANDLE fthandle,
	    unsigned int *datap,
	    int count,
	    int &wordsReceived)
{
  int ftStatus;
  unsigned int TxIntBuffer[6];
  unsigned int BytesWritten;
  unsigned int RxBytes, BytesReceived, TotalBytesReceived;
  unsigned int numWordsToRead;
  int numBytesToRead;
  unsigned char *cPtr;

  cPtr = (unsigned char *)datap;

  // limit count to 16bits for now:
  numWordsToRead = (unsigned int)count & 0xFFFF;
  numBytesToRead = numWordsToRead * 4;

  // where to write the memory address
  unsigned int memFifoRegAddress = 25 << 16;

  // First 32bit word: upper 16 bits = 0xAAAA, lower 8 bits: number of words to follow (3)
  TxIntBuffer[0] = 0xAAAA0001;
  // next command word:	memory count register
  //			TX[31] = 0 : WRITE
  //			TX[27:16] = 12bit register address
  //			TX[15: 0] = 16bit count
  TxIntBuffer[1] = memFifoRegAddress | numWordsToRead;

  // Next 32bit word: switch firmware to read mode
  //			a single 32bit word with upper 16 bits = 0xAAAB,
  //			lower 16 bits: number of 32bit words to read (1)
  TxIntBuffer[2] = 0xAAAB0000 | numWordsToRead;


  // Now send the array
#ifdef _FTD2XX
  ftStatus = FT_Write(fthandle, TxIntBuffer, 12, &BytesWritten);
  if (ftStatus == FT_OK) {
    // FT_Write OK
    if (BytesWritten != 12)
      cerr << "FT_Write wrote " << BytesWritten << " expected 12" << endl;
    }
  else {
    // FT_Write Failed
    cerr << "Write failed with status " << ftStatus << endl;
    return(ftStatus);
  }
#else
  BytesWritten = ftdi_write_data(fthandle, (unsigned char *)TxIntBuffer, 12);
  if (BytesWritten != 12) {
    cerr << "ftdi_write_data returned " << BytesWritten << endl;
    ftStatus = BytesWritten;
    return (ftStatus);
  }
#endif


#ifdef _FTD2XX
  unsigned int EventDWord, TxBytes;
  // wait until some bytes are ready to be read
  FT_GetStatus(fthandle, &RxBytes, &TxBytes, &EventDWord);
  while (RxBytes == 0) {
#ifdef _WIN32
    Sleep(4);
#else
    usleep(4000);
#endif
    FT_GetStatus(fthandle, &RxBytes, &TxBytes, &EventDWord);
  }
#endif
  RxBytes = numBytesToRead;


  // Second: do a FTDI read transaction for the desired bytes
  // This call will block until "expectedBytes" bytes have been received,
  // so only read available bytes
  TotalBytesReceived = 0;
#ifdef _FTD2XX
  ftStatus = FT_Read(fthandle, cPtr, RxBytes, &BytesReceived);
  if (ftStatus == FT_OK) {
    // FT_Read OK
    TotalBytesReceived = BytesReceived;
    wordsReceived = (int)TotalBytesReceived/4;

  }
  else {
    // FT_Read Failed
    cerr << "Read failed with status " << ftStatus << endl;
    return ftStatus;
  }
#else
  ftStatus = ftdi_read_data(fthandle, cPtr, RxBytes);
  if (ftStatus >= 0) { 
    // FT_Read OK 
    BytesReceived = ftStatus;
    if (BytesReceived != RxBytes) {
      cerr << "Read " << ftStatus << " bytes, expected " 
	   << RxBytes << " bytes " << endl;
      // for (int i=0; i<ftStatus; i++) {
      // 	cerr << dec << i << ": " << hex << showbase << (unsigned int)cPtr[i] << endl;
      // }
    }
    else {
      TotalBytesReceived = ftStatus;
      wordsReceived = (int)TotalBytesReceived/4;
    }
  }
  else { 
    // ftdi_read_data Failed 
    cerr << "Read failed with status " << ftStatus << endl;
    cerr << ftdi_get_error_string(fthandle) << endl;
    return ftStatus;
  } 

#endif

  if ((int)TotalBytesReceived == numBytesToRead) return FT_OK;

#ifdef _FTD2XX
  // otherwise check if there are more bytes to read
  cPtr += BytesReceived;
  FT_GetStatus(fthandle, &RxBytes, &TxBytes, &EventDWord);
  if (RxBytes > 0) {
    ftStatus = FT_Read(fthandle, cPtr, RxBytes, &BytesReceived);
    if (ftStatus == FT_OK) {
      // FT_Read OK
      TotalBytesReceived += BytesReceived;
      wordsReceived = (int)TotalBytesReceived/4;
    }
    else {
      // FT_Read Failed
      cerr << "Read failed with status " << ftStatus << endl;
      return ftStatus;
    }
  }
#endif

  return ftStatus;
}
