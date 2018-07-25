// C++ includes
#include <iostream>
#include <fstream>
#include <iomanip>
using namespace std;

#ifdef _FTD2XX
#ifdef _WIN32
#include <windows.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

// FTDI D2xx include
#include "ftd2xx.h"

#else
#include <stdlib.h>
#include <string.h>
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

// external functions
extern FT_STATUS open_ftdi(const char *, FT_HANDLE *);
extern FT_STATUS close_ftdi(FT_HANDLE *);
extern FT_STATUS writeReg(FT_HANDLE, unsigned short, unsigned short, unsigned int &);
extern FT_STATUS readReg(FT_HANDLE, unsigned short, unsigned long long &);
extern FT_STATUS SendPacket(FT_HANDLE, unsigned int, unsigned int[], unsigned int, unsigned int[]);
extern FT_STATUS writeMem(FT_HANDLE, unsigned short, unsigned int *, int);
extern FT_STATUS readMem(FT_HANDLE, unsigned short, unsigned int *, int, int &);
extern FT_STATUS readFifo(FT_HANDLE, unsigned int *, int, int &);
extern FT_STATUS readFifo32(FT_HANDLE, unsigned int, unsigned int *);

//const int NUM_MEMORY_IO = 511;
const int NUM_MEMORY_IO = 65535;
const unsigned int FIRMWARE_TRAILER = 0xCAFEFEED;

int main(int argc, char *argv[])
{
  FT_HANDLE ftdi = (FT_HANDLE)NULL;
  FT_STATUS ftStatus;
  char serial[16];
  unsigned short data;
  unsigned int dataW, trailerW;
  unsigned long long dataLongW;
  int count;
  //unsigned int dd;
  unsigned short address;
  unsigned short memAddrStart;
  bool bRead, bFill, bClear, bMemRead, bFifoRead;
  unsigned int *TxIntBuf = new unsigned int[NUM_MEMORY_IO];
  unsigned int *RxIntBuf = new unsigned int[NUM_MEMORY_IO];
  int fillCount, wordsReceived;

  // set defaults
  // the "A" at the end of the serial number specifies "Port A" of the module
#ifdef _FTD2XX
  strcpy(serial, "FTWWH5BOA"); // module at UT
#else
  //strcpy(serial, "FTWWH5BO"); // module at UT
  strcpy(serial, "FTWWEJH9"); // module at IPHC
#endif
  count = 1;
  address = 0;
  data = 0;
  bRead = true;
  bFill = bClear = bMemRead = bFifoRead = false;
  fillCount = 511;
  memAddrStart = 0;

  // parse command line arguments
  while (count < argc) {
    if(strcasecmp(argv[count],"-r") == 0) {
      //cout << "found -r argument\n";
      bRead = true;
    }
    else if(strcasecmp(argv[count],"-w") == 0) {
      //cout << "found -w argument\n";
      bRead = false;
    }
    else if(strcasecmp(argv[count],"-j") == 0) {
      ifstream conf;
      conf.open(argv[++count]); // "in" is default
      if ( !conf.good() ) {
	cerr << argv[count] << ": file error\n";
	return -1;
      }
      fillCount = 0;
      conf >> hex; // hex numbers
      while (conf.good()) {
	conf >> hex >> TxIntBuf[fillCount];
	if (conf.eof()) break;
	fillCount++;
      }
      conf.close();
      // cout << "found " << fillCount << " hex numbers:" << endl;
      // for (int i=0; i<fillCount; i++) {
      // 	cout << dec << i << ": " << hex << showbase << TxIntBuf[i] << endl;
      // }
      bFill = true;
    }
    else if(strcasecmp(argv[count],"-s") == 0) {
      //cout << "found -s argument\n";
      memAddrStart = (unsigned short)strtol(argv[++count], (char **)NULL,0);
    }
    else if(strcasecmp(argv[count],"-f") == 0) {
      //cout << "found -f argument\n";
      bFill = true;
      fillCount = (int)strtol(argv[++count], (char **)NULL,0);
      if(fillCount > NUM_MEMORY_IO) {
	cerr << "Max memory size is currently " << NUM_MEMORY_IO << endl;
	return 0;
      }
      for(int i=0; i<fillCount; i++) TxIntBuf[i] = 0xA0000000 + i;
    }
    else if(strcasecmp(argv[count],"-m") == 0) {
      //cout << "found -m argument\n";
      bMemRead = true;
      fillCount = (int)strtol(argv[++count], (char **)NULL,0);
      if(fillCount > NUM_MEMORY_IO) {
	cerr << "Max memory size is currently " << NUM_MEMORY_IO << endl;
	return 0;
      }
    }
    else if(strcasecmp(argv[count],"-u") == 0) {
      //cout << "found -m argument\n";
      bFifoRead = true;
      fillCount = (int)strtol(argv[++count], (char **)NULL,0);
      if(fillCount > NUM_MEMORY_IO) {
	cerr << "Max memory size is currently " << NUM_MEMORY_IO << endl;
	return 0;
      }
    }
    else if(strcasecmp(argv[count],"-c") == 0) {
      //cout << "found -c argument\n";
      bClear = true;
      fillCount = (int)strtol(argv[++count], (char **)NULL,0);
      if(fillCount > NUM_MEMORY_IO) {
	cerr << "Max memory size is currently " << NUM_MEMORY_IO << endl;
	return 0;
      }
      for(int i=0; i<fillCount; i++) TxIntBuf[i] = 0;
    }
    else if(strcasecmp(argv[count],"-a") == 0) {
      //cout << "found -a argument\n";
      address = (unsigned short)(strtol(argv[++count], (char **)NULL,0) & 0xFFF);

    }
    else if(strcasecmp(argv[count],"-d") == 0) {
      //cout << "found -d argument\n";
      data = (unsigned short)strtol(argv[++count], (char **)NULL,0);

    }
    else if(strcasecmp(argv[count],"--reset") == 0) {
      unsigned char dummy = 'F';
      unsigned int BytesWritten;
#ifdef _FTD2XX
      ftStatus = open_ftdi(serial, &ftdi);
      if (ftStatus != FT_OK) {
	cout << "open_ftdi returned " << ftStatus << endl;
	return 0;
      }
      ftStatus = FT_Write(ftdi, (void *)&dummy, 1, &BytesWritten);
      if (ftStatus == FT_OK) {
	// FT_Write OK
	if (BytesWritten != 1)
	  cerr << "FT_Write wrote " << BytesWritten << " expected 1" << endl;
      }
      else {
	// FT_Write Failed
	cerr << "Write failed with status " << ftStatus << endl;
      }
#else
      if ((ftdi = ftdi_new()) == (ftdi_context *)NULL) {
	cerr << "ftdi_new failed" << endl;
	return -1;
      }

      ftdi_set_interface(ftdi, INTERFACE_B);
      // open a device with a specific serial number (second to last argument to open)
      // with index 1 (last argument to open)
      if ((ftStatus = ftdi_usb_open_desc(ftdi, 0x0403, 0x6010, NULL, serial)) < 0) {
	cerr << "opening device with serial " << serial << " failed with error " << ftStatus << endl; 
	cerr << ftdi_get_error_string(ftdi) << endl;
	ftdi_free(ftdi);
	return -1;
      }
      BytesWritten = ftdi_write_data(ftdi, &dummy, 1);
      if (BytesWritten != 1) {
	cerr << "ftdi_write_data returned " << BytesWritten << endl;
      }

#endif
      ftStatus = close_ftdi(&ftdi);
      if(ftStatus != FT_OK)
	cout << "close_ftdi returned " << ftStatus << endl;
      return 0;
    }
    else if(strcasecmp(argv[count],"--serial") == 0) {
      //cout << "found --serial argument\n";
      strcpy(serial, argv[++count]);
    }
    else {
      cout << "invalid argument " << argv[count] << endl;
    }
    count++;
  }

  ftStatus = open_ftdi(serial, &ftdi);
  if (ftStatus != FT_OK) {
    cout << "open_ftdi returned " << ftStatus << endl;
    return 0;
  }

  if (bFill) { // ....Fill Memory....
    cout << "Writing " << fillCount << " words of the memory" << endl;
    ftStatus = writeMem(ftdi, memAddrStart, TxIntBuf, fillCount);
    if (ftStatus != FT_OK)
      cout << "writeMem returned " << (unsigned int)ftStatus << endl;
  }
  else if (bClear) { // ....Clearing Memory....
    cout << "Clearing " << fillCount << " words of the memory" << endl;
    ftStatus = writeMem(ftdi, memAddrStart, TxIntBuf, fillCount);
    if (ftStatus != FT_OK)
      cout << "writeMem returned " << ftStatus << endl;
  }
  else if (bMemRead) { // ....Reading Memory....
    for(int i=0; i<fillCount; i++) RxIntBuf[i] = 0;
    cout << "Reading " << fillCount << " words of the memory" << endl;
    ftStatus = readMem(ftdi, memAddrStart, RxIntBuf, fillCount, wordsReceived);
    cout << "readMem returned " << (unsigned int)ftStatus << ", read words: " << wordsReceived << endl;
    if(ftStatus == FT_OK) {
      //cout << "Press return to print and check the received data" << endl;
      //getchar();
      //cout << endl;
      ofstream ofs ("jtag_r.dat", ofstream::out|ofstream::trunc);
      // check the received data
      // expect it to come from the above fill memory routine
      bool notmonotone = false;
      //cout << "0: 0x" << hex << setw(8) << setfill('0') << RxIntBuf[0] << endl;
      ofs << "0x" << hex << setw(8) << setfill('0') << RxIntBuf[0] << endl;
      for (int i=1; i<fillCount; i++) {
    	//cout << dec << i << ": 0x" << hex << setw(8) << setfill('0') << RxIntBuf[i] << endl;
	ofs << "0x" << hex << setw(8) << setfill('0') << RxIntBuf[i] << endl;
    	//if(RxIntBuf[i] != (RxIntBuf[i-1]+1)) notmonotone = true;
      }
      ofs.close();
      if (notmonotone) cerr << " not monotone" << endl;

    }
  }
  else if (bFifoRead) { // ....Reading Fifo....
    for(int i=0; i<fillCount; i++) RxIntBuf[i] = 0;
    cout << "Reading " << fillCount << " words from Fifo" << endl;
    ftStatus = readFifo(ftdi, RxIntBuf, fillCount, wordsReceived);
    cout << "readFifo returned " << (unsigned int)ftStatus << ", read words: " << wordsReceived << endl;
    if(ftStatus == FT_OK) {
      //cout << "Press return to print and check the received data" << endl;
      //getchar();
      //cout << endl;
      //ofstream ofs ("fifo.dat", ofstream::out|ofstream::trunc);
      ofstream ofs ("fifo.dat", ofstream::out|ofstream::trunc|ios::binary);
      // check the received data
      // expect it to come from the above fill memory routine
      bool notmonotone = false;
      //cout << "0: 0x" << hex << setw(8) << setfill('0') << RxIntBuf[0] << endl;
      //ofs << "0x" << hex << setw(8) << setfill('0') << RxIntBuf[0] << endl;
      ofs.write((char*)&RxIntBuf[0],4);
      for (int i=1; i<fillCount; i++) {
    	//cout << dec << i << ": 0x" << hex << setw(8) << setfill('0') << RxIntBuf[i] << endl;
	//ofs << "0x" << hex << setw(8) << setfill('0') << RxIntBuf[i] << endl;
        ofs.write((char*)&RxIntBuf[i],4);
    	//if(RxIntBuf[i] != (RxIntBuf[i-1]+1)) notmonotone = true;
      }
      ofs.close();
      if (notmonotone) cerr << " not monotone" << endl;

    }
  }
  else if (bRead) { // ....READING....
    cout << "Reading register at address " << hex << showbase << address << endl;
    ftStatus = readReg(ftdi, address, dataLongW);
    dataW = (unsigned int) (dataLongW & 0x00000000FFFFFFFF);
    trailerW = (unsigned int) ((dataLongW >> 32) & 0x00000000FFFFFFFF);
    if (trailerW != FIRMWARE_TRAILER)
      cout << "Wrong trailer while attempting to read from firmware register. Received: " << trailerW << " Expected: " << FIRMWARE_TRAILER << endl;
    cout << "readReg returned " << ftStatus << ", data = " << hex << showbase << dataW << endl;
  }  
  else { // ....WRITING.....
    cout << "Writing " << hex << showbase << data << " to register at address " << address << endl;
    ftStatus = writeReg(ftdi, address, data, trailerW);
    if (ftStatus != FT_OK)
      cout << "writeReg returned " << ftStatus << endl;
//    if (trailer != FIRMWARE_TRAILER)
    if (trailerW != FIRMWARE_TRAILER)
      cout << "Wrong trailer while attempting to write to firmware register. Received: " << trailerW << " Expected: " << FIRMWARE_TRAILER << endl;
  }


  // close device again
  ftStatus = close_ftdi(&ftdi);
  if(ftStatus != FT_OK)
    cout << "close_ftdi returned " << ftStatus << endl;

  delete TxIntBuf;

  return 0;
}
