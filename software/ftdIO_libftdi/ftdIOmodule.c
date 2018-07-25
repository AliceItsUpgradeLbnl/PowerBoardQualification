#include </usr/include/python2.6/Python.h>
//#include <Python.h>

#define _FTD2XX

#ifdef _FTD2XX
#include "ftd2xx.h"
#else
#include <ftdi.h>

typedef struct ftdi_context * FT_HANDLE;

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

static FT_HANDLE _myFtdi = (FT_HANDLE)NULL;

FT_STATUS _open_ftdi(const char *, FT_HANDLE *);
FT_STATUS _close_ftdi(FT_HANDLE *);
FT_STATUS _writeReg(FT_HANDLE, unsigned short, unsigned short, unsigned int*);
FT_STATUS _readReg(FT_HANDLE, unsigned short, unsigned long long*);
FT_STATUS _sendPacket(FT_HANDLE, unsigned int, unsigned int[], unsigned int, unsigned int[]);

const int NUM_MEMORY_IO = 65535;
const unsigned int FIRMWARE_TRAILER_MSP = 0xCAFE;

static PyObject* open_ftdi(PyObject* self, PyObject* args)
{
  const char* serial;
  FT_STATUS ftStatus;
  
  if (!PyArg_ParseTuple(args, "s", &serial))
    return NULL;
  
  if (_myFtdi != (FT_HANDLE)NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Device already open");
    return NULL;
  }

  ftStatus = _open_ftdi(serial, &_myFtdi);
  if (ftStatus != FT_OK) {
    fprintf(stderr, "open_ftdi failed with status %d\n", ftStatus);
    PyErr_SetString(PyExc_NameError, "Could not open device with this serial number");
    return NULL;
  }

  Py_RETURN_NONE;
}
 
static PyObject* close_ftdi(PyObject* self, PyObject* args)
{
  FT_STATUS ftStatus;
  
  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  
  ftStatus = _close_ftdi(&_myFtdi);
  if (ftStatus != FT_OK) {
    fprintf(stderr, "close_ftdi failed with status %d\n", ftStatus);
    PyErr_SetString(PyExc_RuntimeError, "Could not close device");
    return NULL;
  }
  
  Py_RETURN_NONE;
}
 
static PyObject* readReg(PyObject* self, PyObject* args)
{
  unsigned short      address;
  unsigned long long  data;
  unsigned int        dataW, trailerW;

  FT_STATUS ftStatus;
  
  if (!PyArg_ParseTuple(args, "H", &address))
    return NULL;
  
  ftStatus = _readReg(_myFtdi, address, &data);
  dataW = (unsigned int) (data & 0x00000000FFFFFFFF);
  trailerW = (unsigned int) ((data >> 32) & 0x00000000FFFFFFFF);
  if (ftStatus != FT_OK) {
    fprintf(stderr, "readReg failed with status %d\n", ftStatus);
    PyErr_SetString(PyExc_IOError, "readReg failed");
    return NULL;
  }
  if (trailerW>>16 != FIRMWARE_TRAILER_MSP)
    fprintf(stderr, "Wrong trailer while attempting to read from firmware register. Received: %X Expected: %X%s", trailerW, FIRMWARE_TRAILER_MSP<<16, "XXXX");
 
  return Py_BuildValue("i", dataW);
}

static PyObject* writeReg(PyObject* self, PyObject* args)
{
  unsigned short address;
  unsigned short data;
  unsigned int   trailerW;
  FT_STATUS ftStatus;
  
  if (!PyArg_ParseTuple(args, "HH", &address, &data))
    return NULL;
  
  ftStatus = _writeReg(_myFtdi, address, data, &trailerW);
  if (ftStatus != FT_OK) {
    fprintf(stderr, "writeReg returned %d\n", ftStatus);
    PyErr_SetString(PyExc_IOError, "writeReg failed");
    return NULL;
  }
  if (trailerW>>16 != FIRMWARE_TRAILER_MSP)
    fprintf(stderr, "Wrong trailer while attempting to read from firmware register. Received: %X Expected: %X%s", trailerW, FIRMWARE_TRAILER_MSP<<16, "XXXX");
 
  Py_RETURN_NONE;
}

static PyObject* sendPacket(PyObject* self, PyObject* args)
{
  
  PyObject *inputBuffer; // = PyList_New(10000);
  PyObject *outputBuffer; //= PyList_New(10000);

  if (!PyArg_ParseTuple(args, "OO", &inputBuffer, &outputBuffer))
    return NULL;

  unsigned int inBuffer[10000];
  unsigned int outBuffer[10000];
  unsigned int i;
  PyObject * extracted;

  unsigned int inputBufferSize = PyList_Size(inputBuffer);
  if (inputBufferSize) {
    for (i = 0; i < inputBufferSize; i++) {
      extracted = PyObject_GetItem(inputBuffer, PyLong_FromUnsignedLong(i));
      const char* s = PyString_AsString(extracted);
      inBuffer[i] = atoi(s);
    }
  }

  unsigned int outputBufferSize = PyList_Size(outputBuffer);
  FT_STATUS ftStatus;
  ftStatus = _sendPacket(_myFtdi, inputBufferSize, inBuffer, outputBufferSize, outBuffer);
  if (ftStatus != FT_OK) {
    fprintf(stderr, "sendPacket returned %d\n", ftStatus);
    PyErr_SetString(PyExc_IOError, "sendPacket failed");
    return NULL;
  }

  if (outputBufferSize) {
    for (i = 0; i < outputBufferSize; i++) {
      PyObject_SetItem(outputBuffer, PyLong_FromUnsignedLong(i), PyLong_FromUnsignedLong(outBuffer[i]));
    }
  }

  Py_RETURN_NONE;
}

static PyMethodDef FtdIOmoduleMethods[] =
{
  {"open_ftdi", open_ftdi, METH_VARARGS, "Open FTDI device by serial number."},
  {"close_ftdi", close_ftdi, METH_VARARGS, "Close FTDI device if open."},
  {"readReg", readReg, METH_VARARGS, "Returns register content at given address."},
  {"writeReg", writeReg, METH_VARARGS, "Writes to register at given address."},
  {"sendPacket", sendPacket, METH_VARARGS, "Sends a command packet and returns the data read out."},
  {NULL, NULL, 0, NULL}
};
 
PyMODINIT_FUNC
 
initftdIOmodule(void)
{
  (void) Py_InitModule("ftdIOmodule", FtdIOmoduleMethods);
}

FT_STATUS _open_ftdi(const char *serial, FT_HANDLE *fthandle)
{
  int retval;
  unsigned char Mode, Mask, LatencyTimer;

  // open a device with a specific serial number (last argument to open)
#ifdef _FTD2XX
  if ((retval = FT_OpenEx((PVOID)serial, FT_OPEN_BY_SERIAL_NUMBER, fthandle)) != FT_OK) {
    //
    fprintf(stderr, "opening device with serial %s failed with error %i\n", serial, retval);
    return retval;
  }
#else
  if ((*fthandle = ftdi_new()) == (FT_HANDLE)NULL) {
    fprintf(stderr, "ftdi_new failed\n");
    return -1;
  }

  // open a device with a specific serial number (last argument to open)
  if ((retval = ftdi_usb_open_desc(*fthandle, 0x0403, 0x6010, NULL, serial)) < 0) {
    fprintf(stderr, "opening device with serial %s failed with error %i\n", serial, retval);
    fprintf(stderr, "%s\n", ftdi_get_error_string(*fthandle));
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

FT_STATUS _close_ftdi(FT_HANDLE *fthandle)
{
  int retval = FT_OK;
  if (*fthandle != (FT_HANDLE)NULL) {
#ifdef _FTD2XX
    if ((retval = FT_Close(*fthandle)) == FT_OK)
      *fthandle = (FT_HANDLE)NULL;
    else
      fprintf(stderr, "unable to close ftdi device: error %i\n", retval);
#else
    if ((retval = ftdi_usb_close(*fthandle)) < 0) {
      fprintf(stderr, "unable to close ftdi device: error %i\n", retval);
      fprintf(stderr, "%s\n", ftdi_get_error_string(*fthandle));
    }

    ftdi_free(*fthandle);
#endif
  }
  return retval;
}

FT_STATUS _writeReg(FT_HANDLE fthandle, unsigned short address, unsigned short data, unsigned int *trailer)
{
  unsigned int TxIntBuffer[3];

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
  unsigned int SizeOfBufferedData; // This should be zero at the beginning of an operation
  FT_GetQueueStatus(fthandle, &SizeOfBufferedData);
  if (SizeOfBufferedData != 0) {
    printf("Data was found in the FTDI output buffer before a transaction was initiated. Data size is: %d.\n", SizeOfBufferedData);
    exit(EXIT_FAILURE);
  }

  int ftStatus;
  unsigned int BytesWritten;
  ftStatus = FT_Write(fthandle, TxIntBuffer, 12, &BytesWritten);
  if (ftStatus == FT_OK) {
    // FT_Write OK
    if (BytesWritten != 12)
      printf("FT_Write wrote %u, expected 12\n", BytesWritten);
  }
  else {
    // FT_Write Failed
    printf("Write failed with status %i\n", ftStatus);
    return(ftStatus);
  }

#else
  BytesWritten = ftdi_write_data(fthandle, (unsigned char *)TxIntBuffer, 12);
  if (BytesWritten != 12) {
    printf("ftdi_write_data returned %u\n", BytesWritten);
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
      printf("Read %u trailer bytes out of 4:\n", BytesReceived);
      int i;
      for (i = 0; i < (int)BytesReceived; i++)
        printf("%i: %X", i, (unsigned int)RxBuffer[i]);
    }
  }
  else {
    // FT_Read Failed
    printf("Read trailer failed with status %i\n", ftStatus); 
  }

#else
  ftStatus = ftdi_read_data(fthandle, RxBuffer, 4);
  if (ftStatus == 4) { 
    // FT_Read OK 
    ftStatus = FT_OK;
  }
  else { 
    // ftdi_read_data Failed 
    printf("Read trailer failed with status  %d", ftStatus);
//    cerr << ftdi_get_error_string(fthandle) << endl;
  } 
#endif

   return(ftStatus);
}

FT_STATUS _readReg(FT_HANDLE fthandle, unsigned short address, unsigned long long *data)
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
  unsigned int SizeOfBufferedData; // This should be zero at the beginning of an operation
  FT_GetQueueStatus(fthandle, &SizeOfBufferedData);
  if (SizeOfBufferedData != 0) {
    printf("Data was found in the FTDI output buffer before a transaction was initiated. Data size is: %d.\n", SizeOfBufferedData);
    exit(EXIT_FAILURE);
  }

  ftStatus = FT_Write(fthandle, TxIntBuffer, 12, &BytesWritten);
  if (ftStatus == FT_OK) {
    // FT_Write OK
    if (BytesWritten != 12)
      printf("FT_Write wrote %d, expected 12\n", BytesWritten);
    }
  else {
    // FT_Write Failed
    printf("Write address failed with status %i\n", ftStatus);
    return(ftStatus); 
  }
#else
  BytesWritten = ftdi_write_data(fthandle, (unsigned char *)TxIntBuffer, 12);
  if (BytesWritten != 12) {
    printf("ftdi_write_data returned %d", BytesWritten);
    ftStatus = BytesWritten;
    return (ftStatus);
  }
#endif

  unsigned char *RxBuffer = (unsigned char *)data;

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
      printf("Read %i bytes:\n", BytesReceived);
      int i;
      for (i = 0; i < (int)BytesReceived; i++)
        printf("%i: %u\n", i, (unsigned int)RxBuffer[i]);
    }
  }
  else {
    // FT_Read Failed
    printf("Read failed with status %i\n", ftStatus);
    
  }

#else
  ftStatus = ftdi_read_data(fthandle, RxBuffer, 8);
  if (ftStatus == 8) { 
    // FT_Read OK 
    ftStatus = FT_OK;
  }
  else { 
    // ftdi_read_data Failed 
    printf("Read failed with status %d", ftStatus);
  } 
#endif

  return(ftStatus);
}

FT_STATUS _sendPacket(FT_HANDLE fthandle, unsigned int numWordsToWrite, unsigned int writeDataBuffer[], unsigned int numWordsToRead, unsigned int readDataBuffer[])
{
  int ftStatus;
  unsigned int TxIntBuffer[numWordsToWrite + 2]; // Must include header and trailer 

  // Limit num of words to write and read to a 16-bit integer for now:
  numWordsToWrite = numWordsToWrite & 0xFFFF;
  numWordsToRead  = numWordsToRead  & 0xFFFF;

  // Creating a buffer with the input data + header and trailer
  TxIntBuffer[0] = 0xAAAA0000 | numWordsToWrite;
  int i = 0;
  for (i = 0; i < numWordsToWrite; ++i)
  {
    TxIntBuffer[i + 1] = writeDataBuffer[i];
  }
  TxIntBuffer[numWordsToWrite + 1] = 0xAAAB0000 | (numWordsToRead + 1);

  // Calculating total packet bytes (to write and to read, with header and trailer)
  unsigned int totalNumBytesToWrite = numWordsToWrite*4 + 8;
  unsigned int totalNumBytesToRead  = numWordsToRead*4  + 4;

  unsigned int BytesWritten;

  // Now send the array
#ifdef _FTD2XX
  unsigned int SizeOfBufferedData; // This should be zero at the beginning of an operation
  FT_GetQueueStatus(fthandle, &SizeOfBufferedData);
  if (SizeOfBufferedData != 0) {
    printf("Data was found in the FTDI output buffer before a transaction was initiated. Data size is: %d.\n", SizeOfBufferedData);
    exit(EXIT_FAILURE);
  }

  ftStatus = FT_Write(fthandle, TxIntBuffer, totalNumBytesToWrite, &BytesWritten);
  if (ftStatus == FT_OK) {
    // FT_Write OK
    if (BytesWritten != totalNumBytesToWrite)
      printf("FT_Write wrote %i, expected %i", BytesWritten, totalNumBytesToWrite);
    }
  else {
    // FT_Write Failed
    printf("Write command packet failed with status %i\n", ftStatus);
    return(ftStatus);
  }
#else
  BytesWritten = ftdi_write_data(fthandle, (unsigned char *)TxIntBuffer, totalNumBytesToWrite);
  if (BytesWritten != totalNumBytesToWrite) {
    printf("ftdi_write_data returned %d", BytesWritten);
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
  int timeoutSetting = 2500;
  int timeout = timeoutSetting;
  FT_GetQueueStatus(fthandle, &RxBytes);
  while (RxBytes != totalNumBytesToRead && timeout-- > 0) {
#ifdef _WIN32
    Sleep(4);
#else
    usleep(4000);
#endif
    FT_GetQueueStatus(fthandle, &RxBytes);
  }
  
  if (timeout < 0){
    printf("Timeout! Timeout is presently set to %f seconds.\n", ((float) timeoutSetting)*4/1000);
    exit(EXIT_FAILURE); 
  }

  // This should not happen
  if (RxBytes != totalNumBytesToRead) return (FT_OTHER_ERROR);
  // This call will block until "expectedBytes" bytes have been received
  ftStatus = FT_Read(fthandle, RxBuffer, totalNumBytesToRead, &BytesReceived);
  if (ftStatus == FT_OK) {
    // FT_Read OK
    if (BytesReceived != totalNumBytesToRead) {
      printf("Read %i bytes:\n", BytesReceived);
      int i;
      for (i = 0; i < (int)BytesReceived; i++)
        printf("%i: %u", i, (unsigned int)RxBuffer[i]);
    }
  }
  else {
    // FT_Read Failed
    printf("Read data output from command packet failed with status %i\n", ftStatus);
  }

#else
  ftStatus = ftdi_read_data(fthandle, RxBuffer, totalNumBytesToRead);
  if (ftStatus == (int) totalNumBytesToRead) { 
    // FT_Read OK 
    ftStatus = FT_OK;
  }
  else { 
    // ftdi_read_data Failed 
    printf("Read data output from command packet failed with status %d. Number of bytes received is wrong.\n", ftStatus);
    //cerr << ftdi_get_error_string(fthandle) << endl;
  } 
#endif

  if (readDataBuffer[numWordsToRead]>>16 != FIRMWARE_TRAILER_MSP) {
    printf("Firmware trailer error: Expected %X%s, Received %X.\n", FIRMWARE_TRAILER_MSP<<16, "XXXX",readDataBuffer[numWordsToRead]);
    PyErr_SetString(PyExc_IOError, "Firmware trailer readout failed (unrecognized firmware trailer)");
    exit(EXIT_FAILURE);
  }
 
  if (readDataBuffer[numWordsToRead] & 0xFFFF) {
    printf("Last firmware operation encountered an error. Error count is %d.\n", readDataBuffer[numWordsToRead] & 0xFFFF);
    PyErr_SetString(PyExc_IOError, "Firmware trailer readout failed (error counter is wrong)");
    exit(EXIT_FAILURE);
  }

   return(ftStatus);
}

