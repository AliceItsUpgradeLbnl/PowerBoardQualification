#!/usr/bin/env python
__author__ = "M.Arratia"
__version__ = "2.0"
__status__ = "Prototype"


###work in progress###, 03/23/17
from UsefulFunctions import *



def BiasVoltageScan(output,channel, step):
    OpenFtdi() # Starts communication with RDO board
    start = 255
    end = 0
    startime = time.strftime("%Y%m%d%H%M%S") #Setting timestamp format 
    t1 = datetime.datetime.now() #Getting timestamp
    print t1
    print ' The voltage scan step is %d [DAC]' %(step)
    print ' The channel to be tested is #%d'%(channel)
    EnableBias(channel)
    for voltage in range(start, end , -1*step):
        SetVoltage(channel,voltage)
        with open(output,"ab") as f:
            f.write(str(line) + "\n")
 	########end of loop over voltage###############   
    ShutDownBias()
    print 'end of BIAS voltage scan for channel %d' %(channel)
    print '################################################## \n'	
    CloseFtdi() # Ends communication with RDO board
    return
