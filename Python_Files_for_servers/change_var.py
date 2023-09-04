# ----------------------------------------------
# Script Recorded by ANSYS Electronics Desktop Version 2019.3.0
# 12:22:35  May 22, 2020
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

linew_str = "{:.9f}".format(float(linew))
slot1_x_str = "{:.9f}".format(float(slot1_x))
slot1_y_str = "{:.9f}".format(float(slot1_y))
slot2_x_str = "{:.9f}".format(float(slot2_x))
slot2_y_str = "{:.9f}".format(float(slot2_y))

oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:linew",
					"Value:="		, linew_str+"mm"
				]
			]
		]
	])
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:slot1_x",
					"Value:="		, slot1_x_str+"mm"
				]
			]
		]
	])
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:slot1_y",
					"Value:="		, slot1_y_str+"mm"
				]
			]
		]
	])
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:slot2_x",
					"Value:="		, slot2_x_str+"mm"
				]
			]
		]
	])
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:slot2_y",
					"Value:="		, slot2_y_str+"mm"
				]
			]
		]
	])
oProject.Save()