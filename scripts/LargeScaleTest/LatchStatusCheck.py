from UsefulFunctions import*
import math

def LatchUpCheck(output, sleep, PowerUnitID):
    OpenFtdi() # Starts communication with RDO board

    ConfigureRTD(PowerUnitID) # To monitor temperature on the power board

    # Setting threshold to max value
    LowerThresholdsToMin(PowerUnitID) 
    RaiseThresholdsToMax(PowerUnitID)

    passed = True
    print " "
    print 'Printing results:'
    print 'CH#   Before Enabling  /  After Enabling  /  After Latching  /  Check OK?'
    # Loop over channels
    for channel in range(16):
        beforeEnabling = GetPowerLatchStatus(PowerUnitID)
        UnlatchPower(channel, PowerUnitID)#enable channel 
	time.sleep(sleep)
        afterEnabling = GetPowerLatchStatus(PowerUnitID) #read status
        SetThreshold(channel, 0, PowerUnitID) #set threshold of channel to zero to latch it
        time.sleep(sleep)
        afterLatching = GetPowerLatchStatus(PowerUnitID) #read status
        if (beforeEnabling == 0 and afterEnabling == 1 << channel and afterLatching == 0):
            line = "%2d %10d %20d %18d %15s" %(channel, beforeEnabling, afterEnabling, afterLatching, 'YES')
	else:
            line = "%2d %10d %20d %18d %15s" %(channel, beforeEnabling, afterEnabling, afterLatching, 'NO')
            passed = False

	print line
        with open(output,"ab") as f:
            f.write(str(line) + "\n")
  
    print " "
    LowerThresholdsToMin(PowerUnitID) #to latch everything and erase whatever previous state
    RaiseThresholdsToMax(PowerUnitID)

    CloseFtdi() # Ends communication with RDO board

    return passed
