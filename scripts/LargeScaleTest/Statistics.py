#!/usr/bin/python

from   array import array
import ROOT

columns = {}

columns["ThresholdScan"]   = ["ChannelNumber", "ThDAC", "VsetDAC", "V", "I", "R", "T", "LUState", "Timestamp"]
columns["VoltageScan"]     = ["ChannelNumber", "VsetDAC", "V", "Vrms", "dV", "I", "Irms", "dI", "R", "T", "LUState", "Timestamp"]
columns["BiasScan"]        = ["VsetDAC", "V", "Vrms", "dV", "I", "Irms", "dI", "R", "T", "LUState", "Timestamp"]

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
    def __init__(self, PowerUnitID, load, summary):
        Scan.__init__(self, "ThresholdScan", True)
        self.load          = load
        self.PowerUnitID   = PowerUnitID
        self.summary       = summary
        self.expectedLowerValues = self.params["tscanExpectedLowerValues"][self.load]
        self.expectedUpperValues = self.params["tscanExpectedUpperValues"][self.load]

    def visualizeAndCheck(self, showFits = False, displayData = False, saveToFile = False):
        hasProblem = False

        # setting up all of the arrays
        channels, thvsi = array('f'), array('f')  
        iints, islopes = array('f'), array('f')
        iintserr, islopeserr = array('f'), array('f')
        channelserr = array('f')
        fitgraphs = []

        
        ilowers = []
        iuppers = []
        for channelNumber in range(0, 16):
            channels.append(float(channelNumber))
            channelserr.append(0.0)
 
            # pulling relevant data
            dac, i = array('f'), array('f')

            for step in self.ChannelData[str(channelNumber)]:
                if float(step["VsetDAC"]) == 0:
                    ilowers.append(float(step["I"]))
                if float(step["VsetDAC"]) == 250:
                    iuppers.append(float(step["I"]))
                if (float(step["VsetDAC"]) > self.config["ThresholdScan_maxfit"][self.load]):
                    continue
                dac.append(float(step["ThDAC"]))
                i.append(float(step["I"]))
                
            idacgraph, idacfit = self._createAndFitGraph(dac, i, int(channelNumber)%8)
            islopes.append(idacfit.GetParameter(1))
            islopeserr.append(idacfit.GetParError(1))
            iints.append(idacfit.GetParameter(0))
            iintserr.append(idacfit.GetParError(0))

	    fitgraphs.append((idacgraph))

        if saveToFile:
            AppendThresholdToSummaryFile(self.summary, self.PowerUnitID, self.load, ilowers, iuppers, iints, islopes)

        # Checking errors of slopes
        if any([x > self._GetUpper("tslopeserr") for x in islopeserr]):
            hasProblem = True
            print "Threshold scan tslopeserr exceed limit. Limit: " + str(self._GetUpper("tslopeserr")) + ", Read values: " + str(islopeserr)
        # Checking errors of intercepts
        if any([x > self._GetUpper("tintserr") for x in iintserr]):
            hasProblem = True
            print "Threshold scan tintserr exceed limit. Limit: " + str(self._GetUpper("tintserr")) + ", Read values: " + str(iintserr)

        if showFits:
            datacanvas = ROOT.TCanvas("datacanvas", "Data and fits")

            imultigraph = ROOT.TMultiGraph()

            for graphs in fitgraphs:
                imultigraph.Add(graphs)

            imultigraph.Draw("ap")
            imultigraph.GetXaxis().SetTitle("Current Threshold [DAC]")
            imultigraph.GetYaxis().SetTitle("I")
            imultigraph.GetXaxis().SetLabelSize(0.07)
            imultigraph.GetYaxis().SetLabelSize(0.07)

        fitcanvas = ROOT.TCanvas("fitcanvas", "Fit results")
        fitcanvas.Divide(2,1)

        fitcanvas.cd(1)
        iintsgraph = ROOT.TGraphErrors(len(channels), channels, iints, channelserr, iintserr)
        iintsgraph.SetTitle("Intercept I vs Channel")
        iintsgraph.SetMarkerStyle(4)
        iintsgraph.GetXaxis().SetLimits(-1,17)
        if self._checkAndDraw(iintsgraph, iints, "tints"):
            hasProblem = True
            print "Threshold scan tints is outside boundaries. Boundaries: " + str(self._GetLower("tints")) + ", " + str(self._GetUpper("tints")) + ", Read values: " + str(iints)

        fitcanvas.cd(2)
        islopesgraph = ROOT.TGraphErrors(len(channels), channels, islopes, channelserr, islopeserr)
        islopesgraph.SetTitle("Slope I vs Channel")
        islopesgraph.SetMarkerStyle(4)
        islopesgraph.GetXaxis().SetLimits(-1,17)
        if self._checkAndDraw(islopesgraph, islopes, "tslopes"):
            hasProblem = True
            print "Threshold scan tslopes is outside boundaries. Boundaries: " + str(self._GetLower("tslopes")) + ", " + str(self._GetUpper("tslopes")) + ", Read values: " + str(islopes)
        if (displayData):
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

    def _checkParams(self, values, graphType):
        graphMin  = self._GetLower(graphType)
        graphMax  = self._GetUpper(graphType)

        exceedsRange = False
        for value in values:
	    if value > graphMax or value < graphMin:
	        exceedsRange = True

        return exceedsRange

    def _checkAndDraw(self, graph, values, graphType, drawOnly = False):
        graph.Draw("ap")
        if not drawOnly:
            graphMin  = self._GetLower(graphType)
            graphMax  = self._GetUpper(graphType)

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

            return exceedsRange

        return False

    def _GetLower(self, graphType):
        return self.expectedLowerValues[graphType]

    def _GetUpper(self, graphType):
        return self.expectedUpperValues[graphType]
 

class VoltageScan(Scan):
    def __init__(self):
        Scan.__init__(self, "VoltageScan", True)
        self.vslopesgraph  = []
        self.vintsgraph    = []
        self.ivslopesgraph = []
        self.islopesgraph  = []
        self.iintsgraph    = []
 
    def visualizeAndCheck(self, showFits = False):
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

        vlowers = []
        vuppers = []
        for channelNumber in range(0, 16):
            channels.append(float(channelNumber))
            channelserr.append(0.0)

            # pulling relevant data
            dac = array('f')
            v   = array('f')
            i   = array('f')

            for step in self.ChannelData[str(channelNumber)]:
                if int(step["VsetDAC"]) == 0:
                    vlowers.append(float(step["V"]))
                if int(step["VsetDAC"]) == 250:
                    vuppers.append(float(step["V"]))
                # Skip what is above max fit value
                if int(step["VsetDAC"]) > 250:
                    continue

                # Fill data structures
                dac.append(float(step["VsetDAC"]))
                v.append(float(step["V"]))
                i.append(float(step["I"]))
                bin = vrms.FindBin(float(step["VsetDAC"]), float(channelNumber))
                vrms.SetBinContent(bin, float(step["Vrms"]))
                irms.SetBinContent(bin, float(step["Irms"]))

            # Creating and fitting each graph
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

        # Voltage intercepts and checks
        fitcanvas.cd(1)
        vintsgraph = ROOT.TGraphErrors(len(channels), channels, vints, channelserr, vintserr)
        vintsgraph.SetTitle("Intercept [V] vs Channel")
        vintsgraph.SetMarkerStyle(4)
        vintsgraph.GetXaxis().SetLimits(-1,17)

        # Voltage slopes and checks
        fitcanvas.cd(2)
        vslopesgraph = ROOT.TGraphErrors(len(channels), channels, vslopes, channelserr, vslopeserr)
        vslopesgraph.SetTitle("Slope V vs Channel")
        vslopesgraph.SetMarkerStyle(4)
        vslopesgraph.GetXaxis().SetLimits(-1,17)
        vslopesgraph.GetYaxis().SetLabelSize(0.07)

        # Inverse of loads no checks
        fitcanvas.cd(3)
        ivslopesgraph = ROOT.TGraphErrors(len(channels), channels, ivslopes, channelserr, ivslopeserr)
        ivslopesgraph.SetTitle("Load [#Omega] vs Channel")
        ivslopesgraph.SetMarkerStyle(4)
        ivslopesgraph.GetXaxis().SetLimits(-1,17)
        ivslopesgraph.Draw("ap")
        ivslopesgraph.GetXaxis().SetLabelSize(0.07)
        ivslopesgraph.GetYaxis().SetLabelSize(0.07)

        # Current intercepts and checks
        fitcanvas.cd(4)
        iintsgraph = ROOT.TGraphErrors(len(channels), channels, iints, channelserr, iintserr)
        iintsgraph.SetTitle("Intercept [I] vs Channel")
        iintsgraph.SetMarkerStyle(4)
        iintsgraph.GetXaxis().SetLimits(-1,17)
        iintsgraph.GetXaxis().SetLabelSize(0.07)
        iintsgraph.GetYaxis().SetLabelSize(0.07)

        # Current slopes and checks
        fitcanvas.cd(5)
        islopesgraph = ROOT.TGraphErrors(len(channels), channels, islopes, channelserr, islopeserr)
        islopesgraph.SetTitle("Slope I vs Channel")
        islopesgraph.SetMarkerStyle(4)
        islopesgraph.GetXaxis().SetLimits(-1,17)
        islopesgraph.GetXaxis().SetLabelSize(0.07)
        islopesgraph.GetYaxis().SetLabelSize(0.07)

        rmscanvas = ROOT.TCanvas("rmscanvas", "RMS measurements")
        rmscanvas.Divide(2,1)
        rmscanvas.cd(1)
        vrms.Draw("COLZ")
        rmscanvas.cd(2)
        irms.Draw("COLZ")

        return vints, vslopes, ivslopes, iints, islopes

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
        graph_sub.SetMarkerColor(color)
        graph_sub.SetLineColor(color)
        graph_sub.SetMarkerStyle(4)
        return graph_sub

class BiasScan(Scan):
    def __init__(self):
        Scan.__init__(self, "BiasScan", False)
        self.vgraph = []
        self.igraph = []

    def visualizeAndCheck(self):
        hasProblem = False

        dac, v, i, vrms, dv, irms, di = array('f'), array('f'), array('f'), array('f'), array('f'), array('f'), array('f')
        vlower = 0.
        vuuper = 0.
        for step in self.Data:
	    if int(step["VsetDAC"]) == 130:
                vlower = float(step["V"])
	    if int(step["VsetDAC"]) == 0:
                vupper = float(step["V"])
            # Skip what is above max fit value
            if float(step["I"]) == 0.0:
                continue
            #if int(step["VsetDAC"]) > self.config["BiasScan_maxfit"][self.load]:
            #    continue
            
            # Fill data structures
            dac.append(float(step["VsetDAC"]))
            v.append(float(step["V"]))
            i.append(float(step["I"]))
            vrms.append(float(step["Vrms"]))
            dv.append(float(step["dV"]))
            irms.append(float(step["Irms"]))
            di.append(float(step["dI"]))

        vgraph, vfit = self._createAndFitGraph(dac, v)
        vslope    = vfit.GetParameter(1)
        vslopeerr = vfit.GetParError(1)
        vint    = vfit.GetParameter(0)
        vinterr = vfit.GetParError(0)
        igraph, ifit = self._createAndFitGraph(dac, i)
        islope    = ifit.GetParameter(1)
        islopeerr = ifit.GetParError(1)
        iint    = ifit.GetParameter(0)
        iinterr = ifit.GetParError(0)
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

        return vint, vslope, iint, islope

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
        graph_sub.SetMarkerColor(color)
        graph_sub.SetLineColor(color)
        graph_sub.SetMarkerStyle(4)
        return graph_sub

    def _setAxes(self, graph, xtitle, ytitle):
        graph.SetMarkerStyle(4)
        graph.SetTitle("")
        graph.GetXaxis().SetTitle(xtitle)
        graph.GetYaxis().SetTitle(ytitle)
