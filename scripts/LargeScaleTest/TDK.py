!/usr/bin/env python
__author__ = "G.Contin"
__version__ = "1.0"
__status__ = "Prototype"

import socket
import sys

def read_status_TDK1():

    TCP_1 = '131.243.31.12'
    TCP_PORT = 8003
    BUFFER_SIZE = 1024
    MESSAGE = 'OUTP:STAT?'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()
    print "received data:", data


def set_Volt_TDK1():

    TCP_1 = '131.243.31.12'
    TCP_PORT = 8003
    BUFFER_SIZE = 1024
    MESSAGE = 'OUTP:STAT?'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()

    print "received data:", data

def read_Volt_TDK1():

    TCP_1 = '131.243.31.12'
    TCP_PORT = 8003
    BUFFER_SIZE = 1024
    MESSAGE = 'VOLT?'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()

    print "received data:", data
