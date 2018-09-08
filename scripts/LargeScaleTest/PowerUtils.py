#!/usr/bin/env python

import socket
import sys
import time
import fcntl
import os
import errno

BUFFER_SIZE = 1024
TCP_IP = ['131.243.30.214', '131.243.30.215']
TCP_PORT = 8003

def read_status_TDK(tdk_id):
    if tdk_id < 0 or tdk_id > 1:
        return

    MESSAGE = 'OUTP:STAT?'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP[tdk_id], TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()
    wait()
    return data[0:-1]

def set_status_TDK(tdk_id, tdk_status):
    if tdk_id < 0 or tdk_id > 1:
        return
    if tdk_status != "ON" and tdk_status != "OFF":
        return

    MESSAGE = 'OUTP:STAT ' + tdk_status
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP[tdk_id], TCP_PORT))
    fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK)
    s.send(MESSAGE)
    try:
        data = s.recv(BUFFER_SIZE)
    except socket.error, e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            pass
        else:
            print "An error occurred when trying to turn TDK output " + tdk_status + ". Errorcode is " + e
            print "Received error data:", data
            sys.exit(1)

    s.close()
    wait()

def set_volt_TDK(tdk_id, voltage):
    if tdk_id < 0 or tdk_id > 1:
        return

    VINT = int(voltage)
    VDEC = voltage - VINT
    VDEC = int(VDEC*100 + 0.1)
    MESSAGE = ':VOLT ' + str(VINT) + "." + str(VDEC)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP[tdk_id], TCP_PORT))
    fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK)
    s.send(MESSAGE)
    try:
        data = s.recv(BUFFER_SIZE)
    except socket.error, e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            pass
        else:
            print "An error occurred when trying to turn TDK output " + tdk_status + ". Errorcode is " + e
            print "Received error data:", data
            sys.exit(1)

    s.close()
    wait()

def read_volt_TDK(tdk_id):
    if tdk_id < 0 or tdk_id > 1:
        return

    MESSAGE = 'MEAS:VOLT?'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP[tdk_id], TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()
    wait()

    return data

def read_curr_TDK(tdk_id):
    if tdk_id < 0 or tdk_id > 1:
        return

    MESSAGE = 'MEAS:CURR?'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP[tdk_id], TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()
    wait()

    return data

def switchcontrol_TDK(tdk_id, control_type):
    if tdk_id < 0 or tdk_id > 1:
        return
    if control_type != "LOC" and control_type != "REM":
        return

    MESSAGE = 'SYST:SET ' + control_type
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP[tdk_id], TCP_PORT))
    s.send(MESSAGE)
    s.close()
    wait()

def wait():
    time.sleep(0.2)
