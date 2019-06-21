#!/usr/bin/env python

from threading import Thread
import pexpect
import os
import base64

absolute_path_origin      = "/home/its/Desktop/PB-production/PB-production/scripts/LargeScaleTest/GuiUtils/"  # on this computer
kerberos_timeout          = 10000 # 20 seconds
error_msg_recipients      = ["albertocollu@lbl.gov"]

def AttemptGenerateKerberosTicket(key = '0123456789'):
    thread = Thread(target=GenerateKerberosTicket(key))
    thread.daemon = True 
    thread.start()
    thread.join(kerberos_timeout)
    if thread.is_alive():
        msg = "Timeout: renewal of Kerberos ticket not possible (" + kerberos_timeout + "s)"
        ReportError(msg)
        return False
    return True

def GenerateKerberosTicket(key):
    try:
        child = pexpect.spawn('kinit aliceitslbl')
        child.expect('CERN.CH:')
        child.sendline(KerberosAccess(key, "maVnnKhqn6ttWg=="))
        print "Done ticket generation!"
        child.expect('\n')
    except:
        msg = "Authentication error: system encountered an error while authenticating into Kerberos"
        ReportError(msg)

def KerberosAccess(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

def ReportError(error_msg):
    for email in error_msg_recipients:
        os.system('mail -s "' + error_msg + '" ' + email + ' < ' + absolute_path_origin + "KerberosTicketGeneratorMsg.txt")
    print error_msg


if __name__ == '__main__':
    AttemptGenerateKerberosTicket()
