#!/usr/bin/env python
__author__ = "M.Arratia"
__version__ = "2.0"
__status__ = "Prototype"


###work in progress###, 03/23/17
from UsefulFunctions import *



def VoltageScan(output, master, channel, step):
    start = 255
    end = 0
    startime = time.strftime("%Y-%m-%d_%H-%M-%S") #Setting timestamp format 
    t1 = datetime.datetime.now() #Getting timestamp
    print t1
    print ' The voltage scan step is %d [DAC]' %(step)
    print ' The channel to be tested is #%d'%(channel)

    RaiseThresholdsToMax()
    'Latch status is ' , PrintLatchStatus(master)
    Unlatch(master, channel)
    AddressConfigRegADC(master) #this is necessary to be able to read ADCs
    sleep(0.1)
    for voltage in range(start, end , -1*step):
        SetVoltage(master, channel,voltage) 
	print '----------Reading I,V---------- ' 
        I, V, I_ADC, V_ADC = ReadADC(master) #read current and voltage from ADCs (before setting new threshold)
        Iread = Vread = 0                   
        #Looping over channels, printing the saved currents and voltages. These are the last ones before latch occurred
        Vread = V[channel]
        Iread = I[channel]
        #print 'Voltage' , Vread , ' current ' , Iread
	rload = -1
	if(Iread>0): rload = Vread/Iread
        Vread_ADC = V_ADC[channel]
        Iread_ADC = I_ADC[channel]
        line = "%d %5d %10.2f %8.2f %8.2f %8.d %4.d %4.d" % (channel, voltage, Vread, Iread, rload, start, end, step)
        print "ch# Vset [DAC] V [V] I [A]  R [ohm]"
        print "%d %5d %10.2f %8.2f %8.2f" % (channel, voltage, Vread, Iread, rload)

        with open(output,"ab") as f:
            f.write(str(line) + "\n")
 	########end of loop over voltage###############   
    return



VoltageScan("biasscan.txt", True, 0, 20)
