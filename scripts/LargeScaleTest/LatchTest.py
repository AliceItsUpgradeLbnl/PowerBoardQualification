from UsefulFunctions import*
import math

import ReadConfig

def LatchTest(output, load, PowerUnitID):
    # Config params
    config = ReadConfig.GetMostRecentConfig('/home/its/Desktop/PB-production/PB-production/scripts/LargeScaleTest/QualificationConfig/')
    minrc = config["LatchTest_minrc"]		
    maxrc = config["LatchTest_maxrc"]		


    OpenFtdi() # Starts communication with RDO board

    ConfigurePowerADC(PowerUnitID) # To be able to read out voltages and currents
    ConfigureBiasADC(PowerUnitID) # To be able to read out voltages and currents

    passed = True

    # Recording states of channels before enabling them
    poweronStates   = GetPowerLatchStatus(PowerUnitID)
    poweronVoltages = ReadPowerChannelVoltages(PowerUnitID)
    poweronCurrents = ReadPowerChannelCurrents(PowerUnitID)

    ponBiasCurrent = 0.
    ponBiasVoltage = 0.
    ponCurrents = [0. for x in range(16)]
    ponVoltages = [0. for x in range(16)]
    for i in range(10):
        poweronBiasCurrent, poweronBiasVoltage = ReadBiasADC(PowerUnitID) 
        ponBiasCurrent  = ponBiasCurrent + poweronBiasCurrent 
        ponBiasVoltage  = ponBiasVoltage + poweronBiasVoltage
        ponCurrents = [x + y for x,y in zip(ponCurrents, ReadPowerChannelCurrents(PowerUnitID))]
        ponVoltages = [x + y for x,y in zip(ponVoltages, ReadPowerChannelVoltages(PowerUnitID))]
    ponCurrents.append(ponBiasCurrent)
    ponVoltages.append(ponBiasVoltage)
    ponCurrents = [('%.3f' % (x*100)) for x in ponCurrents]
    ponVoltages = [('%.4f' % (x*100)) for x in ponVoltages]
    # Check positive voltages at power on
    if any([float(x) > 10. for x in ponVoltages[0:16]]):
        print "Power on voltage for positive voltages is not ~0V"
        sys.exit()
    # Check positive currents at power on
    if any([(float(x) > 7. or x < -7.) for x in ponCurrents[0:16]]):
        print "Power on current for positive voltages is not ~0A"
        sys.exit()
    # Check negative regulator voltage at power on
    if (float(ponVoltages[16]) > -4500 or float(ponVoltages[16]) < -5000):
        print "Power on voltage for negative voltage regulator is not ~-5V"
        sys.exit()
    # Check negative regulator current at power on
    if (float(ponCurrents[16]) > 70 or float(ponCurrents[16]) < 30):
        print ponCurrents[16]
        print "Power on current for negative voltage regulator is not ~50mA"
        sys.exit()

    lines = []
    lines.append(" ")
    lines.append("Power on Voltages and currents:")
    lines.append("Channel:              0      1      2      3      4      5      6      7      8      9     10     11     12     13     14     15     NREG")
    lines.append("Voltage (e-3) [V]: " + " ".join(str(x) for x in ponVoltages))
    lines.append("Current (e-3) [I]: " + " ".join(str(x) for x in ponCurrents))
    lines.append(" ")
    for line in lines:
        print line
        with open(output,"ab") as f:
	    f.write(str(line) + "\n")

    # Latching all channels and setting threshold to max value
    LowerThresholdsToMin(PowerUnitID) 
    time.sleep(1.)

    header = 'CH#   After PB powering  /  After Enabling  /  After Disabling  /  After Power not latched  /  After Power Latched  /  All checks passed?'
    with open(output,"ab") as f:
	f.write(str(header) + "\n")

    print " "
    print 'Printing state results:'
    print 'CH#   After PB powering  /  After Enabling  /  After Disabling  /  After Power not latched  /  After Power Latched  /  All checks passed?'

    lines.append

    # Setting Power voltages to midscale
    SetPowerVoltageAll(0xFF, PowerUnitID)

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

    # Starting test of the bias circuitry
    print " "
    SetBiasVoltage(0x50, PowerUnitID)
    time.sleep(1.)
    poweronStates = 0xFF - int(GetBiasLatchStatus(PowerUnitID), 2)
    
    print 'Printing results:'
    print 'CH#   After PB powering  /  After Enabling  /  After Disabling  /                                                      All checks passed?'
    #DisableBiasAll(PowerUnitID)
    biasRes = {"Low": 1000., "Nominal": 1000., "High": 330.}
    offset = 0.
    for biasOutput in range(0, 3):
        idleCurrent, voltage = ReadBiasADC(PowerUnitID) 
        UnlatchBiasWithMask(0x7, PowerUnitID)
        time.sleep(0.1)  # Enable time
        afterEnablingThreeStates = 0xFF - int(GetBiasLatchStatus(PowerUnitID), 2)
        time.sleep(0.25) # ADC conversion time
        currentThree, voltageThree = ReadBiasADC(PowerUnitID) 
        if biasOutput == 0:
            offset = currentThree - abs(voltageThree)*(3./biasRes[load] + 1./100.)
        UnlatchBiasWithMask(0x7 - 2**biasOutput, PowerUnitID)
        time.sleep(0.1)  # Enable time
        afterEnablingStates = 0xFF - int(GetBiasLatchStatus(PowerUnitID), 2)
        time.sleep(0.25) # ADC conversion time
        current, voltage = ReadBiasADC(PowerUnitID) 
        DisableBiasAll(PowerUnitID)
        time.sleep(0.1)  # Enable time
        afterDisablingStates = 0xFF - int(GetBiasLatchStatus(PowerUnitID), 2)
        time.sleep(0.25) # ADC conversion time
        finalCurrent, finalVoltage = ReadBiasADC(PowerUnitID) 
        if not (poweronStates == 0 and afterEnablingThreeStates == 0x7 and afterEnablingStates == (0x7 - 2**biasOutput) and afterDisablingStates == 0):
            print "Bias channel states are wrong!"            
            line = "%2s %10d %23d %18d %70s" %("B" + str(biasOutput), poweronStates, 0x7 - afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        elif not (abs(finalCurrent - idleCurrent) < 0.0001 and voltage > -3.5 and voltage < -2.5):
            print "Mismatch between idle current and current after all channel disable, or voltage not in the expected range"
            line = "%2s %10d %23d %18d %70s" %("B" + str(biasOutput), poweronStates, 0x7 - afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        elif not ((abs(abs(voltage)/(currentThree - current) - biasRes[load])/biasRes[load]) < 0.1):
            print "Measured load resistance does not match actual load"
            line = "%2s %10d %23d %18d %70s" %("B" + str(biasOutput), poweronStates, 0x7 - afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        else:
            line = "%2s %10d %23d %18d %70s" %("B" + str(biasOutput), poweronStates, 0x7 - afterEnablingStates, afterDisablingStates, 'YES')

	print line
        with open(output,"ab") as f:
            f.write(str(line) + "\n")

    SetBiasVoltage(0x80, PowerUnitID)
    time.sleep(1.)  # Wait before sampling

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
    currentLimit = current - offset
    if load == "Low":
        if not (poweronStates == 0 and afterEnablingStates == (1 << 3) and afterDisablingStates == 0):
            print "Bias channel states are wrong!"            
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        elif not ((currentLimit < 0.105 and currentLimit > 0.075) and (voltage < -1.5 and voltage > -2.5)):
            print "Current limit outside boundaries (75mA - 105mA) or voltage outside boundaries (-1.5, -2.5)"            
            print currentLimit, offset
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        elif not ((abs(finalCurrent - idleCurrent) < 0.0001) and ((abs(voltage)/currentLimit) - 28.)/28. < 0.1) :
            print "Mistmatch between idle current and current after all channel disabled or wrong load measurement" 
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        else:
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'YES')
    else:
        if not (poweronStates == 0 and afterEnablingStates == (1 << 3) and afterDisablingStates == 0):
            print "Bias channel states are wrong!"            
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        elif not (abs(finalCurrent - idleCurrent) < 0.0001 and voltage < -4.5):
            print "Mismatch between idle current and current after all channel disable, or voltage is higher than -4.5V"
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        elif not ((abs(abs(voltage)/(current - idleCurrent) - biasRes[load])/biasRes[load]) < 0.1):
            print "Measured load resistance does not match actual load"
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'NO')
            passed = False
        else:
            line = "%2s %10d %23d %18d %70s" %("B3", poweronStates, afterEnablingStates, afterDisablingStates, 'YES')

    print line
    with open(output,"ab") as f:
        f.write(str(line) + "\n")

    if load == "Low":
        with open(output,"ab") as f:
            f.write(" " + "\n")
            f.write("Negative voltage regulator hardware current limit measured with Low current loads: %f\n" % currentLimit)


    CloseFtdi() # Ends communication with RDO board

    return passed
