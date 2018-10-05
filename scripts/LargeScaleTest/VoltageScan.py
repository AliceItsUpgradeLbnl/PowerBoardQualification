#!/usr/bin/env python
__author__ = "A.Collu"
__version__ = "2.0"
__status__ = "Prototype"

import numpy as np

from UsefulFunctions import *
import ReadConfig
import time
from datetime import datetime

def PowerVoltageScan(output, load, PowerUnitID):
    # Config params
    config = ReadConfig.GetMostRecentConfig('/home/its/Desktop/PB-production/PB-production/scripts/LargeScaleTest/QualificationConfig/')
    step     = config["PowerScan_Vstep"]
    start    = config["PowerScan_start"]
    end      = config["PowerScan_end"]
    Nsamples = config["PowerScan_nsamples"]

    header   = "CH# Vset[DAC]   V[V]    dVRMS[mV] dVpp[mV]    I[A]  dIRMS[mA] dIpp[mA]   R[ohm]   T[C]   State                Timestamp" 
    with open(output,"ab") as f:
        f.write(str(header) + "\n")

    OpenFtdi() # Starts communication with RDO board

    ConfigureRTD(PowerUnitID) # To monitor temperature on the power board

    # Setting threshold to max value
    LowerThresholdsToMin(PowerUnitID) # To latch everything and erase whatever previous state
    RaiseThresholdsToMax(PowerUnitID)

    # Switching on the channels in sequence to avoid sensing issues on the TDK supply
    UnlatchPowerWithMask(PowerUnitID, 0x000F)
    time.sleep(0.2)
    UnlatchPowerWithMask(PowerUnitID, 0x00FF)
    time.sleep(0.2)
    UnlatchPowerWithMask(PowerUnitID, 0x0FFF)
    time.sleep(0.2)
    UnlatchPowerWithMask(PowerUnitID, 0xFFFF)
    time.sleep(0.2)

    # This is necessary to be able to read ADCs that read the power channels
    ConfigurePowerADC(PowerUnitID) 

    #print "#ch Vset [DAC] V [V] VRMS [mV] dV[mV] I [A] IRMS [mA] dI [mA] R [ohm] T[C]"
    for voltage in range(start, end, -1*step): #loop over voltages
        print ' '
	print 'Setting voltage of all channels to %f [V]' %(voltage)
        SetPowerVoltageAll(voltage, PowerUnitID)
        time.sleep(0.2)
        LUstate = GetPowerLatchStatus(PowerUnitID)
        if LUstate == 0x00: break
        Imatrix = np.zeros((Nsamples,16))
	Vmatrix = np.zeros((Nsamples,16))
        
        for n in range(Nsamples):
            Itemp, Vtemp, I_ADC, V_ADC = ReadPowerADC(PowerUnitID)
	    Imatrix[n] = Itemp
	    Vmatrix[n] = Vtemp
            
        T = ReadRTD(PowerUnitID, 1)
        print "Printing results:"
        print "CH# Vset[DAC]   V[V]    dVRMS[mV] dVpp[mV]    I[A]  dIRMS[mA] dIpp[mA]   R[ohm]   T[C]   State                 Timestamp" 
        for ch in range(16): #loop over 
	    Ipoints = np.array([x[ch] for x in Imatrix])
	    Vpoints = np.array([x[ch] for x in Vmatrix])
            Iread   = Ipoints.mean()
	    IRMS    = 1000*Ipoints.std()
	    Vread   = Vpoints.mean()
	    VRMS    = 1000*Vpoints.std()
            DeltaI  = 1000*(Ipoints.max()-Ipoints.min())
	    DeltaV  = 1000*(Vpoints.max()-Vpoints.min())
	    rload   = -666
	    if(Iread > 0.): rload = Vread/Iread
            line = "%2d %7d %10.4f %8.1f %9.1f %10.4f %8.1f %6.1f %11.3f %6.1f %20s %24s" \
                   % (ch, voltage, Vread, VRMS, DeltaV, Iread, IRMS, DeltaI, rload, T, str(bin(LUstate)), str(datetime.now().strftime("%Y%m%dT%H%M%S%f")))
            print line
            with open(output,"ab") as f:
                f.write(str(line) + "\n")

    # Set the thresholds low to latch all unlatched channels (this should not be necessary if the board works properly), and then re-raise the thresholds for next test
    print ' '
    LowerThresholdsToMin(PowerUnitID) 
    RaiseThresholdsToMax(PowerUnitID)

    CloseFtdi() # Ends communication with RDO board

def BiasVoltageScan(output, load, PowerUnitID, testType = "standard"):
    # Config params
    config = ReadConfig.GetMostRecentConfig('/home/its/Desktop/PB-production/PB-production/scripts/LargeScaleTest/QualificationConfig/')
    step = config["BiasScan_Vstep"]
    start = config["BiasScan_start"]
    end = config["BiasScan_end"]
    Nsamples = config["BiasScan_nsamples"]
    header = "Vset[DAC]   V[V]      dVRMS[mV]   dVpp[mV]   I[A]     dIRMS[mA]   dIpp[mA]   R[ohm]   T[C]     State      Timestamp"
    with open(output,"ab") as f:
        f.write(str(header) + "\n")

    # Starts communication with RDO board
    OpenFtdi() 

    # To monitor temperature on the power board
    ConfigureRTD(PowerUnitID) 

    print 'Setting Bias Voltage ' 
    SetBiasVoltage(0,PowerUnitID)
    biasMask = 0
    if (testType == "calibration"):
        biasMask = 0x0
    elif (load == "Low"):
        biasMask = 0x7
    elif (load == "High"):
        biasMask = 0x9
    else:
        biasMask = 0xF
    UnlatchBiasWithMask(biasMask, PowerUnitID)
                                    
    ConfigureBiasADC(PowerUnitID) # this is necessary to be able to read ADCs
    time.sleep(0.2)
    print " "
    print "Scanning voltages and printing results:"
    print "Vset[DAC]   V[V]      dVRMS[mV]   dVpp[mV]   I[A]     dIRMS[mA]   dIpp[mA]   R[ohm]   T[C]     State      Timestamp"
    for voltage in range(start, end , -1*step):
        SetBiasVoltage(voltage, PowerUnitID)
        time.sleep(0.2)
        
        Ipoints = np.array([])
	Vpoints = np.array([])
        for n in range(Nsamples):
	    Itemp, Vtemp = ReadBiasADC(PowerUnitID) #read current and voltage from ADCs (before setting new threshold)
            Ipoints = np.append(Ipoints, Itemp)
	    Vpoints = np.append(Vpoints, Vtemp)

        Iread = Ipoints.mean()
	IRMS  = 1000*Ipoints.std()
	Vread = Vpoints.mean()
	VRMS  = 1000*Vpoints.std()
        DeltaI = 1000*(Ipoints.max()-Ipoints.min())
	DeltaV = 1000*(Vpoints.max()-Vpoints.min())
        rload = -1
	if(Iread > 0.): rload = Vread/Iread

        T = ReadRTD(PowerUnitID, 1)
        state = bin(0xFF - int(GetBiasLatchStatus(PowerUnitID), 2)) # bitwise not because all bits are active low
        line = "%5d %12.4f %9.2f %11.2f %11.6f %9.3f %9.3f %9.3f %9.3f %9s %24s" \
               % (voltage, Vread, VRMS, DeltaV, Iread, IRMS, DeltaI, abs(rload), T, state, str(datetime.now().strftime("%Y%m%dT%H%M%S%f")))
        print line

        with open(output,"ab") as f:
            f.write(str(line) + "\n")

    print ' '
    DisableBiasAll(PowerUnitID)

    # Ends communication with RDO board
    CloseFtdi() 
