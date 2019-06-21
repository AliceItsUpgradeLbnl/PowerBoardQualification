#!/usr/bin/env python

from threading import Thread
import pexpect
import os
import base64

absolute_path_origin      = "/home/its/Desktop/PB-production/PB-production/scripts/RESULTS/"  # on this computer
absolute_path_destination = "aliceitslbl@lxplus.cern.ch:/eos/project/a/alice-its/PowerBoard/" # EOS at CERN
eos_transfer_timeout      = 300 # 5 minutes by default
error_msg_recipients      = ["albertocollu@lbl.gov"]

def UploadPbdata(key):
    thread = Thread(target=EosRsync(key))
    thread.daemon = True 
    thread.start()
    thread.join(eos_transfer_timeout)
    if thread.is_alive():
        msg = "Timeout: transfer to CERN EOS exceeded maximum time (" + eos_transfer_timeout + "s), transfer aborted"
        ReportError(msg)

def EosRsync(key):
    try:
        child = pexpect.spawn('rsync -rv --size-only -e "ssh -K" ' + absolute_path_origin + ' ' + absolute_path_destination)
        child.expect('rd:')
        child.sendline(EosAccess(key, "maVnnKhqn6ttWg=="))
        child.expect('sending incremental file list')
        print "Sending incremental file list to CERN EOS..."
        print "Origin: " + absolute_path_origin
        print "Destination: " + absolute_path_destination
        print "Please wait ..."
        child.expect([pexpect.TIMEOUT, 'total size is'])
        child.expect('\n')
        print "Done!"
        child.interact()
    except:
        msg = "Transfer error: system encountered an error while transferring data to CERN EOS, transfer aborted"
        ReportError(msg)

def EosAccess(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

def ReportError(error_msg):
    for email in error_msg_recipients:
        os.system('mail -s "' + error_msg + '" ' + email + ' < ' + absolute_path_origin.split('RESULTS/')[0] + "LargeScaleTest/GuiUtils/FixMeMsg.txt")
    print error_msg

UploadPbdata("0123456789")
