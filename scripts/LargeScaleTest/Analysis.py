import sys
import PowerboardTestData
import ROOT

#Irradiation
#namebefore = "../TXTFILES/20170725T180147_BoardID19_v1.1_PowerUnitID2_LoadType2_Config6_VoltageScan_Joshua.txt"
#nameafter = "../TXTFILES/20170926T113831_BoardID19_v1.1_PowerUnitID2_LoadType2_Config6_VoltageScan_Miguel.txt"

#Control
#namebefore = "../TXTFILES/20170920T142830_BoardID25_v1.1_PowerUnitID1_LoadType2_Config6_VoltageScan_Miguel.txt"
#namebefore = "../TXTFILES/20170727T175143_BoardID25_v1.1_PowerUnitID1_LoadType2_Config6_VoltageScan_Joshua.txt"
#nameafter = "../TXTFILES/20170927T145558_BoardID25_v1.1_PowerUnitID1_LoadType2_Config6_VoltageScan_Miguel.txt"

namebefore = "../TXTFILES/20170727T180140_BoardID25_v1.1_PowerUnitID1_LoadType3_Config6_VoltageScan_Joshua.txt"
nameafter = "../TXTFILES/20170927T150126_BoardID25_v1.1_PowerUnitID1_LoadType3_Config6_VoltageScan_Miguel.txt"

vs_after = PowerboardTestData.VoltageScan()
vs_after.readFile(nameafter)
vs_after.visualizeAndCheck(True)

vs_before = PowerboardTestData.VoltageScan()
vs_before.readFile(namebefore)
vs_before.visualizeAndCheck(True)


raw_input('Voltage Scan - voltage measurements')

c = ROOT.TCanvas()
c.Divide(2)
c.cd(1)
vs_after.vslopesgraph.Draw("AP")
vs_before.vslopesgraph.SetMarkerColor(2)
vs_before.vslopesgraph.Draw("Psame")
vs_after.vslopesgraph.Print()

c.cd(2)

vs_after.vintsgraph.Draw("AP")
vs_after.vintsgraph.SetMaximum(1.65)
vs_after.vintsgraph.SetMinimum(1.58)

vs_before.vintsgraph.SetMarkerColor(2)
vs_before.vintsgraph.Draw("Psame")
vs_after.vintsgraph.Print()

#c.cd(3)

#vs_after.ivslopesgraph.Draw("AP")
#vs_before.ivslopesgraph.SetMarkerColor(2)
#vs_before.ivslopesgraph.Draw("Psame")
#vs_after.ivslopesgraph.Print()
c.SaveAs("VoltageScan_VoltageMeasurements.pdf")

raw_input('Voltage Scan - current measurements')

d = ROOT.TCanvas()
d.Divide(2)
d.cd(1)
vs_after.islopesgraph.SetMarkerColor(1)
vs_after.islopesgraph.Draw("AP")
vs_before.islopesgraph.SetMarkerColor(2)
vs_before.islopesgraph.Draw("Psame")
vs_after.islopesgraph.Print()

d.cd(2)

vs_after.iintsgraph.SetMarkerColor(1)
vs_after.iintsgraph.Draw("AP")
vs_after.iintsgraph.SetMaximum(1.7)
vs_after.iintsgraph.SetMinimum(0.2)

vs_before.iintsgraph.SetMarkerColor(2)
vs_before.iintsgraph.Draw("Psame")
vs_after.iintsgraph.Print()
d.SaveAs("VoltageScan_CurrentMeasurements.pdf")

##DO BIAS SCAN

namebefore = "../TXTFILES/20170725T181717_BoardID19_v1.1_PowerUnitID1_LoadType1_Config6_BiasVoltageScan_Joshua.txt"
nameafter = "../TXTFILES/20170926T114452_BoardID19_v1.1_PowerUnitID1_LoadType1_Config6_BiasVoltageScan_Miguel.txt"

print ' About to do bias scan voltage' 
bs_after = PowerboardTestData.BiasVoltageScan()
bs_after.readFile(nameafter)
bs_after.visualizeAndCheck()


bs_before= PowerboardTestData.BiasVoltageScan()
bs_before.readFile(namebefore)
bs_before.visualizeAndCheck()

c.Clear()
bs_after.vgraph.Draw("AP")
bs_after.vgraph.GetFunction("pol1").SetLineColor(1)
bs_before.vgraph.SetMarkerColor(2)
bs_before.vgraph.Draw("Psame")
c.SaveAs("biasVResults.pdf")


bs_after.igraph.Draw("AP")
bs_after.igraph.GetFunction("pol1").SetLineColor(1)
bs_before.igraph.SetMarkerColor(2)
bs_before.igraph.Draw("Psame")


c.SaveAs("biasIResults.pdf")


