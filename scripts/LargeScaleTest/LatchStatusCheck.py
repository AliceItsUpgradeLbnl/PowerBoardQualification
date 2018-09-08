from UsefulFunctions import*
import math

def LatchUpCheck(output, sleep, PowerUnitID):
    OpenFtdi() # Starts communication with RDO board

    ConfigurePowerADC(PowerUnitID) # To be able to read out voltages and currents

    # Latching all channels and setting threshold to max value
    LowerThresholdsToMin(PowerUnitID) 

    # Setting Power voltages to midscale
    SetPowerVoltageAll(0x80, PowerUnitID)
   
    passed = True
    print " "
    print 'Printing results:'
    print 'CH#   Before Enabling  /  After Power on Latched  /  After Enabling  /  After Disabling  /  After Latching  /  Check OK?'
    # Loop over channels
    for channel in range(16):
        # Recording states of channels before enabling them
        beforeEnablingStates   = GetPowerLatchStatus(PowerUnitID)
        beforeEnablingVoltages = ReadPowerChannelVoltages(PowerUnitID)
        # Setting threshold low, enabling channel, expecting them not being able to switch on 
        SetThreshold(channel, 0x000, PowerUnitID)
        time.sleep(0.020)
        UnlatchPower(channel, PowerUnitID)
	time.sleep(0.020)  # Minimum latch time 
        afterPowerLatchedStates = GetPowerLatchStatus(PowerUnitID)
	time.sleep(0.012)  # ADC conversion time
        afterPowerLatchedVoltages = ReadPowerChannelVoltages(PowerUnitID)
        # Raising threshold to max, enabling channels and checking states and voltages
        SetThreshold(channel, 0xFFF, PowerUnitID)
        time.sleep(0.020)
        UnlatchPower(channel, PowerUnitID) # Enable channel 
	time.sleep(0.03)  # Turn on time of the regulators
        afterEnablingStates   = GetPowerLatchStatus(PowerUnitID) # Read status
	time.sleep(0.012) # Conversion time of the ADCs
        afterEnablingVoltages = ReadPowerChannelVoltages(PowerUnitID)
        print afterEnablingVoltages
        # Disabling channels and checking states and voltages
        DisablePowerAll(PowerUnitID)
	time.sleep(0.003)  # Turn off time of the regulators
        afterDisablingStates  = GetPowerLatchStatus(PowerUnitID) # Read status
	time.sleep(0.012) # Conversion time of the ADCs
        afterDisablingVoltages = ReadPowerChannelVoltages(PowerUnitID)
        # Lowering thresholds channels and checking states and voltages
        SetThreshold(channel, 0, PowerUnitID) # Set threshold of channel to zero to latch it
	time.sleep(0.003)  # Turn off time of the regulators after threshold is raised
        afterLatchingStates   = GetPowerLatchStatus(PowerUnitID) # Read status
	time.sleep(0.012) # Conversion time of the ADCs
        afterLatchingVoltages = ReadPowerChannelVoltages(PowerUnitID)
        if (beforeEnablingStates == 0 and afterPowerLatchedStates == 0 and afterEnablingStates == 1 << channel and afterDisablingStates == 0 and afterLatchingStates == 0 \
            and not any([(voltage > 0.001) for voltage in beforeEnablingVoltages]) \
            and not any([(voltage > 0.001) for voltage in afterPowerLatchedVoltages]) \
            and (afterEnablingVoltages[channel] > 2.0) \
            and not any([(afterEnablingVoltages[i] > 0.001) for i in range(len(afterEnablingVoltages)) if i != channel]) \
            and not any([(voltage > 0.001) for voltage in afterDisablingVoltages]) \
            and not any([(voltage > 0.001) for voltage in afterLatchingVoltages])):
            line = "%2d %10d %20d %20d %20d %18d %15s" %(channel, beforeEnablingStates, afterPowerLatchedStates, afterEnablingStates, afterDisablingStates, afterLatchingStates, 'YES')
	else:
            line = "%2d %10d %20d %20d %20d %18d %15s" %(channel, beforeEnablingStates, afterPowerLatchedStates, afterEnablingStates, afterDisablingStates, afterLatchingStates, 'NO')
            passed = False

	print line
        with open(output,"ab") as f:
            f.write(str(line) + "\n")
  
    print " "
    LowerThresholdsToMin(PowerUnitID) # To latch everything and erase whatever previous state
    RaiseThresholdsToMax(PowerUnitID)

    CloseFtdi() # Ends communication with RDO board

    return passed
