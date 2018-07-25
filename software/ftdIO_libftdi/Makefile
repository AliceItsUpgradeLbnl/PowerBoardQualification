CC = g++
INCPATH = -I/home/its/libftdi/libftdi/src -I.
LIBS 	= -L/usr/local/lib64 -lftdi1
LFLAGS	= -O2 -m64 -Wl,-rpath,/usr/local/lib64 -fPIC

LDFLAGS += $(LFLAGS) $(LIBS)

CFLAGS += -m64 -Wall $(INCPATH)
CXXFLAGS += -O2 -Wall -m64 $(INCPATH)

all: ftdIO

find_all: find_all.o

ftdIO: ftdIO.o ftdi_utils.o

