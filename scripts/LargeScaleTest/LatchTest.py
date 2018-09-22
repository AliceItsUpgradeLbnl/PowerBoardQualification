from UsefulFunctions import*
import math

import ReadConfig

def LatchTest(output, load, PowerUnitID):
    # Config params
    config = ReadConfig.GetMostRecentConfig('/home/its/Desktop/PB-production/PB-production/scripts/LargeScaleTest/QualificationConfig/')
    minrc = config["LatchTest_minrc"]		
    maxrc = config["LatchTest_maxrc"]		

    header = 'CH#   After PB powering  /  After Enabling  /  After Disabling  /  After Power not latched  /  After Power Latched  /  All checks passed?'
    with open(output,"ab") as f:
	f.write(str(header) + "\n")

    OpenFtdi() # Starts communication with RDO board

    ConfigurePowerADC(PowerUnitID) # To be able to read out voltages and currents

    # Latching all channels and setting threshold to max value
    LowerThresholdsToMin(PowerUnitID) 
    time.sleep(1.)

    # Setting Power voltages to midscale
    SetPowerVoltageAll(0xFF, PowerUnitID)
   
    passed = True
    print " "
    print 'Printing results:'
    print 'CH#   After PB powering  /  After Enabling  /  After Disabling  /  After Power not latched  /  After Power Latched  /  All checks passed?'
    # Recording states of channels before enabling them
    poweronStates   = GetPowerLatchStatus(PowerUnitID)
    poweronVoltages = ReadPowerChannelVoltages(PowerUnitID)
    # Loop over channels
    for channel in range(16):
        # Setting threshold low, enabling channel and setting threshold high after 10ms (short time)
        if (channel % 2):
            SetThreshold(channel, 0x368, PowerUnitID) # Lowering digital thresholds so the channels will latch at poweron (however threshold will be raised so it won't happen)
        else:
            SetThreshold(channel, 0x20E, PowerUnitID) # Lowering analog thresholds so the channels will latch at poweron (however threshold will be raised so it won't happen)
	time.sleep(0.010)  # Setting time of the threshold
        ListOfCommands = []
        LinkType       = IOExpanderPowerLink
        I2CAddress     = IOExpanderPowerAddress[channel/8]
        I2CData   = [0xFF & (1 << channel%8)]
        AppendWriteToDevice(ListOfCommands, I2CLink(PowerUnitID, LinkType), I2CAddress, *I2CData)
        AppendSleep(ListOfCommands, minrc * 1000) # 7 ms (10 ms RC is nominal, 8ms is -20%, taking 1ms lower margin)
        LinkType       = ThresPowerLink 
        I2CAddress     = ThresPowerAddress[channel/4]
        I2CData   = [0x3F, 0xFF, 0xF0]
        AppendWriteToDevice(ListOfCommands, I2CLink(PowerUnitID, LinkType), I2CAddress, *I2CData)
        SendPacket(ListOfCommands, [])
        time.sleep(0.05)
        afterPowerNotLatchedStates = GetPowerLatchStatus(PowerUnitID)
	time.sleep(0.12)  # ADC conversion time (15ms per ADC channel * # channels)
        afterPowerNotLatchedVoltages = ReadPowerChannelVoltages(PowerUnitID)

        # Setting threshold low, enabling channel and setting threshold high after 10ms (short time)
        if (channel % 2):
            SetThreshold(channel, 0x368, PowerUnitID) # Lowering digital thresholds so the channels will latch at poweron (however threshold will be raised so it won't happen)
        else:
            SetThreshold(channel, 0x20E, PowerUnitID) # Lowering analog thresholds so the channels will latch at poweron (however threshold will be raised so it won't happen)
	time.sleep(0.010)  # Setting time of the threshold
        ListOfCommands = []
        LinkType       = IOExpanderPowerLink
        I2CAddress     = IOExpanderPowerAddress[channel/8]
        I2CData   = [0xFF & (1 << channel%8)]
        AppendWriteToDevice(ListOfCommands, I2CLink(PowerUnitID, LinkType), I2CAddress, *I2CData)
        AppendSleep(ListOfCommands, maxrc * 1000) # 13 ms (10 ms RC is nominal, 12ms is +20%, taking 1ms higher margin)
        LinkType       = ThresPowerLink 
        I2CAddress     = ThresPowerAddress[channel/4]
        I2CData   = [0x3F, 0xFF, 0xF0]
        AppendWriteToDevice(ListOfCommands, I2CLink(PowerUnitID, LinkType), I2CAddress, *I2CData)
        SendPacket(ListOfCommands, [])
        time.sleep(0.05)
        afterPowerLatchedStates = GetPowerLatchStatus(PowerUnitID)
	time.sleep(0.12)  # ADC conversion time (15ms per ADC channel * # channels)
        afterPowerLatchedVoltages = ReadPowerChannelVoltages(PowerUnitID)

        # Raising threshold to max, enabling channels and checking states and voltages
        SetThreshold(channel, 0xFFF, PowerUnitID)
	time.sleep(0.003)  # Setting time of the threshold
        UnlatchPower(channel, PowerUnitID) # Enable channel 
	time.sleep(0.001)  # Turn on time of the regulators (< 1ms)
        afterEnablingStates   = GetPowerLatchStatus(PowerUnitID) # Read status
	time.sleep(0.12) # Conversion time of the ADCs
        afterEnablingVoltages = ReadPowerChannelVoltages(PowerUnitID)
        # Disabling channels and checking states and voltages
        DisablePowerAll(PowerUnitID)
	time.sleep(0.001)  # Turn off time of the regulators
        afterDisablingStates = GetPowerLatchStatus(PowerUnitID) # Read status
	time.sleep(0.12) # Conversion time of the ADCs
        afterDisablingVoltages = ReadPowerChannelVoltages(PowerUnitID)
        if (poweronStates == 0 and afterPowerNotLatchedStates == (1 << channel) and afterPowerLatchedStates == 0 \
            and afterEnablingStates == (1 << channel) and afterDisablingStates == 0 \
            and not any([(voltage > 0.001) for voltage in poweronVoltages]) \
            and (afterPowerNotLatchedVoltages[channel] > 2.0) \
            and not any([(afterPowerNotLatchedVoltages[i] > 0.001) for i in range(len(afterPowerNotLatchedVoltages)) if i != channel]) \
            and not any([(voltage > 0.001) for voltage in afterPowerLatchedVoltages]) \
            and (afterEnablingVoltages[channel] > 2.0) \
            and not any([(afterEnablingVoltages[i] > 0.001) for i in range(len(afterEnablingVoltages)) if i != channel]) \
            and not any([(voltage > 0.001) for voltage in afterDisablingVoltages])):
            line = "%2d %10d %23d %18d %23d %24d %21s" %(channel, poweronStates, afterEnablingStates, afterDisablingStates, afterPowerNotLatchedStates, afterPowerLatchedStates, 'YES')
	else:
            line = "%2d %10d %23d %18d %23d %24d %21s" %(channel, poweronStates, afterEnablingStates, afterDisablingStates, afterPowerNotLatchedStates, afterPowerLatchedStates, 'NO')
            passed = False

	print line
        with open(output,"ab") as f:
            f.write(str(line) + "\n")
  
    print " "
    LowerThresholdsToMin(PowerUnitID) # To latch everything and erase whatever previous state
    RaiseThresholdsToMax(PowerUnitID)

    # Testing bias section - Channels 0-2
    ConfigureBiasADC(PowerUnitID) # this is necessary to be able to read ADCs
    print " "
    SetBiasVoltage(0x80, PowerUnitID)
    time.sleep(0.5)
    poweronStates = 0xFF - int(GetBiasLatchStatus(PowerUnitID), 2)
    poweronCurrent, poweronVoltage = ReadBiasADC(PowerUnitID) 
    
    print 'Printing results:'
    print 'CH#   After PB powering  /  After Enabling  /  After Disabling  /                                                      All checks passed?'
    #DisableBiasAll(PowerUnitID)
    for biasOutput in range(3):
        idleCurrent, voltage = ReadBiasADC(PowerUnitID) 
        UnlatchBias(biasOutput, PowerUnitID)
        time.sleep(0.1)  # Enable time
        afterEnablingStates = 0xFF - int(GetBiasLatchStatus(PowerUnitID), 2)
        time.sleep(0.25) # ADC conversion time
        current, voltage = ReadBiasADC(PowerUnitID) 
        DisableBiasAll(PowerUnitID)
        time.sleep(0.1)  # Enable time
        afterDisablingStates = 0xFF - int(GetBiasLatchStatus(PowerUnitID), 2)
        time.sleep(0.25) # ADC conversion time
        finalCurrent, finalVoltage = ReadBiasADC(PowerUnitID) 
        if not (poweronStates == 0 and afterEnablingStates == (1 << biasOutput) and afterDisablingStates == 0 and \
           abs(finalCurrent - idleCurrent) < 0.001 and idleCurrent < 0.015 and voltage < -4.):
            line = "%2s %10d %23d %18d %70s" %("B" + str(biasOutput), poweronStates, afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        else:
            line = "%2s %10d %23d %18d %70s" %("B" + str(biasOutput), poweronStates, afterEnablingStates, afterDisablingStates, 'YES')

	print line
        with open(output,"ab") as f:
            f.write(str(line) + "\n")

        #if (abs(abs(voltage)/(current - idleCurrent) - 1000.)/1000.) > 0.20:
        #    #print "Measured load does not match actual load (expected 1k Ohm)"
        #    passed = False

    idleCurrent, voltage = ReadBiasADC(PowerUnitID) 
    UnlatchBias(3, PowerUnitID)
    time.sleep(0.1)  # Enable time
    afterEnablingStates = 0xFF - int(GetBiasLatchStatus(PowerUnitID), 2)
    time.sleep(0.25) # ADC conversion time
    current, voltage = ReadBiasADC(PowerUnitID) 
    DisableBiasAll(PowerUnitID)
    time.sleep(0.1)  # Enable time
    afterDisablingStates = 0xFF - int(GetBiasLatchStatus(PowerUnitID), 2)
    time.sleep(0.25) # ADC conversion time
    finalCurrent, finalVoltage = ReadBiasADC(PowerUnitID) 
    if load == "Low":
        if not (poweronStates == 0 and afterEnablingStates == (1 << 3) and afterDisablingStates == 0 and \
                (current < 0.070 and current > 0.060) and (voltage < -2.0 and voltage > -3.0) and abs(finalCurrent - idleCurrent) < 0.001 and idleCurrent < 0.015):
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        else:
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'YES')
    else:
        if not (poweronStates == 0 and afterEnablingStates == (1 << 3) and afterDisablingStates == 0 and \
            abs(finalCurrent - idleCurrent) < 0.001 and idleCurrent < 0.015 and voltage < -4.):
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        else:
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'YES')

    print line
    with open(output,"ab") as f:
        f.write(str(line) + "\n")

    CloseFtdi() # Ends communication with RDO board

    return passed
