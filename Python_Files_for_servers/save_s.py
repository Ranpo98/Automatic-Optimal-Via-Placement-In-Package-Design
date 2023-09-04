# ----------------------------------------------
# Script Recorded by ANSYS Electronics Desktop Version 2019.3.0
# 20:26:33  May 22, 2020
# ----------------------------------------------
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.SetActiveProject("yi_ant1")
oDesign = oProject.SetActiveDesign("ant")

linew=4.0
slot1_x=5.0
slot1_y=30.0
slot2_x=30.0
slot2_y=0.01
outfile="ant_2495.s1p"

linew_str = "{:.9f}".format(float(linew))
slot1_x_str = "{:.9f}".format(float(slot1_x))
slot1_y_str = "{:.9f}".format(float(slot1_y))
slot2_x_str = "{:.9f}".format(float(slot2_x))
slot2_y_str = "{:.9f}".format(float(slot2_y))
flname = "/home/thong/Ansoft/yi_ant1_optim/"+outfile

oModule = oDesign.GetModule("Solutions")
oModule.ExportNetworkData("boxx=\'80mm\' boxy=\'80mm\' boxz=\'60mm\' gndslot_x=\'8mm\' gndslot_y=\'16mm\' gndx=\'50mm\' linew=\'"+linew_str+"mm\' linex=\'25mm\' patchx=\'30.63mm\' patchy=\'32.45mm\' porth=\'6mm\' portw=\'12mm\' slot1_x=\'"+slot1_x_str+"mm\' slot1_y=\'"+slot1_y_str+"mm\' slot2_x=\'"+slot2_x_str+"mm\' slot2_y=\'"+slot2_y_str+"mm\' sub1_x=\'8mm\' sub1_y=\'18mm\' subx=\'50mm\' suby=\'52mm\' subz=\'1.6mm\'", ["Setup1:Sweep"], 3, flname, 
	[
"All"
	], True, 50, "S", -1, 0, 15, True, True, False)
