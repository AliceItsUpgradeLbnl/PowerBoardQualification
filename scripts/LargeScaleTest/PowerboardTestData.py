#!/usr/bin/env python

import PowerboardTestDB as db
import ROOT
from   array import array
import sys


columns = {}
columns["ThresholdScan"]   = ["ChannelNumber", "ThDAC", "VsetDAC", "V", "I", "R", "T", "LUState"]
columns["VoltageScan"]     = ["ChannelNumber", "VsetDAC", "V", "Vrms", "dV", "I", "Irms", "dI", "R", "T", "LUState"]
columns["BiasVoltageScan"] = ["VsetDAC", "V", "Vrms", "dV", "I", "Irms", "dI", "R", "T", "LUState"]
columns["TemperatureScan"] = ["Vavg", "Itot", "TBoard", "TAux1", "TAux2"]
columns["LatchupTest"]     = ["ChannelNumber", "BeforeEnabling", "AfterEnabling", "AfterLatching"]
columns["TestInfo"]        = ["BoardNumber", "BoardVersion", "TestNumber", "LoadType", "PowerUnit", "Config", "Tester", "Timestamp"]

class Scan(object):
    def __init__(self, testName, hasChannelData):
        self.Data = []
        self.columns = columns[testName]
        self.testName = testName
        self.hasChannelData = hasChannelData

    def readFile(self, filename):
        with open(filename) as f:
            for line in f:
                data = line.split()
                if len(data) == len(self.columns) and data[0].isdigit():
                    self.Data.append(dict(zip(self.columns, data)))
        if self.hasChannelData:
            self.buildChannelData()

    def readDB(self, boardNumber, testId=0):
        self.Data = db.getRows(testName, boardNumber, testId)
        if self.hasChannelData:
            self.buildChannelData()

    def buildChannelData(self):
        self.ChannelData = {}

        for step in self.Data:
            channelNumber = step["ChannelNumber"]
            if channelNumber not in self.ChannelData:
                self.ChannelData[channelNumber] = []
            self.ChannelData[channelNumber].append(step)

class ThresholdScan(Scan):
    def __init__(self):
        Scan.__init__(self, "ThresholdScan", True)

    def visualizeAndCheck(self, showFits=False):
        hasProblem = False

        # setting up all of the arrays
        channels, thvsi = array('f'), array('f')  
        fitgraphs = []

        for channelNumber, steps in self.ChannelData.iteritems():
            channels.append(float(channelNumber))
            channelserr.append(0.0) # What is this?

            # pulling relevant data
            dac, i = array('f'), array('f'), array('f')

            for step in steps:
                dac.append(float(step["ThDAC"]))
                i.append(float(step["I"]))
                
            idacgraph, idacfit = self._createAndFitGraph(dac, i, int(channelNumber)%8)
            islopes.append(idacfit.GetParameter(1))
            islopeserr.append(idacfit.GetParError(1))
            iints.append(idacfit.GetParameter(0))
            iintserr.append(idacfit.GetParError(0))

	    fitgraphs.append((idacgraph))

        if showFits:
            datacanvas = ROOT.TCanvas("datacanvas", "Data and fits")
            #datacanvas.Divide(1,3)

            imultigraph = ROOT.TMultiGraph()

            for graphs in fitgraphs:
                imultigraph.Add(graphs[1])

            imultigraph.Draw("ap")
            imultigraph.GetXaxis().SetTitle("Current Threshold [DAC]")
            imultigraph.GetYaxis().SetTitle("I")
            imultigraph.GetXaxis().SetLabelSize(0.07)
            imultigraph.GetYaxis().SetLabelSize(0.07)

        #fitcanvas = ROOT.TCanvas("fitcanvas", "Fit results")
        #fitcanvas.Divide(5,1)

        #fitcanvas.cd(1)
        #vintsgraph = ROOT.TGraphErrors(len(channels), channels, vints, channelserr, vintserr)
        #vintsgraph.SetTitle("Intercept [V] vs Channel")
        #vintsgraph.SetMarkerStyle(4)
        #vintsgraph.GetXaxis().SetLimits(-1,17)
        #self.vintsgraph = vintsgraph
        #vintsHasProblem = self._checkAndDraw(vintsgraph, vints, 0.1)
        #hasProblem = hasProblem or vintsHasProblem

        #fitcanvas.cd(2)
        #vslopesgraph = ROOT.TGraphErrors(len(channels), channels, vslopes, channelserr, vslopeserr)
        #vslopesgraph.SetTitle("Slope V vs Channel")
        #vslopesgraph.SetMarkerStyle(4)
        #vslopesgraph.GetXaxis().SetLimits(-1,17)
        #self.vslopesgraph = vslopesgraph
        #vslopesHasProblem = self._checkAndDraw(vslopesgraph, vslopes, 0.1)
        #vslopesgraph.GetXaxis().SetLabelSize(0.07)
        #vslopesgraph.GetYaxis().SetLabelSize(0.07)
        #hasProblem = hasProblem or vslopesHasProblem

        #fitcanvas.cd(3)
        #ivslopesgraph = ROOT.TGraphErrors(len(channels), channels, ivslopes, channelserr, ivslopeserr)
        #ivslopesgraph.SetTitle("Load [#Omega] vs Channel")
        #ivslopesgraph.SetMarkerStyle(4)
        #ivslopesgraph.GetXaxis().SetLimits(-1,17)
        #ivslopesgraph.Draw("ap")
        #ivslopesgraph.GetXaxis().SetLabelSize(0.07)
        #ivslopesgraph.GetYaxis().SetLabelSize(0.07)

        #self.ivslopesgraph = ivslopesgraph

        #fitcanvas.cd(4#)
        #iintsgraph = ROOT.TGraphErrors(len(channels), channels, iints, channelserr, iintserr)
        #iintsgraph.SetTitle("Intercept [I] vs Channel")
        #iintsgraph.SetMarkerStyle(4)
        #iintsgraph.GetXaxis().SetLimits(-1,17)
        #self.iintsgraph = iintsgraph
        #iintsHasProblem = self._checkAndDraw(iintsgraph, iints, 0.1)
        #iintsgraph.GetXaxis().SetLabelSize(0.07)
        #iintsgraph.GetYaxis().SetLabelSize(0.07)
        #hasProblem = hasProblem or iintsHasProblem

        #fitcanvas.cd(5)
        #islopesgraph = ROOT.TGraphErrors(len(channels), channels, islopes, channelserr, islopeserr)
        #islopesgraph.SetTitle("Slope I vs Channel")
        #islopesgraph.SetMarkerStyle(4)
        #islopesgraph.GetXaxis().SetLimits(-1,17)
        #self.islopesgraph = islopesgraph
        #islopesHasProblem = self._checkAndDraw(islopesgraph, islopes, 0.1)
        #islopesgraph.GetXaxis().SetLabelSize(0.07)
        #islopesgraph.GetYaxis().SetLabelSize(0.07)
        #hasProblem = hasProblem or islopesHasProblem

        if (displayData):
            sys.stdin.flush()
            raw_input("Press enter to continue \n")

        return hasProblem
        
class VoltageScan(Scan):
    def __init__(self):
        Scan.__init__(self, "VoltageScan", True)
        self.vslopesgraph = []
        self.vintsgraph = []
        self.ivslopesgraph = []
        self.islopesgraph = []
        self.iintsgraph = []
        self.expectedValues = {"vintsana": 1.63, "vintsdig": 1.63, "vslopesana": 0.00495, "vslopesdig": 0.00495, \
                               "ivintsana": 1., "ivintsdig": 1., "ivslopesana": 10., "ivslopesdig": 2.2, \
                               "iintsana": 0.16, "iintsdig": 0.73, "islopesana": 0.0005, "islopesdig": 0.00215}

        self.toleranceValues = {"vintsana": 0.1, "vintsdig": 0.1, "vslopesana": 0.1, "vslopesdig": 0.1, \
                                "ivintsana": 0.1, "ivintsdig": 0.1, "ivslopesana": 0.1, "ivslopesdig": 0.1, \
                                "iintsana": 0.1, "iintsdig": 0.1, "islopesana": 0.1, "islopesdig": 0.1}
 
    def visualizeAndCheck(self, showFits=False, displayData=False):
        hasProblem = False

        # setting up all of the arrays
        channels, vints, vslopes, ivslopes, iints, islopes = array('f'), array('f'), array('f'), array('f'), array('f'), array('f')  
        channelserr, vintserr, vslopeserr, ivslopeserr, iintserr, islopeserr = array('f'), array('f'), array('f'), array('f'), array('f'), array('f')
        fitgraphs = []

        # a rather ugly way of getting the number of bins
        nSteps = len(self.ChannelData.values()[0])
        vrms = ROOT.TH2F("vrms", "V RMS", nSteps, 0, 256, 16, 0, 16)
        irms = ROOT.TH2F("irms", "I RMS", nSteps, 0, 256, 16, 0, 16)
        vrms.SetMaximum(5)
        irms.SetMaximum(5)

        for channelNumber in range(0, 16):
            channels.append(float(channelNumber))
            channelserr.append(0.0)

            # pulling relevant data
            dac = array('f')
            v   = array('f')
            i   = array('f')

            for step in self.ChannelData[str(channelNumber)]:
                dac.append(float(step["VsetDAC"]))
                v.append(float(step["V"]))
                i.append(float(step["I"]))
                
                bin = vrms.FindBin(float(step["VsetDAC"]), float(channelNumber))
                vrms.SetBinContent(bin, float(step["Vrms"]))
                irms.SetBinContent(bin, float(step["Irms"]))

            # creating and fitting each graph
            vdacgraph, vdacfit = self._createAndFitGraph(dac, v, int(channelNumber)%8)
            vslopes.append(vdacfit.GetParameter(1))
            vslopeserr.append(vdacfit.GetParError(1))
            vints.append(vdacfit.GetParameter(0))
            vintserr.append(vdacfit.GetParError(0))
            vdacgraph_subtracted = self._subtractFit(vdacgraph, vdacfit, int(channelNumber)%8)

            ivgraph, ivfit = self._createAndFitGraph(i, v, int(channelNumber)%8)
            ivslopes.append(ivfit.GetParameter(1))
            ivslopeserr.append(ivfit.GetParError(1))

            idacgraph, idacfit = self._createAndFitGraph(dac, i, int(channelNumber)%8)
            islopes.append(idacfit.GetParameter(1))
            islopeserr.append(idacfit.GetParError(1))
            iints.append(idacfit.GetParameter(0))
            iintserr.append(idacfit.GetParError(0))

            #fitgraphs.append((vdacgraph, ivgraph, idacgraph, ))
	    fitgraphs.append((vdacgraph, ivgraph, idacgraph, vdacgraph_subtracted))

        if showFits:
            datacanvas = ROOT.TCanvas("datacanvas", "Data and fits")
            datacanvas.Divide(1,3)

            vmultigraph, ivmultigraph, imultigraph = ROOT.TMultiGraph(), ROOT.TMultiGraph(), ROOT.TMultiGraph()
            vmultigraph_sub =  ROOT.TMultiGraph()

            for graphs in fitgraphs:
                vmultigraph.Add(graphs[0])
                ivmultigraph.Add(graphs[1])
                imultigraph.Add(graphs[2])
		vmultigraph_sub.Add(graphs[3])

            datacanvas.cd(1)
            vmultigraph.Draw("ap")
            vmultigraph.GetXaxis().SetTitle("VsetDAC")
            vmultigraph.GetYaxis().SetTitle("V")
            vmultigraph.GetXaxis().SetLabelSize(0.07)
            vmultigraph.GetYaxis().SetLabelSize(0.07)
            datacanvas.cd(2)
            vmultigraph_sub.Draw("APL")
            vmultigraph_sub.GetXaxis().SetTitle("VsetDAC")
            vmultigraph_sub.GetYaxis().SetTitle("V - Fit")
            vmultigraph_sub.GetXaxis().SetLabelSize(0.07)
            vmultigraph_sub.GetYaxis().SetLabelSize(0.07)
            datacanvas.cd(3)
            ivmultigraph.Draw("ap")
            ivmultigraph.GetXaxis().SetTitle("I")
            ivmultigraph.GetYaxis().SetTitle("V")
            ivmultigraph.GetXaxis().SetLabelSize(0.07)
            ivmultigraph.GetYaxis().SetLabelSize(0.07)
            datacanvas.cd(4)
            imultigraph.Draw("ap")
            imultigraph.GetXaxis().SetTitle("VsetDAC")
            imultigraph.GetYaxis().SetTitle("I")
            imultigraph.GetXaxis().SetLabelSize(0.07)
            imultigraph.GetYaxis().SetLabelSize(0.07)

        fitcanvas = ROOT.TCanvas("fitcanvas", "Fit results")
        fitcanvas.Divide(5,1)

        fitcanvas.cd(1)
        vintsgraph = ROOT.TGraphErrors(len(channels), channels, vints, channelserr, vintserr)
        vintsgraph.SetTitle("Intercept [V] vs Channel")
        vintsgraph.SetMarkerStyle(4)
        vintsgraph.GetXaxis().SetLimits(-1,17)
        #self.vintsgraph = vintsgraph
        vintsHasProblem = self._checkAndDraw(vintsgraph, vints[0::2], "vintsana")
        hasProblem = hasProblem or vintsHasProblem
        vintsHasProblem = self._checkAndDraw(vintsgraph, vints[1::2], "vintsdig")
        hasProblem = hasProblem or vintsHasProblem

        fitcanvas.cd(2)
        vslopesgraph = ROOT.TGraphErrors(len(channels), channels, vslopes, channelserr, vslopeserr)
        vslopesgraph.SetTitle("Slope V vs Channel")
        vslopesgraph.SetMarkerStyle(4)
        vslopesgraph.GetXaxis().SetLimits(-1,17)
        #self.vslopesgraph = vslopesgraph
        vslopesgraph.GetXaxis().SetLabelSize(0.07)
        vslopesgraph.GetYaxis().SetLabelSize(0.07)
        vslopesHasProblem = self._checkAndDraw(vslopesgraph, vslopes[0::2], "vslopesana")
        hasProblem = hasProblem or vslopesHasProblem
        vslopesHasProblem = self._checkAndDraw(vslopesgraph, vslopes[1::2], "vslopesdig")
        hasProblem = hasProblem or vslopesHasProblem

        fitcanvas.cd(3)
        ivslopesgraph = ROOT.TGraphErrors(len(channels), channels, ivslopes, channelserr, ivslopeserr)
        ivslopesgraph.SetTitle("Load [#Omega] vs Channel")
        ivslopesgraph.SetMarkerStyle(4)
        ivslopesgraph.GetXaxis().SetLimits(-1,17)
        ivslopesgraph.Draw("ap")
        ivslopesgraph.GetXaxis().SetLabelSize(0.07)
        ivslopesgraph.GetYaxis().SetLabelSize(0.07)
        ivslopesHasProblem = self._checkAndDraw(ivslopesgraph, ivslopes[0::2], "ivslopesana")
        hasProblem = hasProblem or ivslopesHasProblem
        ivslopesHasProblem = self._checkAndDraw(ivslopesgraph, ivslopes[1::2], "ivslopesdig")
        hasProblem = hasProblem or ivslopesHasProblem

        #self.ivslopesgraph = ivslopesgraph

        fitcanvas.cd(4)
        iintsgraph = ROOT.TGraphErrors(len(channels), channels, iints, channelserr, iintserr)
        iintsgraph.SetTitle("Intercept [I] vs Channel")
        iintsgraph.SetMarkerStyle(4)
        iintsgraph.GetXaxis().SetLimits(-1,17)
        iintsgraph.GetXaxis().SetLabelSize(0.07)
        iintsgraph.GetYaxis().SetLabelSize(0.07)
        iintsHasProblem = self._checkAndDraw(iintsgraph, iints[0::2], "iintsana")
        hasProblem = hasProblem or iintsHasProblem
        iintsHasProblem = self._checkAndDraw(iintsgraph, iints[1::2], "iintsdig")
        hasProblem = hasProblem or iintsHasProblem
        #self.iintsgraph = iintsgraph

        fitcanvas.cd(5)
        islopesgraph = ROOT.TGraphErrors(len(channels), channels, islopes, channelserr, islopeserr)
        islopesgraph.SetTitle("Slope I vs Channel")
        islopesgraph.SetMarkerStyle(4)
        islopesgraph.GetXaxis().SetLimits(-1,17)
        #self.islopesgraph = islopesgraph
        islopesgraph.GetXaxis().SetLabelSize(0.07)
        islopesgraph.GetYaxis().SetLabelSize(0.07)
        islopesHasProblem = self._checkAndDraw(islopesgraph, islopes[0::2], "islopesana")
        hasProblem = hasProblem or islopesHasProblem
        islopesHasProblem = self._checkAndDraw(islopesgraph, islopes[1::2], "islopesdig")
        hasProblem = hasProblem or islopesHasProblem

        rmscanvas = ROOT.TCanvas("rmscanvas", "RMS measurements")
        rmscanvas.Divide(2,1)
        rmscanvas.cd(1)
        vrms.Draw("COLZ")
        rmscanvas.cd(2)
        irms.Draw("COLZ")

        if displayData:
            sys.stdin.flush()
            raw_input("Press enter to continue \n")

        return hasProblem

    def _createAndFitGraph(self, x, y, color):
        graph = ROOT.TGraph(len(x), x, y)
        graph.Fit('pol1', 'q')
        fit = graph.GetFunction('pol1')
        graph.SetMarkerStyle(4)
        graph.SetMarkerColor(color)
        fit.SetLineColor(color)
	
        return (graph, fit)

    def _subtractFit(self,graph,fit,color):

        graph_sub = ROOT.TGraph(graph.GetN())
        for n in range(graph.GetN()):
            x = ROOT.Double()
            y = ROOT.Double()
            graph.GetPoint(n,x,y)
            ysub = y-fit.Eval(x)
            graph_sub.SetPoint(n, x, ysub)
            #print x
            #print 'ysub = %2.4f, y=%2.4f, eval =%2.4f'%(ysub,y,fit.Eval(x))   
        graph_sub.SetMarkerColor(color)
        graph_sub.SetLineColor(color)
        graph_sub.SetMarkerStyle(4)
        return graph_sub

    def _checkAndDraw(self, graph, values, graphType):
        graph.Draw("ap")
        #graph.Fit('pol0', 'q0')
        #fit = graph.GetFunction('pol0')
        #center = fit.GetParameter(0)
        expected  = self._GetExpected(graphType)
        tolerance = self._GetTolerance(graphType)
        graphMin  = (1-tolerance)*expected
        graphMax  = (1+tolerance)*expected

        exceedsRange = False
        for value in values:
            if value > graphMax or value < graphMin:
                exceedsRange = True

        if exceedsRange:
            # draw dashed horizontal lines indicating the tolerance
            # actually, turn everything red, because ROOT is a pain
            graph.SetMarkerColor(2)
            graph.SetMarkerStyle(20)
            graph.SetLineColor(2)
            graph.SetFillColor(2)
            # rescale the axes
            #graph.SetMinimum(graphMin)
            #graph.SetMaximum(graphMax)       

        #raw_input("Press enter to continue")

        return exceedsRange

    def _GetExpected(self, graphType):
        return self.expectedValues[graphType]

    def _GetTolerance(self, graphType):
        return self.toleranceValues[graphType]

class BiasVoltageScan(Scan):
    def __init__(self):
        Scan.__init__(self, "BiasVoltageScan", False)
        self.vgraph = []
        self.igraph = []

    def visualizeAndCheck(self, displayData=False):
        hasProblem = False

        dac, v, i, dv, di = array('f'), array('f'), array('f'), array('f'), array('f')
        for step in self.Data:
            dac.append(float(step["VsetDAC"]))
            v.append(float(step["V"]))
            i.append(float(step["I"]))
            dv.append(float(step["dV"]))
            di.append(float(step["dI"]))

        vgraph, vfit = self._createAndFitGraph(dac, v)
        igraph, ifit = self._createAndFitGraph(dac, i)
        vgraph_subtracted = self._subtractFit(vgraph, vfit, 4)
        igraph_subtracted = self._subtractFit(igraph, ifit, 4)
        self.vgraph = vgraph
        self.igraph = igraph
        dvgraph = ROOT.TGraph(len(dac), dac, dv)
        digraph = ROOT.TGraph(len(dac), dac, di)

        biascanvas = ROOT.TCanvas("biascanvas", "Bias voltage scan results")
        biascanvas.Divide(2,2)

        biascanvas.cd(1)
        vgraph.Draw("ap")
        self._setAxes(vgraph, "VsetDAC", "Voltage [V]")

        biascanvas.cd(2)
        igraph.Draw("ap")
        self._setAxes(igraph, "VsetDAC", "Current [A]")

        biascanvas.cd(3)
        dvgraph.Draw("ap")
        self._setAxes(dvgraph, "VsetDAC", "Noise [mV]")

        biascanvas.cd(4)
        digraph.Draw("ap")
        self._setAxes(digraph, "VsetDAC", "Noise [mA]")

        if displayData:
            sys.stdin.flush()
            raw_input("Press enter to continue")

        return hasProblem

    def _createAndFitGraph(self, x, y):
        graph = ROOT.TGraph(len(x), x, y)
        #graph.Fit('pol1')
        #return graph

        graph.Fit('pol1', 'q')
        fit = graph.GetFunction('pol1')
        graph.SetMarkerStyle(4)
        graph.SetMarkerColor(1)
        fit.SetLineColor(2)
	
        return (graph, fit)

    def _subtractFit(self,graph,fit,color):

        graph_sub = ROOT.TGraph(graph.GetN())
        for n in range(graph.GetN()):
            x = ROOT.Double()
            y = ROOT.Double()
            graph.GetPoint(n,x,y)
            ysub = y-fit.Eval(x)
            graph_sub.SetPoint(n, x, ysub)
            #print x
            #print 'ysub = %2.4f, y=%2.4f, eval =%2.4f'%(ysub,y,fit.Eval(x))   
        graph_sub.SetMarkerColor(color)
        graph_sub.SetLineColor(color)
        graph_sub.SetMarkerStyle(4)
        return graph_sub

    def _setAxes(self, graph, xtitle, ytitle):
        graph.SetMarkerStyle(4)
        graph.SetTitle("")
        graph.GetXaxis().SetTitle(xtitle)
        graph.GetYaxis().SetTitle(ytitle)

class TemperatureScan(Scan):
    def __init__(self):
        Scan.__init__(self, "TemperatureScan", False)

class LatchupTest(Scan):
    def __init__(self):
        Scan.__init__(self, "LatchupTest", False)

class TestInfo(object):
    def __init__(self):
        self.Data = {}

    def parseFilename(self, filename):
        metadata = filename.split("_")

        self.Data["Timestamp"] = metadata[0]
        # strip off "BoardID"
        self.Data["BoardNumber"] = metadata[1][7:]
        # strip off "v"
        self.Data["BoardVersion"] = metadata[2][1:]
        # strip off "PowerUnitID"
        self.Data["PowerUnit"] = metadata[3][11:]
        # strip off "LoadType"
        self.Data["LoadType"] = metadata[4][8:]
        # strip off "Config"
        self.Data["Config"] = metadata[5][6:]
        # strip off ".txt"
        self.Data["Tester"] = metadata[7][:-4]

    def readDB(self, boardNumber, testId=0):
        self.Data = db.getRows("TestInfo", boardNumber, testId)[0]
        self.Id = self.Data["Id"]
