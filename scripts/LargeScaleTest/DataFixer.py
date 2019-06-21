#!/usr/bin/env python

import PowerboardTestData as PbData

#../RESULTS/PB-0096_PU-Left_Load-High_BiasCalibration_20190529T133641.dat     ../RESULTS/PB-0096_PU-Right_Load-High_BiasScan_20190529T133641.dat
#../RESULTS/PB-0096_PU-Left_Load-High_BiasScan_20190529T133641.dat            ../RESULTS/PB-0096_PU-Right_Load-High_ThresholdScan_20190529T133641.dat
#../RESULTS/PB-0096_PU-Left_Load-High_ThresholdScan_20190529T133641.dat       ../RESULTS/PB-0096_PU-Right_Load-High_VoltageCalibration_20190529T133641.dat
#../RESULTS/PB-0096_PU-Left_Load-High_VoltageCalibration_20190529T133641.dat  ../RESULTS/PB-0096_PU-Right_Load-High_VoltageScan_20190529T133641.dat
#../RESULTS/PB-0096_PU-Left_Load-High_VoltageScan_20190529T133641.dat         ../RESULTS/PB-0096_PU-Right_Load-Low_BiasScan_20190529T131449.dat
#../RESULTS/PB-0096_PU-Left_Load-Low_BiasScan_20190529T131449.dat             ../RESULTS/PB-0096_PU-Right_Load-Low_LatchTest_20190529T131449.dat
#../RESULTS/PB-0096_PU-Left_Load-Low_LatchTest_20190529T131449.dat            ../RESULTS/PB-0096_PU-Right_Load-Low_TemperatureTest_20190529T131449.dat
#../RESULTS/PB-0096_PU-Left_Load-Low_TemperatureTest_20190529T131449.dat      ../RESULTS/PB-0096_PU-Right_Load-Low_ThresholdScan_20190529T131449.dat
#../RESULTS/PB-0096_PU-Left_Load-Low_ThresholdScan_20190529T131449.dat        ../RESULTS/PB-0096_PU-Right_Load-Low_VoltageScan_20190529T131449.dat
#../RESULTS/PB-0096_PU-Left_Load-Low_VoltageScan_20190529T131449.dat          ../RESULTS/PB-0096_PU-Right_Load-Nominal_BiasScan_20190529T132540.dat
#../RESULTS/PB-0096_PU-Left_Load-Nominal_BiasScan_20190529T132540.dat         ../RESULTS/PB-0096_PU-Right_Load-Nominal_ThresholdScan_20190529T132540.dat
#../RESULTS/PB-0096_PU-Left_Load-Nominal_ThresholdScan_20190529T132540.dat    ../RESULTS/PB-0096_PU-Right_Load-Nominal_VoltageScan_20190529T132540.dat
#../RESULTS/PB-0096_PU-Left_Load-Nominal_VoltageScan_20190529T132540.dat      ../RESULTS/PB-0096_summary_20190529T133641.txt
#../RESULTS/PB-0096_PU-Right_Load-High_BiasCalibration_20190529T133641.dat

def GenerateBiasVoltageSummaryReport(inputFile, PowerUnitID, load):
    bvsData = PbData.BiasScan(PowerUnitID, load, "./trial.txt") 
    bvsData.readFile(inputFile)
    bvsData.visualizeAndCheck(False, True)

def GeneratePowerVoltageSummaryReport(inputFile, PowerUnitID, load):
    vsData = PbData.VoltageScan(PowerUnitID, load, "./trial.txt") 
    vsData.readFile(inputFile)
    vsData.visualizeAndCheck(True, False, True)

def GenerateThresholdScanSummaryReport(inputFile, PowerUnitID, load):
    tsData = PbData.ThresholdScan(PowerUnitID, load, "./trial.txt") 
    tsData.readFile(inputFile)
    tsData.visualizeAndCheck(True, False, True)

GenerateThresholdScanSummaryReport("../RESULTS/PB-0096_PU-Right_Load-Low_ThresholdScan_20190529T131449.dat", "Right", "Low")
GenerateThresholdScanSummaryReport("../RESULTS/PB-0096_PU-Left_Load-Low_ThresholdScan_20190529T131449.dat", "Left", "Low")
