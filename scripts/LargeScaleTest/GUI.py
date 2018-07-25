#!/usr/bin/env python

import Tkinter as tk
import tkMessageBox

import os
import io
import sys
import signal
import time
import shutil
import subprocess
import json
from definitions import WriteToDevice
from definitions import ReadFromDevice
from definitions import ReadRSFromDevice

from PowerUtils import PowerCyclePowerUnit
from I2CTest import I2CTest
from LatchStatusCheck import *
from VoltageScan import *
from ThresholdScan import *
from TemperatureTest import* 

from DataPlotter import PlotPowerVoltageScanData
from DataPlotter import PlotBiasVoltageScanData
from DataPlotter import PlotThresholdScanData

import FileHandler
import PowerboardTestData as PbData

outputFolder = 'RESULTS/'
configurationFolder = 'LargeScaleTest/ScanConfig/'

class StopTest(Exception):
    pass

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, relief = 'ridge', borderwidth = 2)
        self.grid(ipadx = 0, ipady = 0)

        # Defining the size of all columns
        self.grid_rowconfigure(0, minsize = 10)
        self.grid_rowconfigure(1, minsize = 30)
        self.grid_rowconfigure(2, minsize = 30)
        self.grid_rowconfigure(3, minsize = 30)
        self.grid_rowconfigure(4, minsize = 30)
        self.grid_rowconfigure(5, minsize = 30)
        self.grid_rowconfigure(6, minsize = 10)
        self.grid_rowconfigure(7, minsize = 10)
        self.grid_rowconfigure(8, minsize = 30)
        self.grid_rowconfigure(9, minsize = 30)
        self.grid_rowconfigure(10, minsize = 10)
        self.grid_rowconfigure(11, minsize = 10)
        self.grid_rowconfigure(12, minsize = 10)
        self.grid_rowconfigure(13, minsize = 10)
        self.grid_rowconfigure(14, minsize = 10)
        self.grid_rowconfigure(15, minsize = 10)
        self.grid_rowconfigure(16, minsize = 10)
        self.grid_rowconfigure(17, minsize = 10)
        self.grid_rowconfigure(18, minsize = 10)
        self.grid_rowconfigure(19, minsize = 10)
        self.grid_rowconfigure(20, minsize = 0)
        self.grid_rowconfigure(21, minsize = 10)
        self.grid_rowconfigure(22, minsize = 10)
        self.grid_rowconfigure(23, minsize = 10)
        self.grid_rowconfigure(24, minsize = 10)
        self.grid_rowconfigure(25, minsize = 10)
        self.grid_rowconfigure(26, minsize = 10)
        self.grid_rowconfigure(27, minsize = 10)
        self.grid_rowconfigure(28, minsize = 10)
        self.grid_columnconfigure(0, minsize = 10)
        self.grid_columnconfigure(1, minsize = 60)
        self.grid_columnconfigure(2, minsize = 60)
        self.grid_columnconfigure(3, minsize = 20)
        self.grid_columnconfigure(4, minsize = 130)
        self.grid_columnconfigure(5, minsize = 130)
        self.grid_columnconfigure(6, minsize = 130)
        self.grid_columnconfigure(7, minsize = 10)

        self.PowerUnitID = "Right"        

        config = {}
        PowerBoardIdIndexDict = {'Right': 1, 'Left': 2}
        # get the most recent configuration file
        files = os.listdir(configurationFolder)
        prefix = 'config'
        # the integer casting is necessary to sort properly
        numbers = [int(f[len(prefix):]) for f in files if f.startswith(prefix) and not f.endswith('~')]
        configNumber = max(numbers)
        configurationFile = configurationFolder + prefix + str(configNumber)

        with open(configurationFile) as f:
            config = json.load(f)

        #self.test_names= ["CH#%i"%n for n in range(16)]
        self.boxes    = []
        self.Eboxes   = []
        self.box_vars = []
        self.box_enab = []
        self.box_num  = 0
        self.BoardID = None

        ch_vars = [0 for i in range(16)]

        ch_en   = [0 for i in range(16)]

        ## Setters, getters and more ##############################
        def buildOutputFilename(timestamp, testName, PowerUnitID):
          filename = outputFolder + str(timestamp)
          filename = filename +'_BoardID%i_PowerUnit%s_LoadType%s_Config%s_%s_%s.txt' %(GetBoardID(), PowerUnitID, GetLoadType(), configNumber, testName, GetNameOfTester())
          return filename

        def GetPowerUnitID():
	    return self.PowerUnitID

        def GetBoardID():
            return self.BoardID

        def LockBoardID():
            try:
                self.BoardID = int(boardidField.get())
                boardidField.config(state='readonly')
                lockButton.config(state='disabled')
                unlockButton.config(state='normal')
                clearResultsButton.config(state='normal')
                pbtestingStatus = GetPowerBoardTestingStatus(GetBoardID())
                SetPbtestingStatusFields(pbtestingStatus)
            except:
                boardidField.delete(0, "end")
                tkMessageBox.showinfo("Wrong Board ID", "Invalid Board ID. Rescan and confirm.")

        def UnlockBoardID():
            boardidField.config(state='normal')
            boardidField.delete(0, "end")
            lockButton.config(state='normal')
            unlockButton.config(state='disabled')
            clearResultsButton.config(state='disabled')
            SetPbtestingStatusFields([0,0,0])
            self.BoardID = None

        def GetPowerBoardTestingStatus(boardId):
            pbtestingStatus = []
            for loadType in ["Low", "Nominal", "High"]:
                pbtestingStatus.append(FileHandler.CheckFiles(boardId, loadType))
            return pbtestingStatus

        def SetPbtestingStatusFields(pbtestingStatus):
            if pbtestingStatus[0]:
                lowEntry.config(disabledbackground = 'green') 
            else:
                lowEntry.config(disabledbackground = 'grey') 
            if pbtestingStatus[1]:
                nominalEntry.config(disabledbackground = 'green') 
            else:
                nominalEntry.config(disabledbackground = 'grey') 
            if pbtestingStatus[2]:
                highEntry.config(disabledbackground = 'green') 
            else:
                highEntry.config(disabledbackground = 'grey') 

                 
        def LoadFirmware():
	    os.system('clear')
	    print "========================================================================================="
	    print "                            Start loading firmware ........."
	    print "========================================================================================="
	    print " "
	    print " "

            subprocess.call(['/bin/bash', '-c', "/home/its/Desktop/PB-production/PB-production/firmware/scripts/loadfirmware.sh"])
            LdFirmware.config(bg='green')

	    print " "
	    print " "
	    print "========================================================================================="
	    print "                            Firmware successfully loaded!"
	    print "========================================================================================="

        def CheckCommunicationWithPowerBoard():
            if not CheckRDOConfigDone():
                return
            os.system('clear')
       	    print "========================================================================================="
	    print "                        Start checking communication ........."
	    print "========================================================================================="
	    print " "
	    print " "
            subprocess.call(['/bin/bash', '-c', "/home/its/Desktop/PB-production/PB-production/USB_tools/findall.sh"])
            OpenFtdi()
            print "Attempting to read from Power Unit Right..."
            data1 = GetBiasLatchStatus(1)
            print "Done successfully!"
            print "Attempting to read from Power Unit Left..."
            data2 = GetBiasLatchStatus(2)
            print "Done successfully!"
            CloseFtdi()
            CheckComm.config(bg='green')

	    print " "
	    print " "
	    print "========================================================================================="
	    print "                             End checking communication!"
	    print "========================================================================================="

        ## Test methods ###########################################
        def RunI2CTest(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=False, PowerUnitID=self.PowerUnitID):
            CleanTestReportEntry(PowerUnitID)
            if not CheckMainParameters() or not CheckRDOConfigAndCommDone():
                return

            os.system('clear')
            print "========================================================================================="
            print "                   Starting I2C test on Power Unit %s ........." %(PowerUnitID)
            print "========================================================================================="
            print " "
            print " "

            temporaryFile = "JUNK/I2CTest_PowerUnit%s.txt" %(PowerUnitID)
            if os.path.exists(temporaryFile): os.remove(temporaryFile)
            passed = I2CTest(PowerBoardIdIndexDict[PowerUnitID])
            PrintSummaryInGui(PowerUnitID, [GetTestMessage(0, passed)])
            if saveToFile and passed:
                outputFile = buildOutputFilename(timestamp, "I2CTest", PowerUnitID)
                subprocess.call(['/bin/bash', '-c', "cp %s %s" %(temporaryFile, outputFile)])
             
            print " "
            print " "
            print "========================================================================================="
            print "                        I2C test ended. Test passed? ", passed
            print "========================================================================================="

            return passed

        def RunLatchupCheck(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=False, PowerUnitID=self.PowerUnitID):
            CleanTestReportEntry(PowerUnitID)
            #if not CheckMainParameters() or not CheckRDOConfigAndCommDone():
            #    return
            os.system('clear')
            print "========================================================================================="
            print "                Starting Latch Up Scan on Power Unit %s ........." %(PowerUnitID)
            print "========================================================================================="
            print " "
            print " "

            temporaryFile = "JUNK/LatchTest_PowerUnit%s.txt" %(PowerUnitID)
            if os.path.exists(temporaryFile): os.remove(temporaryFile)
            header = "CH# Before Enabling / After Enabling / After Latching"
            with open(temporaryFile,"ab") as f:
                f.write(str(header) + "\n")
            sleep = config["LatchTest_sleep"]		
            passed = LatchUpCheck(temporaryFile, sleep, PowerBoardIdIndexDict[PowerUnitID])
            PrintSummaryInGui(PowerUnitID, [GetTestMessage(1, passed)])
            if saveToFile and passed:
            	outputFile = buildOutputFilename(timestamp, "Latchtest", PowerUnitID)
                subprocess.call(['/bin/bash', "-c", "cp %s %s" %(temporaryFile, outputFile)])

            print " "
            print " "
            print "========================================================================================="
            print "                        Latch Up Scan ended. Test passed? ", passed
            print "========================================================================================="

            return passed

        def RunBiasVoltageScan(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=False, PowerUnitID=self.PowerUnitID):
            CleanTestReportEntry(PowerUnitID)
            if not CheckMainParameters() or not CheckRDOConfigAndCommDone():
                return

            os.system('clear')
            print "========================================================================================="
            print "                 Starting Bias Voltage Scan on Power Unit %s ........." %(PowerUnitID)
            print "========================================================================================="
            print " "
            print " "

            temporaryFile = "JUNK/BiasVoltageScan_PowerUnit%s.txt" %(PowerUnitID)
            if os.path.exists(temporaryFile): os.remove(temporaryFile)
            isMaster = True
            Vstep = config["BiasScan_Vstep"]
            start = config["BiasScan_start"]
            end = config["BiasScan_end"]
            sleep = config["BiasScan_sleep"]
            samplingtime = config["BiasScan_samplingtime"]
            nsamples = config["BiasScan_nsamples"]

            header = "Vset [DAC] V [V] VRMS [V] dV[mV] I [A] IRMS [A] dI[mA] R [ohm] T[C]"
            with open(temporaryFile,"ab") as f:
                f.write(str(header) + "\n")
            BiasVoltageScan(temporaryFile, Vstep, start, end, samplingtime, nsamples, sleep, PowerBoardIdIndexDict[PowerUnitID])

            bvsData = PbData.BiasVoltageScan() 
            bvsData.readFile(temporaryFile)
            bvsHasProblem = bvsData.visualizeAndCheck()
            passed = not bvsHasProblem
            PrintSummaryInGui(PowerUnitID, [GetTestMessage(2, passed)])
            if saveToFile and passed:
            	outputFile = buildOutputFilename(timestamp, "BiasVoltageScan", PowerUnitID)
                subprocess.call(['/bin/bash', '-c', "cp %s %s" %(temporaryFile, outputFile)])

            print " "
            print " "
            print "========================================================================================="
            print "                        Bias Scan test ended. Test passed? ", passed
            print "========================================================================================="

            return passed

        def RunPowerVoltageScan(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=False, PowerUnitID=self.PowerUnitID):
            CleanTestReportEntry(PowerUnitID)
            if not CheckMainParameters() or not CheckRDOConfigAndCommDone():
                return

            os.system('clear')
            print "========================================================================================="
            print "               Starting Power Voltage Scan on Power Unit %s ........." %(PowerUnitID)
            print "========================================================================================="
            print " "
            print " "

            Vstep  = config["PowerScan_Vstep"]
            start  = config["PowerScan_start"]
            end    = config["PowerScan_end"]
            samplingtime = config["PowerScan_samplingtime"]
            nsamples = config["PowerScan_nsamples"]
            sleep = config["PowerScan_sleep"]
            header = "CH# Vset[DAC]   V[V]    dVRMS[mV] dVpp[mV]    I[A]  dIRMS[mA] dIpp[mA]   R[ohm]   T[C]   State" 

            temporaryFile = "JUNK/PowerVoltageScan_PowerUnit%s.txt" %(PowerUnitID)
            if os.path.exists(temporaryFile): os.remove(temporaryFile)
            with open(temporaryFile,"ab") as f:
                f.write(str(header) + "\n")
            PowerVoltageScan(temporaryFile, Vstep, start, end, samplingtime, nsamples, sleep, PowerBoardIdIndexDict[PowerUnitID])

            vsData = PbData.VoltageScan() 
            vsData.readFile(temporaryFile)
            plotOption = VoltageScanPlotOption.get()

            vsHasProblem = False
            if (plotOption == 1):
               vsHasProblem = vsData.visualizeAndCheck()
            elif (plotOption == 2):
               vsHasProblem = vsData.visualizeAndCheck(True)

            passed = not vsHasProblem
            PrintSummaryInGui(PowerUnitID, [GetTestMessage(3, passed)])
            if saveToFile and passed:
            	outputFile = buildOutputFilename(timestamp, "VoltageScan", PowerUnitID)
                subprocess.call(['/bin/bash', '-c', "cp %s %s" %(temporaryFile, outputFile)])

            print " "
            print " "
            print "========================================================================================="
            print "                       Power Scan test ended. Test passed? ", passed
            print "========================================================================================="

            return passed

        def RunThresholdScan(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=False, PowerUnitID=self.PowerUnitID):
            CleanTestReportEntry(PowerUnitID)
            if not CheckMainParameters() or not CheckRDOConfigAndCommDone():
                return
            os.system('clear')
            print "========================================================================================="
            print "                Starting Threshold Scan on Power Unit %s ........." %(PowerUnitID)
            print "========================================================================================="
            print " "
            print " "

            step  = config["ThresholdScan_Thstep"]
            start = config["ThresholdScan_start"]
            end   = config["ThresholdScan_end"]
	    Vset  = config["ThresholdScan_Vpoints"]
            header = "CH# Threshold[DAC] Vset[DAC] V[V] I[A]  R[ohm] T[C] LUstate"
            temporaryFile = "JUNK/ThresholdScan_PowerUnit%s.txt" %(PowerUnitID)
            if os.path.exists(temporaryFile): os.remove(temporaryFile)
            with open(temporaryFile,"ab") as f:
                f.write(str(header) + "\n")
            for V in Vset:
                thresholdScanAll(temporaryFile, step, start, end, V, PowerBoardIdIndexDict[PowerUnitID])
            passed = False
            PrintSummaryInGui(PowerUnitID, [GetTestMessage(4, passed)])
            if saveToFile and passed:
            	outputFile = buildOutputFilename(timestamp, "ThresholdScan", PowerUnitID)
                subprocess.call(['/bin/bash', '-c', "cp %s %s" %(temporaryFile, outputFile)])

	    print " "
            print " "
            print "========================================================================================="
            print "                            Threshold Scan test ended. Test passed? ", passed
            print "========================================================================================="

            return passed

        def RunOverTprotectionScan(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=False, PowerUnitID=self.PowerUnitID):
            CleanTestReportEntry(PowerUnitID)
            if not CheckMainParameters() or not CheckRDOConfigAndCommDone():
                return
            os.system('clear')
            print "========================================================================================="
            print "         Starting over-temperature protection test on Power Unit %s ........." %(PowerUnitID)
            print "========================================================================================="
            print " "
            print " "

            temporaryFile = "JUNK/TemperatureScan_PowerUnit%s.txt" %(PowerUnitID)
            if os.path.exists(temporaryFile): os.remove(temporaryFile)
            header = "Vavg[V] Itot[A] T[C]"
            with open(temporaryFile,"ab") as f:
                f.write(str(header) + "\n")

            timestep = config["TemperatureScan_timestep"]
            Vset = config["TemperatureScan_Vset"]

            passed = TemperatureTest(temporaryFile, timestep, PowerBoardIdIndexDict[PowerUnitID], Vset)
            PrintSummaryInGui(PowerUnitID, [GetTestMessage(5, passed)])
            if saveToFile and passed:
            	outputFile = buildOutputFilename(timestamp, "TemperatureScan", PowerUnitID)
                subprocess.call(['/bin/bash', '-c', "cp %s %s" %(temporaryFile, outputFile)])

            print " "
            print " "
            print "========================================================================================="
            print "                      Over-temperature ended. Test passed? ", passed
            print "========================================================================================="

            return passed

        def RunAllScans(timestamp = time.strftime("%Y%m%dT%H%M%S"), saveToFile=False):
            CleanTestReportEntry('Both')
            try:
                if not CheckMainParameters() or not CheckRDOConfigAndCommDone():
                    return
                if not tkMessageBox.askyesno("Voltage Check", "Are the supplied voltages 3.3V and 5V?"): 
                    return 
                if not tkMessageBox.askyesno("Current Check", "Are the 3.3V and 5V idle currents close to 0A?"):
                    return
                RunAllTestsButton.config(state='disabled')
                output = buildOutputFilename(timestamp, "PreliminaryCheck", "Both")
                if os.path.exists(output): os.remove(output)
                with open(output,"ab") as f: f.write("OK\n")
                if not tkMessageBox.askyesno("Start run", "Are you sure you want to run all tests?"):
                    return
                root.update()
                            
                passed      = {"Right": False, "Left": False}
                testResults = {"Right": 0, "Left": 0}
                PowerUnitIDs = ['Right', 'Left']
                # Running preliminary tests
                if load.get() == 'low':
		    tkMessageBox.showwarning( "Info", "Load \"low\" was selected. The GUI will run some preliminary tests on both power units before the scans.", icon="info")
                    for PowerUnitID in PowerUnitIDs:
		        testResults[PowerUnitID] = testResults[PowerUnitID] | (int(RunOverTprotectionScan(timestamp, saveToFile, PowerUnitID)) << 5)
                        tkMessageBox.showwarning( "Info", "Power Unit %s will be power cycled." %(PowerUnitID), icon="info")
                        PowerCyclePowerUnit(PowerUnitID)
                    for PowerUnitID in PowerUnitIDs:
		        testResults[PowerUnitID] = testResults[PowerUnitID] | RunI2CTest(timestamp, saveToFile, PowerUnitID)
                    for PowerUnitID in PowerUnitIDs:
		        testResults[PowerUnitID] = testResults[PowerUnitID] | (int(RunLatchupCheck(timestamp, saveToFile, PowerUnitID))     << 1)
                for PowerUnitID in PowerUnitIDs:
		    # List of tests that will be run
	            testResults[PowerUnitID] = testResults[PowerUnitID] | (int(RunBiasVoltageScan(timestamp, saveToFile, PowerUnitID))  << 2)
		    #testResults[PowerUnitID] = testResults[PowerUnitID] | (int(RunPowerVoltageScan(timestamp, saveToFile, PowerUnitID)) << 3)
		    #testResults[PowerUnitID] = testResults[PowerUnitID] | (int(RunThresholdScan(timestamp, saveToFile, PowerUnitID))    << 4)
                for PowerUnitID in PowerUnitIDs:
                    CleanTestReportEntry(PowerUnitID)
                    messageBuffer, passed[PowerUnitID] = SummaryOfResults(127, testResults[PowerUnitID])
	            PrintSummaryInGui(PowerUnitID, messageBuffer)
                    UpdateReportFieldsTitle(PowerUnitID, passed[PowerUnitID])
	        pbtestingStatus = GetPowerBoardTestingStatus(GetBoardID())
                SetPbtestingStatusFields(pbtestingStatus)
                # Tests are finished, resetting parameters
		tkMessageBox.showwarning( "Info", "All tests finished.", icon="info")
                RunAllTestsButton.config(state="normal")
                name.set('')
                ddownNames['bg'] = 'salmon'
                UnlockBoardID()
                load.set('')
                ddownLoads['bg'] = 'salmon'
                CheckComm['bg'] = 'salmon'
                return passed
            except StopTest:
                StopAllScans()

        def UpdateReportFieldsTitle(PowerUnitID, passed):
            qualification = ""
            fgcolor       = ""
            if passed:
                qualification = "good"
                fgcolor       = "green"
            else:
                qualification = "bad"
                fgcolor       = "red"

            if PowerUnitID == "Right":
                reportsRightTitle.config(text = ("Power Unit Right Qualification: " + qualification), fg = fgcolor)
            elif PowerUnitID == "Left":
                reportsLeftTitle.config(text = ("Power Unit Left Qualification: " + qualification), fg = fgcolor)

        def StopAllScans():
            raise StopTest
            RunAllTestsButton.config(state="normal")

        def CleanTestReportEntry(PowerUnitID):
            if PowerUnitID == 'Right':
            	reportsRight.config(state='normal')
            	reportsRight.delete("1.0", tk.END)
            	reportsRight.config(state='disabled')
            elif PowerUnitID == 'Left':
            	reportsLeft.config(state='normal')
            	reportsLeft.delete("1.0", tk.END)
            	reportsLeft.config(state='disabled')
            elif PowerUnitID == 'Both':
		CleanTestReportEntry("Right")
		CleanTestReportEntry("Left")

        def CheckMainParameters():
            if (GetBoardID() == None or GetNameOfTester() == '' or GetLoadType() == ''):
                tkMessageBox.showinfo("Missing info", "Please check that:\n\n1) Your name is selected\n2) A power board ID is entered\n3) A load is selected")
                return False
            return True

        def CheckRDOConfigAndCommDone():
            if (LdFirmware['bg'] == 'salmon' or CheckComm['bg'] == 'salmon'):
                tkMessageBox.showinfo("RDO unconfigured/unckecked", "Please check that:\n\n1) The firmware is loaded into the FPGA\n2) There is communication with the power board")
                return False
            return True

        def CheckRDOConfigDone():
            if (LdFirmware['bg'] == 'salmon'):
                tkMessageBox.showinfo("RDO unconfigured", "Please load the firmware into the FPGA before checking the communication")
                return False
            return True
                            
        def PrintSummaryInGui(PowerBoardID, messageBuffer):
            if PowerBoardID == 'Right':
            	reportsRight.config(state='normal')
            	for line in messageBuffer:
                    reportsRight.insert(tk.END, line + '\n')
                reportsRight.config(state='disabled')
            if PowerBoardID == 'Left':
            	reportsLeft.config(state='normal')
            	for line in messageBuffer:
                    reportsLeft.insert(tk.END, line + '\n')
                reportsLeft.config(state='disabled')

        # testMap: bitmap of the implemented tests (integer):
        # 0b000001: I2C test
        # 0b000010: Latchup test
        # 0b000100: Bias Voltage scan
        # 0b001000: Power Voltage scan
        # 0b010000: Threshold scan
        # 0b100000: Over-temperature test
        # testResults: bitmap if the results of the tests in line with what described above (0: failed, 1: passed)
	def SummaryOfResults(testMap, testResults):
            passed = True
            messageBuffer = []
	    for i in range(0, 6):
                if ((testMap >> i) & 0x1):
                    if not ((testResults >> i) & 0x1):
                        messageBuffer.append(GetTestMessage(i, False))
                        passed = False
                    else:
                        messageBuffer.append(GetTestMessage(i, True))

            return messageBuffer, passed

        # testNumber:
        # 1: I2C test
        # 2: Latchup test
        # 3: Bias Voltage scan
        # 4: Power Voltage scan
        # 5: Threshold scan
        # 6: Over-temperature test
        # testResult is either failed or passed
        def GetTestMessage(testNumber, testResultBool):
            if testResultBool:
                testResult = 'passed'
            else:
                testResult = 'failed'
            if (testNumber == 0):
                return "I2C test " + testResult
            elif (testNumber == 1):
                return "Latchup test " + testResult
            elif (testNumber == 2):
                return "Bias Voltage scan " + testResult
            elif (testNumber == 3):
                return "Power Voltage scan " + testResult
            elif (testNumber == 4):
                return "Threshold scan " + testResult
            elif (testNumber == 5):
                return "Over-temperature test " + testResult
            else:
                return "Wrong test type selected"

        ## GUI Objects #################################################################################

        ######## TITLE BAR  ##########################################################################
        self.titlefr = tk.Frame(self, bg = 'grey', relief = 'ridge', borderwidth = 2)
        self.titlefr.grid(row = 0, column = 0, columnspan = 10, sticky = 'nsew')
        titleLabel = tk.Label(self.titlefr, width = 45, text = "ALICE ITS Production Power Board qualification", anchor = 'center', fg="white", bg='midnight blue')
        titleLabel.grid(row = 0, column = 0, sticky = 'nsew')
        titleLabel.configure(font=("Helvetica", 18))
        self.canvasfr = tk.Frame(self.titlefr, bg = 'green')
        self.canvasfr.grid(row = 0, column = 1, sticky = 'nsew')
        #canvas = tk.Canvas(self.canvasfr, width = 85, highlightthickness = 0, height = 63, bg = 'green')
        #canvas.grid(row = 0, column = 0)
        self.picture = tk.PhotoImage(file='LargeScaleTest/GuiUtils/Lawrence-Berkley-Laboratory.gif')
        self.picture = self.picture.subsample(5)
        #canvas.create_image(0, 0, image = self.picture, anchor = 'nw')
        
        def DisplayAuthors():
            self.msg = tkMessageBox.showinfo("Developers", "If any issues are found during the operation of the GUI please contact:\n\nAlberto Collu (LBNL) albertocollu@lbl.gov\n\nAlwina Liu (UC Berkeley) alwina@berkeley.edu\n\nMiguel Arratia (UC Berkeley) marratia@berkeley.edu")
        authorsButton = tk.Button(self.canvasfr, image = self.picture, command = DisplayAuthors)
        authorsButton.grid(row = 0, column = 0)

        ################################################################################################
        ######## SETTING NAME ##########################################################################
        ################################################################################################
        def ddownNamesColorChange(event):
            if name.get():
                ddownNames.config(bg = 'green')
            else:
                ddownNames.config(bg = 'salmon')
        # Get the name from a list in file
        tk.Label(self, text = "Select tester name", fg="black").grid(row = 2, column = 1, columnspan = 2)
        namesFile = open('./LargeScaleTest/Names/namesList.txt', 'r')
        namesList = [x.split('\n')[0] for x in namesFile.readlines()]
        name = tk.StringVar()
        ddownNames = tk.OptionMenu(self, name, *namesList, command = ddownNamesColorChange)
        ddownNames.config(width = 10, bg = 'salmon')
        ddownNames.grid(row = 3, column = 1, columnspan = 2)
        def GetNameOfTester():
	    return name.get()

        ### Scan board ID button ##########################################
        tk.Label(self, text = "Scan Board ID", fg="black").grid(row = 4, column = 1)
        boardid  = tk.StringVar()
        boardidField = tk.Entry(self, textvariable=boardid, width = 10, readonlybackground = 'green', background = 'salmon')
        boardidField.grid(row = 5, column = 1)
        boardidField.focus()
        boardidField.insert(0, '')

        lockButton = tk.Button(self, text="Lock ID", command = LockBoardID)
        lockButton.grid(row = 6, column = 1, sticky = 'nswe')
        unlockButton = tk.Button(self, text="Unlock ID", command = UnlockBoardID, state='disabled')
        unlockButton.grid(row = 6, column = 2, sticky = 'nswe')
        ###################################################################

        ### Status  ##########################################
        tk.Label(self, text = "Status", fg="black").grid(row = 4, column = 2)
        fr = tk.Frame(self, bg = 'green')
        fr.grid(row = 5, column = 2)
        lowTvar = tk.StringVar(self, '  L ')
        lowEntry = tk.Entry(fr, textvariable=lowTvar, width = 3, state = 'disabled', disabledbackground = 'grey', disabledforeground='black')
        lowEntry.grid(row = 0, column = 1)
        nominalTvar = tk.StringVar(self, '  N ')
        nominalEntry = tk.Entry(fr, textvariable=nominalTvar, width = 3, state = 'disabled', disabledbackground = 'grey', disabledforeground = 'black')
        nominalEntry.grid(row = 0, column = 2)
        highTvar = tk.StringVar(self, '  H ')
        highEntry = tk.Entry(fr, textvariable=highTvar, width = 3, state = 'disabled', disabledbackground = 'grey', disabledforeground='black')
        highEntry.grid(row = 0, column = 3)

        ######################################################

        def DeleteAllBoardFiles():
            if not tkMessageBox.askyesno("Delete all board files", "Do you want to delete all files for the selected board?"): 
                return 
            if not tkMessageBox.askyesno("Delete all board files", "Are you really sure that you want to delete all files for this board?"): 
                return 
            if not tkMessageBox.askyesno("Delete all board files", "100% sure?"): 
                return 
            FileHandler.DeleteBoardFiles(GetBoardID())
        clearResultsButton = tk.Button(self, text="Clear previous results", command = DeleteAllBoardFiles, state = "disabled")
        clearResultsButton.grid(row = 7, column = 1, columnspan = 2, sticky = 'nsew')
  
        ################################################################################################
        ######## PICK TYPE OF LOAD #####################################################################
        ################################################################################################
        def ddownLoadsColorChange(event):
            if load.get():
                ddownLoads.config(bg = 'green')
            else:
                ddownLoads.config(bg = 'salmon')
        tk.Label(self, text = "Select load", fg="black").grid(row = 8, column = 1, columnspan = 2)
        load = tk.StringVar()
        ddownLoads = tk.OptionMenu(self, load, "Low", "Nominal", "High", command = ddownLoadsColorChange)
        ddownLoads.config(width = 10, bg = 'salmon')
        ddownLoads.grid(row = 9, column = 1, columnspan = 2)
        def GetLoadType():
	    return load.get()


        ################################################################################################
        ######## SELECT VOLTAGE SCAN PLOTTING OPTION ###################################################
        ################################################################################################
        VoltageScanPlotOption = tk.IntVar()
        VoltageScanPlotOption.set(2)

        ######### RDO CFG/CHECK  ##############################################################
        tk.Label(self, text = "RDO Config/Check", fg="black").grid(row = 2, column = 5)
        #######################################################################################

        ######### LOAD FIRMWARE  ##################################################################
        LdFirmware = tk.Button(self, text="Load Firmware", command = LoadFirmware, bg = 'salmon')
        LdFirmware.grid(row = 3, column = 5, sticky = 'nsew')
        ###########################################################################################

        ######### CHECK STATUS OF SYSTEM  #########################################################
        CheckComm = tk.Button(self, text="Check Comm", command = CheckCommunicationWithPowerBoard, bg = 'salmon')
        CheckComm.grid(row = 3, column = 6, sticky = 'nsew')
        ###########################################################################################

        ######### POWER UNIT SELECTION LABEL  #################################################
        tk.Label(self, text = "Select Power Unit", fg="black").grid(row = 4, column = 4, columnspan = 3)
        #######################################################################################

        ######### SCROLL BAR  #################################################################
        def PURightSel():
            self.PowerUnitID = "Right"
            PowerUnitRightButton.config(state = 'disabled')
            PowerUnitLeftButton.config(state = 'normal')
            PowerUnitRightButton.config(background = 'white')
            PowerUnitLeftButton.config(background = 'light grey')
        def PULeftSel():
            self.PowerUnitID = "Left"
            PowerUnitRightButton.config(state = 'normal')
            PowerUnitLeftButton.config(state = 'disabled')
            PowerUnitRightButton.config(background = 'light grey')
            PowerUnitLeftButton.config(background = 'white')
        PowerUnitLeftButton = tk.Button(self, text = "Power Unit Left", command = PULeftSel, disabledforeground = 'blue', background = 'light grey')
        PowerUnitLeftButton.grid(row = 5, column = 4, sticky = 'nsew')
        powerunitScrollbar = tk.Scrollbar(self, orient = 'horizontal')
        powerunitScrollbar.grid(row = 5, column = 5)
        PowerUnitRightButton = tk.Button(self, text = "Power Unit Right", command = PURightSel, state = 'disabled', disabledforeground = 'blue', background = 'white')
        PowerUnitRightButton.grid(row = 5, column = 6, sticky = 'nsew')
        #######################################################################################

        ######### SINGLE SELECTION LABEL  #################################################
        tk.Label(self, text = "Single Tests (on the selected power unit)", fg="black").grid(row = 6, column = 4, columnspan = 3)
        #######################################################################################

        ###########TEMPERATURE SCAN########################################
        TemperatureButton = tk.Button(self, text = "O-Temperature test", command = lambda: RunOverTprotectionScan(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=True, PowerUnitID=self.PowerUnitID))
        TemperatureButton.grid(row = 7, column = 4, sticky = 'nsew')
        ##########################################################################################

        ### I2C ###########################################################
        I2CButton = tk.Button(self, text="I2C test", command = lambda: RunI2CTest(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=True, PowerUnitID=self.PowerUnitID))
        I2CButton.grid(row = 7, column = 5, sticky = 'nsew')
        ###################################################################

        ###########LATCH STATUS CHECK########################################
        LatchupStatusButton = tk.Button(self, text = "Latch test", command = lambda: RunLatchupCheck(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=True, PowerUnitID=self.PowerUnitID))
        LatchupStatusButton.grid(row = 7, column = 6, sticky = 'nsew')
        ##########################################################################################

        ######### BIAS VOLTAGE SCAN ###################################################################
        BiasVoltageScanButton = tk.Button(self, text="Bias scan", command = lambda: RunBiasVoltageScan(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=True, PowerUnitID=self.PowerUnitID))
        BiasVoltageScanButton.grid(row = 8, column = 4, sticky = 'nsew')
        ###########################################################################################

        ######### POWER VOLTAGE SCAN ###################################################################
        PowerVoltageButton = tk.Button(self, text="Power scan", command = lambda: RunPowerVoltageScan(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=True, PowerUnitID=self.PowerUnitID))
        PowerVoltageButton.grid(row = 8, column = 5, sticky = 'nsew')
        ###########################################################################################

        ###########THRESHOLD SCAN########################################
        ThresholdScanButton = tk.Button(self, text = "Threshold scan", command = lambda: RunThresholdScan(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=True, PowerUnitID=self.PowerUnitID))
        ThresholdScanButton.grid(row = 8, column = 6, sticky = 'nsew')
        #############################################################################

        ######### RUN ALL TESTS  #########################################################
        tk.Label(self, text = "Full test procedure (on both power units)", fg="black").grid(row = 9, column = 4, columnspan = 3)
        #######################################################################################
        
        ### Run all test buttons ##########################################################
        RunAllTestsButton = tk.Button(self, text="Run All Tests", command = lambda: RunAllScans(timestamp=time.strftime("%Y%m%dT%H%M%S"), saveToFile=True))
        RunAllTestsButton.grid(row = 10, column = 5, sticky = 'nsew')
        #StopAllTestsButton = tk.Button(self, text="Stop All Tests", command = StopAllScans, state = 'disabled')
        #StopAllTestsButton.grid(row = 9, column = 6, sticky = 'nsew')
        ###################################################################################

        ########### PUSH DATA BUTTON  ######################################
        def PushDataToRepo():
            subprocess.call(['/bin/bash', '-c', "cd .."])
            subprocess.call(['/bin/bash', '-c', "git add *"])
            subprocess.call(['/bin/bash', '-c', "git commit -m \"updating results\""])
            subprocess.call(['/bin/bash', '-c', "git push origin master"])
            print "Done pushing data to the repo"
            
        PushDataToRepoButton = tk.Button(self, text = "Push Data", command = PushDataToRepo)
        PushDataToRepoButton.grid(row = 10, column = 6, sticky = 'nsew')
        #############################################################################

        ### Reports text field (PU RIGHT) #################################################
        reportsRightTitle = tk.Label(self, text = "Power Unit Right Qualification: None", fg="black")
        reportsRightTitle.grid(row = 13, column = 1, columnspan = 4, sticky='sw')
        reportsRight = tk.Text(self, width = 70, height = 7, state='disabled')
        reportsRight.grid(row = 14, column = 1, rowspan = 7, columnspan = 5, sticky = 'wne')
        ###################################################################################

        ########### PLOT VOLTAGE SCAN BUTTON ########################################
        PlotVoltageScanButton = tk.Button(self, text = "Plot Power scan", command = lambda: PlotPowerVoltageScanData('JUNK/PowerVoltageScan_PowerUnitRight.txt'))
        PlotVoltageScanButton.grid(row = 14, column = 6, sticky = 'nsew')
        #############################################################################

        ########### PLOT BIAS SCAN BUTTON ###########################################
        PlotBiasScanButton = tk.Button(self, text = "Plot Bias scan", command = lambda: PlotBiasVoltageScanData('JUNK/BiasVoltageScan_PowerUnitRight.txt'))
        PlotBiasScanButton.grid(row = 15, column = 6, sticky = 'nsew')
        #############################################################################

        ########### PLOT THRESHOLD SCAN BUTTON ######################################
        PlotThresholdScanButton = tk.Button(self, text = "Plot Thres scan", command = lambda: PlotThresholdScanData('JUNK/ThresholdScan_PowerUnitRight.txt'))
        PlotThresholdScanButton.grid(row = 16, column = 6, sticky = 'nsew')
        #############################################################################

        ### Reports text field (PU Left) ##################################################
        reportsLeftTitle = tk.Label(self, text = "Power Unit Left Qualification: None", fg="black")
        reportsLeftTitle.grid(row = 21, column = 1, columnspan = 4, sticky='sw')
        reportsLeft = tk.Text(self, width = 70, height = 7, state='disabled')
        reportsLeft.grid(row = 22, column = 1, rowspan = 7, columnspan = 5, sticky = 'wne')
        ###################################################################################

        ########### PLOT VOLTAGE SCAN BUTTON ########################################
        PlotVoltageScanButton = tk.Button(self, text = "Plot Power scan", command = lambda: PlotPowerVoltageScanData('JUNK/PowerVoltageScan_PowerUnitLeft.txt'))
        PlotVoltageScanButton.grid(row = 22, column = 6, sticky = 'nsew')
        #############################################################################

        ########### PLOT BIAS SCAN BUTTON ###########################################
        PlotBiasScanButton = tk.Button(self, text = "Plot Bias scan", command = lambda: PlotBiasVoltageScanData('JUNK/BiasVoltageScan_PowerUnitLeft.txt'))
        PlotBiasScanButton.grid(row = 23, column = 6, sticky = 'nsew')
        #############################################################################

        ########### PLOT THRESHOLD SCAN BUTTON ######################################
        PlotThresholdScanButton = tk.Button(self, text = "Plot Thres scan", command = lambda: PlotThresholdScanData('JUNK/ThresholdScan_PowerUnitLeft.txt'))
        PlotThresholdScanButton.grid(row = 24, column = 6, sticky = 'nsew')
        #############################################################################

        #self.can = tk.Canvas(self, width = 160, height = 160, bg = 'black')
        #self.can.grid(row = 0, column = 0)
        #self.img = tk.PhotoImage("LargeScaleTest/GuiUtils/Lawrence-Berkley-Laboratory.gif")
        #self.label = tk.Label(image=self.img)
        #self.item = self.can.create_image(100, 100, image=self.img)

        #can = tk.Canvas(self, width = 160, height = 160, bg = 'black')
        #image = tk.Image('LargeScaleTest/GuiUtils/Lawrence-Berkley-Laboratory.jpeg')
        #pic = tk.PhotoImage(image)
        ##pic = tk.PhotoImage()
        #item = can.create_image(0, 0, image=pic)

##Actual MAIN FUNCTION
root = tk.Tk()
app = Application(master=root)
app.master.title("Production Power Board Testing GUI")
app.mainloop()
