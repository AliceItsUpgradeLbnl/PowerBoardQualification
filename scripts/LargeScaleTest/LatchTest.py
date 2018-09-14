from UsefulFunctions import*
import math

def LatchTest(output, sleep, PowerUnitID):
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
    print 'CH#   Before Enabling  /  After Power on Latched  /  After Enabling  /  After Disabling  /  After Latching  /  Check OK?'
    # Loop over channels
    for channel in range(16):
        # Recording states of channels before enabling them
        beforeEnablingStates   = GetPowerLatchStatus(PowerUnitID)
        beforeEnablingVoltages = ReadPowerChannelVoltages(PowerUnitID)

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
        AppendSleep(ListOfCommands, 5000) # 7 ms (10 ms RC is nominal, 8ms is -20%, taking 1ms lower margin)
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
        AppendSleep(ListOfCommands, 13000) # 13 ms (10 ms RC is nominal, 12ms is +20%, taking 1ms higher margin)
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
        print afterEnablingVoltages
        # Disabling channels and checking states and voltages
        DisablePowerAll(PowerUnitID)
	time.sleep(0.001)  # Turn off time of the regulators
        afterDisablingStates = GetPowerLatchStatus(PowerUnitID) # Read status
	time.sleep(0.12) # Conversion time of the ADCs
        afterDisablingVoltages = ReadPowerChannelVoltages(PowerUnitID)
        # Lowering thresholds channels and checking states and voltages
        UnlatchPower(channel, PowerUnitID) # Enable channel 
        time.sleep(0.001) # Turn on time of regulators
        SetThreshold(channel, 0, PowerUnitID) # Set threshold of channel to zero to latch it
	time.sleep(0.003) # Setting time of threshold
        afterLatchingStates = GetPowerLatchStatus(PowerUnitID) # Read status
	time.sleep(0.12) # Conversion time of the ADCs
        afterLatchingVoltages = ReadPowerChannelVoltages(PowerUnitID)
        print afterPowerNotLatchedStates
        print afterPowerLatchedStates
        if (beforeEnablingStates == 0 and afterPowerNotLatchedStates == (1 << channel) and afterPowerLatchedStates == 0 \
            and afterEnablingStates == (1 << channel) and afterDisablingStates == 0 and afterLatchingStates == 0 \
            and not any([(voltage > 0.001) for voltage in beforeEnablingVoltages]) \
            and (afterPowerNotLatchedVoltages[channel] > 2.0) \
            and not any([(afterPowerNotLatchedVoltages[i] > 0.001) for i in range(len(afterPowerNotLatchedVoltages)) if i != channel]) \
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

    # Testing bias section - Channels 0-2
    ConfigureBiasADC(PowerUnitID) # this is necessary to be able to read ADCs
    SetBiasVoltage(0x80, PowerUnitID)
    for biasOutput in range(3):
        DisableBiasAll(PowerUnitID)
        time.sleep(0.1)  # Enable time
        time.sleep(0.12) # ADC conversion time
        idleCurrent, voltage = ReadBiasADC(PowerUnitID) 
        print idleCurrent
        UnlatchBias(biasOutput, PowerUnitID)
        time.sleep(0.1)  # Enable time
        time.sleep(0.12) # ADC conversion time
        current, voltage = ReadBiasADC(PowerUnitID) 
        print current, voltage
        if (abs(abs(voltage)/(current - idleCurrent) - 1000.)/1000.) > 0.20:
            print "Measured load does not match actual load (expected 1000 Ohm)"
            passed = False

    # Testing bias section - Channel 3
    DisableBiasAll(PowerUnitID)
    time.sleep(0.1)  # Enable time
    time.sleep(0.12) # ADC conversion time
    idleCurrent, voltage = ReadBiasADC(PowerUnitID) 
    print idleCurrent
    UnlatchBias(3, PowerUnitID)
    time.sleep(0.1)  # Enable time
    time.sleep(0.12) # ADC conversion time
    current, voltage = ReadBiasADC(PowerUnitID) 
    print current, voltage
    if current > 0.070 or current < 0.060:
        print "Regulator current limit outside boundaries"
    if voltage > -2.0 or voltage < -3.0:
        print "Regulator current limit outside boundaries"
        passed = False

    CloseFtdi() # Ends communication with RDO board

    return passed
