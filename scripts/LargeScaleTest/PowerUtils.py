#!/usr/bin/python

import socket
import sys

def GetIpAddress(PowerUnitID):
    if PowerUnitID == "Right":
        return '131.243.31.12'
    elif PowerUnitID == "Left":
        return '131.243.31.12'

def ReadStatusTdk(PowerUnitID):

    TCP_1 = GetIpAddress(PowerUnitID)
    TCP_PORT = 8003
    BUFFER_SIZE = 1024
    MESSAGE = 'OUTP:STAT?'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()
    print "received data:", data


def SetVoltageTdk(PowerUnitID):

    TCP_1 = GetIpAddress(PowerUnitID)
    TCP_PORT = 8003
    BUFFER_SIZE = 1024
    MESSAGE = 'OUTP:STAT?'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()
    print "received data:", data

def ReadVoltageTdk(PowerUnitID):

    TCP_1 = GetIpAddress(PowerUnitID)
    TCP_PORT = 8003
    BUFFER_SIZE = 1024
    MESSAGE = 'VOLT?'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()
    print "received data:", data

def PowerCyclePowerUnit():
    pass
