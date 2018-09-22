#!/usr/bin/env python

def AppendPreliminaryToSummaryFile(summaryFile, PowerUnitID, tester, posVoltage, posCurrent, negVoltage, negCurrent):
    lines = []
    if PowerUnitID == "Right":
        lines.append("----------------------------------- Summary file -------------------------------------")
        lines.append(" ")
        lines.append("Tester: " + tester)
        lines.append(" ")
        lines.append("-------------------------- Summary for Preliminary test ------------------------------")
    lines.append(" ")
    lines.append("Power Unit " + PowerUnitID + ":")
    lines.append("Smoke test passed? YES")
    lines.append("3.3V Voltage: " + str(posVoltage) + "V; 3.3V Current (must be zero): " + str(posCurrent) + "A")
    lines.append("-5V Voltage: " + str(negVoltage) + "V; -5V Current: " + str(negCurrent) + "A")
    with open(summaryFile,"ab") as f:
        for line in lines:
            f.write(str(line) + "\n")

def AppendI2CToSummaryFile(summaryFile, PowerUnitID):
    lines = []
    if PowerUnitID == "Right":
        lines.append(" ")
        lines.append("-------------------------- Summary for I2C communication test ------------------------")
    lines.append(" ")
    lines.append("Power Unit " + PowerUnitID + ":")
    lines.append("I2C communication test completed successfully? YES")
    with open(summaryFile,"ab") as f:
        for line in lines:
            f.write(str(line) + "\n")

def AppendLatchToSummaryFile(summaryFile, PowerUnitID):
    lines = []
    if PowerUnitID == "Right":
        lines.append(" ")
        lines.append("-------------------------- Summary for Latch test ------------------------------------")
    lines.append(" ")
    lines.append("Power Unit " + PowerUnitID + ":")
    lines.append("Channel: 0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  B0  B1  B2  B3")
    lines.append("Result:  OK  OK  OK  OK  OK  OK  OK  OK  OK  OK  OK  OK  OK  OK  OK  OK  OK  OK  OK  OK")
    with open(summaryFile,"ab") as f:
        for line in lines:
            f.write(str(line) + "\n")

def AppendTemperatureToSummaryFile(summaryFile, PowerUnitID, initialState, initialStateRms, overtemperatureThreshold):
    lines = []
    if PowerUnitID == "Right":
        lines.append(" ")
        lines.append("-------------------------- Summary for Temperature test ------------------------------")
    lines.append(" ")
    lines.append("Power Unit " + PowerUnitID + ":")
    lines.append("Onboard sensor initial temperature.     Mean: " + str(int(initialState[0] * 1000) / 1000.) + "C, RMS: " + str(initialStateRms[0]))
    lines.append("External sensor #1 initial temperature. Mean: " + str(int(initialState[1] * 1000) / 1000.) + "C, RMS: " + str(initialStateRms[1]))
    lines.append("External sensor #2 initial temperature. Mean: " + str(int(initialState[2] * 1000) / 1000.) + "C, RMS: " + str(initialStateRms[2]))
    with open(summaryFile,"ab") as f:
        for line in lines:
            f.write(line + "\n")

def AppendPowerToSummaryFile(summaryFile, PowerUnitID, load, vlowers, vuppers, vints, vslopes, iints, islopes):
    # Rounding all results:
    vlowers = [('%.3f' % x) for x in vlowers]
    vuppers = [('%.3f' % x) for x in vuppers]
    vints   = [('%.3f' % x) for x in vints]
    vslopes = [('%.3f' % (x*1000)) for x in vslopes]
    iints   = [('%.3f' % x) for x in iints]
    islopes = [('%.3f' % (x*1000)) for x in islopes]

    lines = []
    if PowerUnitID == "Right":
        lines.append(" ")
        lines.append("-------------------------- Summary for Voltage scan ----------------------------------")
        lines.append(" ")
        lines.append("Load Type: " + load)
    lines.append(" ")
    lines.append("Power Unit " + PowerUnitID + ":")
    lines.append("Channel:                        0     1     2     3     4     5     6     7     8     9    10    11    12    13    14    15")
    lines.append("Voltage lowest [V]:           " + " ".join(str(x) for x in vlowers))  
    lines.append("Voltage highest [V]:          " + " ".join(str(x) for x in vuppers))  
    lines.append("Voltage intercept [V]:        " + " ".join(str(x) for x in vints))  
    lines.append("Voltage slope (e-3) [V/DAC]:  " + " ".join(str(x) for x in vslopes))  
    lines.append("Current intercept [I]:        " + " ".join(str(x) for x in iints))  
    lines.append("Current slope (e-3) [I/DAC]:  " + " ".join(str(x) for x in islopes))  
    with open(summaryFile,"ab") as f:
        for line in lines:
            f.write(line + "\n")

def AppendBiasToSummaryFile(summaryFile, PowerUnitID, load, vlower, vupper, vint, vslope, iint, islope):
    # Rounding all results:
    vlower  = '%.2f' % vlower
    vupper  = '%.2f' % vupper
    vint    = '%.2f' % (vint * 1000.)
    vslope  = '%.2f' % (vslope * 100.)
    iint    = '%.2f' % (iint * 1000.)
    islope  = '%.2f' % (islope * 10000.)

    lines = []
    if PowerUnitID == "Right":
        lines.append(" ")
        lines.append("-------------------------- Summary for Bias scan -------------------------------------")
        lines.append(" ")
        lines.append("Load Type: " + load)
    lines.append(" ")
    lines.append("Power Unit " + PowerUnitID + ":")
    lines.append("Voltage lowest: " + str(vlower))  
    lines.append("Voltage highest: " + str(vupper))  
    lines.append("Voltage intercept (e-3) [V]: " + str(vint))  
    lines.append("Voltage slope (e-2) [V/DAC]: " + str(vslope))  
    lines.append("Current intercept (e-3) [I]: " + str(iint))  
    lines.append("Current slope (e-4) [I/DAC]: " + str(islope))  
    with open(summaryFile,"ab") as f:
        for line in lines:
            f.write(line + "\n")

def AppendThresholdToSummaryFile(summaryFile, PowerUnitID, load, ilowers, iuppers, iints, islopes):
    # Rounding all results:
    ilowers  = [('%.4f' % x) for x in ilowers]
    iuppers  = [('%.4f' % x) for x in iuppers]
    iints    = [('%.3f' % x) for x in iints]
    islopes  = [('%.4f' % (x*10000)) for x in islopes]

    lines = []
    if PowerUnitID == "Right":
        lines.append(" ")
        lines.append("-------------------------- Summary for Threshold scan --------------------------------")
        lines.append(" ")
        lines.append("Load Type: " + load)
    lines.append(" ")
    lines.append("Power Unit " + PowerUnitID + ":")
    lines.append("Channel:                         0      1      2      3      4      5      6      7      8      9     10     11     12     13     14     15")
    lines.append("Current lowest [I]:           " + " ".join(str(x) for x in ilowers))  
    lines.append("Current highest [I]:          " + " ".join(str(x) for x in iuppers))  
    lines.append("Current intercept [I]:        " + " ".join(str(x) for x in iints))  
    lines.append("Current slope (e-4) [I/DAC]:  " + " ".join(str(x) for x in islopes))  
    with open(summaryFile,"ab") as f:
        for line in lines:
            f.write(line + "\n")

def Round(number, numberOfDecimals):
    factor = int(10**int(numberOfDecimals))
    return int(number * factor)/float(factor)
