#########################################################################
# File Name: xmon_sim_plane.py
# Description: This is the initialization module for simulating Xmon qubits.
#             It includes the simulation of qubits and the calculation of coupling.
#########################################################################

# Import necessary simulation libraries
import win32com.client  # Import win32com library
from addict import Dict
import os
import pathlib
import re
import pandas as pd
from IPython.display import display
import numpy as np  # Import numpy library

# Import physical constants
e = 1.60217657e-19  # Elementary charge
h = 6.62606957e-34  # Planck's constant
hbar = 1.0545718E-34  # Reduced Planck's constant
phinot = 2.067 * 1E-15  # Magnetic flux quantum
phi0 = phinot / (2 * np.pi)  # Reduced magnetic flux quantum
c = 3 * 10 ** 8  # Speed of light


def simulation(qubit, path):
    """
    Main function for simulating Xmon qubits.

    Inputs:
        qubit: Object, describes the parameters of the qubit.
        path: String, the storage path for the simulation result files.

    Outputs:
        Cq: Float, the capacitance parameter of the qubit (femtofarads).
        Ec: Float, the Josephson energy of the qubit (hertz).
    """
    ############################### Interface ########################################
    # a = Xmon(x=0,y=0,Q_name='123')      # Instantiate once
    q_name = qubit.name
    width = qubit.cross_width
    height = qubit.cross_height
    gap = qubit.cross_gap
    cl = qubit.claw_length
    gs = qubit.ground_spacing
    cw = qubit.claw_width
    cg = qubit.claw_gap
    in_s = (cl * 2 + cw - width - gap * 2) / 2
    x = 0 - height - width / 2
    y = 0 - width / 2
    # x_m = -155
    # y_m = -5

    x1 = -gap - gs
    y1 = width + gap + in_s
    x2 = height * 2 + width + gap + gs
    y2 = width + gap + in_s
    x3 = height - gap - in_s
    y3 = width + gap + height + gs
    x4 = height + gap + width + in_s
    y4 = -height - gap - gs

    # xiao_r = ctl.radius
    # da_r =  ctl.radius + ctl.gap

    A = int(qubit.coupling_qubits.right != None)
    B = int(qubit.coupling_qubits.top != None)
    C = int(qubit.coupling_qubits.left != None)
    D = int(qubit.coupling_qubits.bot != None)

    ############################################################################

    oAnsoftApp = win32com.client.Dispatch('AnsoftHfss.HfssScriptInterface')
    oDesktop = oAnsoftApp.GetAppDesktop()
    oProject = oDesktop.NewProject()
    oProject.InsertDesign("Q3D Extractor", '123', "", "")
    oDesign = oProject.SetActiveDesign('123')  # "Q3DDesign1"

    # Set up Analysis
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oModule = oDesign.GetModule("AnalysisSetup")
    oModule.InsertSetup("Matrix",
                        [
                            "NAME:Setup",
                            "AdaptiveFreq:=", "5GHz",
                            "SaveFields:=", False,
                            "Enabled:=", True,
                            [
                                "NAME:Cap",
                                "MaxPass:=", 15,
                                "MinPass:=", 2,
                                "MinConvPass:=", 2,
                                "PerError:=", 0.5,
                                "PerRefine:=", 30,
                                "AutoIncreaseSolutionOrder:=", True,
                                "SolutionOrder:=", "High",
                                "Solver Type:=", "Iterative"
                            ]
                        ])

    # Enlarge the square, add a box, add excitation (Q-chip)
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", str(x - 330) + "um",
            "YStart:=", str(y - 500) + "um",
            "ZStart:=", "1e-05",
            "Width:=", "0.002000",  # Base of 1000*1000
            "Height:=", "0.002000",
            "WhichAxis:=", "Z"
        ],
        [
            "NAME:Attributes",
            "Name:=", "ground_Q_chip_plane",
            "Flags:=", "",
            "Color:=", "(143 175 143)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"copper\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", False,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:=", str(x - 330) + "um",
            "YPosition:=", str(y - 500) + "um",
            "ZPosition:=", "-0.00027",
            "XSize:=", "0.002000",  # Box of 1000*1000
            "YSize:=", "0.002000",
            "ZSize:=", "0.00028"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Q_chip",
            "Flags:=", "",
            "Color:=", "(186 186 205)",
            "Transparency:=", 0.2,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"silicon\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", False,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])
    # Connect points, this is for the bit
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.CreatePolyline(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DAttributeTab",
                [
                    "NAME:PropServers", 
                    "Polyline1"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Name",
                        "Value:="        , "bt_Xmon"
                    ]
                ]
            ]
        ])
    # Inside and out, the principle is the same - big or small.
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.CreatePolyline(
        [
            "NAME:PolylineParameters",
            "IsPolylineCovered:="    , True,
            "IsPolylineClosed:="    , True,
            [
                "NAME:PolylinePoints",
                ["NAME:PLPoint","X:=", str(-gap+x)+"um","Y:="    , str(width+gap+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(-gap+height+x)+"um","Y:="    , str(width+gap+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(-gap+height+x)+"um","Y:="    , str(width+gap+height+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(width+gap+height+x)+"um","Y:="    , str(width+gap+height+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(width+gap+height+x)+"um","Y:="    , str(width+gap+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(width+gap+height*2+x)+"um","Y:="    , str(width+gap+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(width+gap+height*2+x)+"um","Y:="    , str(-gap+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(width+gap+height+x)+"um","Y:="    , str(-gap+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(width+gap+height+x)+"um","Y:="    , str(-gap-height+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(height-gap+x)+"um","Y:="    , str(-gap-height+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(height-gap+x)+"um","Y:="    , str(-gap+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(-gap+x)+"um","Y:="    , str(-gap+y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(-gap+x)+"um","Y:="    , str(gap+width+y)+"um","Z:="    , "1e-5"],
            ],
            [
                "NAME:PolylineSegments",
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 0,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 1,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 2,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 3,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 4,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 5,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 6,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 7,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 8,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 9,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 10,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 11,"NoOfPoints:="        , 2],
                ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 12,"NoOfPoints:="        , 2],
            ],
            [
                "NAME:PolylineXSection",
                "XSectionType:="    , "None",
                "XSectionOrient:="    , "Auto",
                "XSectionWidth:="    , "0mm",
                "XSectionTopWidth:="    , "0mm",
                "XSectionHeight:="    , "0mm",
                "XSectionNumSegments:="    , "0",
                "XSectionBendType:="    , "Corner"
            ]
        ], 
        [
            "NAME:Attributes",
            "Name:="        , "Polyline1",
            "Flags:="        , "",
            "Color:="        , "(143 175 143)",
            "Transparency:="    , 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:="        , "",
            "MaterialValue:="    , "\"copper\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:="        , False,
            "ShellElement:="    , False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:="    , True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:="    , False
        ])
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DAttributeTab",
                [
                    "NAME:PropServers", 
                    "Polyline1"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Name",
                        "Value:="        , "n_polygon_ngon_negative"
                    ]
                ]
            ]
        ])
    if C ==1:
        # LeftOut
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.CreatePolyline(
            [
                "NAME:PolylineParameters",
                "IsPolylineCovered:="    , True,
                "IsPolylineClosed:="    , True,
                [
                    "NAME:PolylinePoints",
                    ["NAME:PLPoint","X:=", str(x1+x)+"um","Y:="    , str(y1+y)+"um","Z:="    , "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1+cl+x)+"um","Y:=", str(y1+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1+cl+x)+"um","Y:=", str(y1+cw+cg*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg-cg-cw+x)+"um","Y:=", str(y1+cw+cg*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg-cg-cw+x)+"um","Y:=", str(y1+cg-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg*2-cw-cl+x)+"um","Y:=", str(y1+cg-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg*2-cw-cl+x)+"um","Y:=", str(y1-cl-cw-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg-cg-cw+x)+"um","Y:=", str(y1-cl-cw-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg-cg-cw+x)+"um","Y:=", str(y1-cl-cl-cw-cw-cg-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1+cl+x)+"um","Y:=", str(y1-cl-cl-cw-cw-cg-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1+cl+x)+"um","Y:=", str(y1-cl-cl-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1+x)+"um","Y:=", str(y1-cl-cl-cw+y)+"um","Z:=", "1e-5"],#12
                    ["NAME:PLPoint","X:=", str(x1+x)+"um","Y:="    , str(y1+y)+"um","Z:="    , "1e-5"],
                    
                ],
                [
                    "NAME:PolylineSegments",
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 0,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 1,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 2,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 3,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 4,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 5,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 6,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 7,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 8,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 9,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 10,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 11,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 12,"NoOfPoints:="        , 2],
                ],
                [
                    "NAME:PolylineXSection",
                    "XSectionType:="    , "None",
                    "XSectionOrient:="    , "Auto",
                    "XSectionWidth:="    , "0mm",
                    "XSectionTopWidth:="    , "0mm",
                    "XSectionHeight:="    , "0mm",
                    "XSectionNumSegments:="    , "0",
                    "XSectionBendType:="    , "Corner"
                ]
            ], 
            [
                "NAME:Attributes",
                "Name:="        , "Polyline3",
                "Flags:="        , "",
                "Color:="        , "(143 175 143)",
                "Transparency:="    , 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="        , "",
                "MaterialValue:="    , "\"copper\"",
                "SurfaceMaterialValue:=", "\"\"",
                "SolveInside:="        , False,
                "ShellElement:="    , False,
                "ShellElementThickness:=", "0mm",
                "IsMaterialEditable:="    , True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="    , False
            ])
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DAttributeTab",
                    [
                        "NAME:PropServers", 
                        "Polyline3"
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Name",
                            "Value:="        , "left_outside"
                        ]
                    ]
                ]
            ])
        # LeftInside
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.CreatePolyline(
            [
                "NAME:PolylineParameters",
                "IsPolylineCovered:="    , True,
                "IsPolylineClosed:="    , True,
                [
                    "NAME:PolylinePoints",
                    
                    ["NAME:PLPoint","X:=", str(x1-cg+x)+"um","Y:=" , str(y1-cl-cl-cg-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg+cl+x)+"um","Y:=" , str(y1-cl-cl-cg-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg+cl+x)+"um","Y:=" , str(y1-cl-cl-cg-cw*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg-cw+x)+"um","Y:=" , str(y1-cl-cl-cg-cw*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg-cw+x)+"um","Y:=" , str(y1-cl-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg-cw-cl+x)+"um","Y:=" , str(y1-cl-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg-cw-cl+x)+"um","Y:=" , str(y1-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg-cw+x)+"um","Y:=" , str(y1-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg-cw+x)+"um","Y:=" , str(y1+cg+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg+cl+x)+"um","Y:=" , str(y1+cg+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg+cl+x)+"um","Y:=" , str(y1+cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x1-cg+x)+"um","Y:=" , str(y1+cg+y)+"um","Z:=", "1e-5"],#24
                    ["NAME:PLPoint","X:=", str(x1-cg+x)+"um","Y:=" , str(y1-cl-cl-cg-cw+y)+"um","Z:=", "1e-5"],
                ],
                [
                    "NAME:PolylineSegments",
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 0,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 1,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 2,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 3,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 4,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 5,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 6,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 7,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 8,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 9,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 10,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 11,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 12,"NoOfPoints:="        , 2],
                ],
                [
                    "NAME:PolylineXSection",
                    "XSectionType:="    , "None",
                    "XSectionOrient:="    , "Auto",
                    "XSectionWidth:="    , "0mm",
                    "XSectionTopWidth:="    , "0mm",
                    "XSectionHeight:="    , "0mm",
                    "XSectionNumSegments:="    , "0",
                    "XSectionBendType:="    , "Corner"
                ]
            ], 
            [
                "NAME:Attributes",
                "Name:="        , "Polyline4",
                "Flags:="        , "",
                "Color:="        , "(143 175 143)",
                "Transparency:="    , 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="        , "",
                "MaterialValue:="    , "\"copper\"",
                "SurfaceMaterialValue:=", "\"\"",
                "SolveInside:="        , False,
                "ShellElement:="    , False,
                "ShellElementThickness:=", "0mm",
                "IsMaterialEditable:="    , True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="    , False
            ])
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DAttributeTab",
                    [
                        "NAME:PropServers", 
                        "Polyline4"
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Name",
                            "Value:="        , "left_inside"
                        ]
                    ]
                ]
            ])
        # Subtract Left
        oEditor.Subtract(
        [
            "NAME:Selections",
            "Blank Parts:="        , "ground_Q_chip_plane",
            "Tool Parts:="        , "left_outside"
        ], 
        
        [
            "NAME:SubtractParameters",
            "KeepOriginals:="    , False
        ])
        # Set material
        oModule = oDesign.GetModule("BoundarySetup")
        oModule.AssignThinConductor(
        [
            "NAME:ThinCond1",
            "Objects:="        , ["left_inside"],
            "Material:="        , "pec",
            "Thickness:="        , "200nm"
        ])
    if  A == 1 :
        # Right finger insert (outside)
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.CreatePolyline(
            [
                "NAME:PolylineParameters",
                "IsPolylineCovered:="    , True,
                "IsPolylineClosed:="    , True,
                [
                    "NAME:PolylinePoints",
                    ["NAME:PLPoint","X:=", str(x2+x)+"um","Y:="    , str(y2+y)+"um","Z:="    , "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+x)+"um","Y:=", str(y2-cl*2-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2-cl+x)+"um","Y:=", str(y2-cl*2-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2-cl+x)+"um","Y:=", str(y2-cl*2-cg*2-cw*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg*2+cw+x)+"um","Y:=", str(y2-cl*2-cg*2-cw*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg*2+cw+x)+"um","Y:=", str(y2-cl-cw-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg*2+cw+cl+x)+"um","Y:=", str(y2-cl-cg-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg*2+cw+cl+x)+"um","Y:=", str(y2-cl+cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg*2+cw+x)+"um","Y:=", str(y2-cl+cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg*2+cw+x)+"um","Y:=", str(y2+cg*2+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2-cl+x)+"um","Y:=", str(y2+cg*2+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2-cl+x)+"um","Y:=", str(y2+y)+"um","Z:=", "1e-5"],#12
                    ["NAME:PLPoint","X:=", str(x2+x)+"um","Y:="    , str(y2+y)+"um","Z:="    , "1e-5"],
                    
                ],
                [
                    "NAME:PolylineSegments",
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 0,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 1,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 2,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 3,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 4,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 5,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 6,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 7,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 8,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 9,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 10,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 11,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 12,"NoOfPoints:="        , 2],
                ],
                [
                    "NAME:PolylineXSection",
                    "XSectionType:="    , "None",
                    "XSectionOrient:="    , "Auto",
                    "XSectionWidth:="    , "0mm",
                    "XSectionTopWidth:="    , "0mm",
                    "XSectionHeight:="    , "0mm",
                    "XSectionNumSegments:="    , "0",
                    "XSectionBendType:="    , "Corner"
                ]
            ], 
            [
                "NAME:Attributes",
                "Name:="        , "Polyline3",
                "Flags:="        , "",
                "Color:="        , "(143 175 143)",
                "Transparency:="    , 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="        , "",
                "MaterialValue:="    , "\"copper\"",
                "SurfaceMaterialValue:=", "\"\"",
                "SolveInside:="        , False,
                "ShellElement:="    , False,
                "ShellElementThickness:=", "0mm",
                "IsMaterialEditable:="    , True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="    , False
            ])
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DAttributeTab",
                    [
                        "NAME:PropServers", 
                        "Polyline3"
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Name",
                            "Value:="        , "right_outside"
                        ]
                    ]
                ]
            ])
        # Right finger insert (inside)
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.CreatePolyline(
            [
                "NAME:PolylineParameters",
                "IsPolylineCovered:="    , True,
                "IsPolylineClosed:="    , True,
                [
                    "NAME:PolylinePoints",
                    
                    ["NAME:PLPoint","X:=", str(x2-cl+cg+x)+"um","Y:=" , str(y2+cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2-cl+cg+x)+"um","Y:=" , str(y2+cg+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg+cw+x)+"um","Y:=" , str(y2+cg+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg+cw+x)+"um","Y:=" , str(y2-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg+cw+cl+x)+"um","Y:=" , str(y2-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg+cw+cl+x)+"um","Y:=" , str(y2-cl-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg+cw+x)+"um","Y:=" , str(y2-cl-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg+cw+x)+"um","Y:=" , str(y2-cl*2-cw*2-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg-cl+x)+"um","Y:=" , str(y2-cl*2-cw*2-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg-cl+x)+"um","Y:=" , str(y2-cl*2-cw-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg+x)+"um","Y:=" , str(y2-cl*2-cw-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x2+cg+x)+"um","Y:=" , str(y2+cg+y)+"um","Z:=", "1e-5"],#24
                    ["NAME:PLPoint","X:=", str(x2+cg-cl+x)+"um","Y:=" , str(y2+cg+y)+"um","Z:=", "1e-5"],
                ],
                [
                    "NAME:PolylineSegments",
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 0,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 1,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 2,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 3,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 4,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 5,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 6,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 7,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 8,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 9,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 10,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 11,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 12,"NoOfPoints:="        , 2],
                ],
                [
                    "NAME:PolylineXSection",
                    "XSectionType:="    , "None",
                    "XSectionOrient:="    , "Auto",
                    "XSectionWidth:="    , "0mm",
                    "XSectionTopWidth:="    , "0mm",
                    "XSectionHeight:="    , "0mm",
                    "XSectionNumSegments:="    , "0",
                    "XSectionBendType:="    , "Corner"
                ]
            ], 
            [
                "NAME:Attributes",
                "Name:="        , "Polyline4",
                "Flags:="        , "",
                "Color:="        , "(143 175 143)",
                "Transparency:="    , 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="        , "",
                "MaterialValue:="    , "\"copper\"",
                "SurfaceMaterialValue:=", "\"\"",
                "SolveInside:="        , False,
                "ShellElement:="    , False,
                "ShellElementThickness:=", "0mm",
                "IsMaterialEditable:="    , True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="    , False
            ])
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DAttributeTab",
                    [
                        "NAME:PropServers", 
                        "Polyline4"
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Name",
                            "Value:="        , "right_inside"
                        ]
                    ]
                ]
            ])
        # Minus outside right
        oEditor.Subtract(
        [
            "NAME:Selections",
            "Blank Parts:="        , "ground_Q_chip_plane",
            "Tool Parts:="        , "right_outside"
        ], 
        
        [
            "NAME:SubtractParameters",
            "KeepOriginals:="    , False
        ])
        # Set material
        oModule = oDesign.GetModule("BoundarySetup")
        oModule.AssignThinConductor(
        [
            "NAME:ThinCond2",
            "Objects:="        , ["right_inside"],
            "Material:="        , "pec",
            "Thickness:="        , "200nm"
        ])
    if  B ==1:
        # Top finger insertion (outside)
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.CreatePolyline(
            [
                "NAME:PolylineParameters",
                "IsPolylineCovered:="    , True,
                "IsPolylineClosed:="    , True,
                [
                    "NAME:PolylinePoints",
                    ["NAME:PLPoint","X:=", str(x3+x)+"um","Y:="    , str(y3+y)+"um","Z:="    , "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl*2+cw+x)+"um","Y:=", str(y3+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl*2+cw+x)+"um","Y:=", str(y3-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl*2+cw*2+cg*2+x)+"um","Y:=", str(y3-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl*2+cw*2+cg*2+x)+"um","Y:=", str(y3+cw+cg*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl+cw+cg+x)+"um","Y:=", str(y3+cw+cg*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl+cw+cg+x)+"um","Y:=", str(y3+cl+cw+cg*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl-cg+x)+"um","Y:=", str(y3+cw+cl+cg*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl-cg+x)+"um","Y:=", str(y3+cw+cg*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3-cw-cg*2+x)+"um","Y:=", str(y3+cw+cg*2+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3-cw-cg*2+x)+"um","Y:=", str(y3-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+x)+"um","Y:=", str(y3-cl+y)+"um","Z:=", "1e-5"],#12
                    ["NAME:PLPoint","X:=", str(x3+x)+"um","Y:="    , str(y3+y)+"um","Z:="    , "1e-5"],
                    
                ],
                [
                    "NAME:PolylineSegments",
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 0,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 1,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 2,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 3,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 4,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 5,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 6,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 7,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 8,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 9,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 10,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 11,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 12,"NoOfPoints:="        , 2],
                ],
                [
                    "NAME:PolylineXSection",
                    "XSectionType:="    , "None",
                    "XSectionOrient:="    , "Auto",
                    "XSectionWidth:="    , "0mm",
                    "XSectionTopWidth:="    , "0mm",
                    "XSectionHeight:="    , "0mm",
                    "XSectionNumSegments:="    , "0",
                    "XSectionBendType:="    , "Corner"
                ]
            ], 
            [
                "NAME:Attributes",
                "Name:="        , "Polyline3",
                "Flags:="        , "",
                "Color:="        , "(143 175 143)",
                "Transparency:="    , 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="        , "",
                "MaterialValue:="    , "\"copper\"",
                "SurfaceMaterialValue:=", "\"\"",
                "SolveInside:="        , False,
                "ShellElement:="    , False,
                "ShellElementThickness:=", "0mm",
                "IsMaterialEditable:="    , True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="    , False
            ])
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DAttributeTab",
                    [
                        "NAME:PropServers", 
                        "Polyline3"
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Name",
                            "Value:="        , "upper_outside"
                        ]
                    ]
                ]
            ])
        # Top finger insert (inside)
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.CreatePolyline(
            [
                "NAME:PolylineParameters",
                "IsPolylineCovered:="    , True,
                "IsPolylineClosed:="    , True,
                [
                    "NAME:PolylinePoints",
                    
                    ["NAME:PLPoint","X:=", str(x3-cg+x)+"um","Y:=" , str(y3-cl+cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3-cg-cw+x)+"um","Y:=" , str(y3-cl+cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3-cg-cw+x)+"um","Y:=" , str(y3+cg+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl+x)+"um","Y:=" , str(y3+cg+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl+x)+"um","Y:=" , str(y3+cl+cg+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl+cw+x)+"um","Y:=" , str(y3+cl+cg+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl+cw+x)+"um","Y:=" , str(y3+cg+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl*2+cw*2+cg+x)+"um","Y:=" , str(y3+cg+cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl*2+cw*2+cg+x)+"um","Y:=" , str(y3-cl+cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl*2+cw+cg+x)+"um","Y:=" , str(y3-cl+cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3+cl*2+cw+cg+x)+"um","Y:=" , str(y3+cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x3-cg+x)+"um","Y:=" , str(y3+cg+y)+"um","Z:=", "1e-5"],#24
                    ["NAME:PLPoint","X:=", str(x3-cg+x)+"um","Y:=" , str(y3-cl+cg+y)+"um","Z:=", "1e-5"],
                ],
                [
                    "NAME:PolylineSegments",
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 0,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 1,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 2,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 3,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 4,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 5,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 6,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 7,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 8,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 9,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 10,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 11,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 12,"NoOfPoints:="        , 2],
                ],
                [
                    "NAME:PolylineXSection",
                    "XSectionType:="    , "None",
                    "XSectionOrient:="    , "Auto",
                    "XSectionWidth:="    , "0mm",
                    "XSectionTopWidth:="    , "0mm",
                    "XSectionHeight:="    , "0mm",
                    "XSectionNumSegments:="    , "0",
                    "XSectionBendType:="    , "Corner"
                ]
            ], 
            [
                "NAME:Attributes",
                "Name:="        , "Polyline4",
                "Flags:="        , "",
                "Color:="        , "(143 175 143)",
                "Transparency:="    , 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="        , "",
                "MaterialValue:="    , "\"copper\"",
                "SurfaceMaterialValue:=", "\"\"",
                "SolveInside:="        , False,
                "ShellElement:="    , False,
                "ShellElementThickness:=", "0mm",
                "IsMaterialEditable:="    , True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="    , False
            ])
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DAttributeTab",
                    [
                        "NAME:PropServers", 
                        "Polyline4"
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Name",
                            "Value:="        , "upper_inside"
                        ]
                    ]
                ]
            ])
        # Minus top out
        oEditor.Subtract(
        [
            "NAME:Selections",
            "Blank Parts:="        , "ground_Q_chip_plane",
            "Tool Parts:="        , "upper_outside"
        ], 
        
        [
            "NAME:SubtractParameters",
            "KeepOriginals:="    , False
        ])
        # Set material
        oModule = oDesign.GetModule("BoundarySetup")
        oModule.AssignThinConductor(
        [
            "NAME:ThinCond3",
            "Objects:="        , ["upper_inside"],
            "Material:="        , "pec",
            "Thickness:="        , "200nm"
        ])
    if D == 1:
        # Lower finger inserts (outside)
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.CreatePolyline(
            [
                "NAME:PolylineParameters",
                "IsPolylineCovered:="    , True,
                "IsPolylineClosed:="    , True,
                [
                    "NAME:PolylinePoints",
                    ["NAME:PLPoint","X:=", str(x4+x)+"um","Y:="    , str(y4+y)+"um","Z:="    , "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl*2-cw+x)+"um","Y:=", str(y4+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl*2-cw+x)+"um","Y:=", str(y4+cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl*2-cw*2-cg*2+x)+"um","Y:=", str(y4+cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl*2-cw*2-cg*2+x)+"um","Y:=", str(y4-cg*2-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl-cw-cg+x)+"um","Y:=", str(y4-cg*2-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl-cw-cg+x)+"um","Y:=", str(y4-cg*2-cw-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl+cg+x)+"um","Y:=", str(y4-cg*2-cw-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl+cg+x)+"um","Y:=", str(y4-cg*2-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4+cw+cg*2+x)+"um","Y:=", str(y4-cg*2-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4+cw+cg*2+x)+"um","Y:=", str(y4+cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4+x)+"um","Y:=", str(y4+cl+y)+"um","Z:=", "1e-5"],#12
                    ["NAME:PLPoint","X:=", str(x4+x)+"um","Y:="    , str(y4+y)+"um","Z:="    , "1e-5"],
                    
                ],
                [
                    "NAME:PolylineSegments",
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 0,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 1,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 2,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 3,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 4,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 5,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 6,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 7,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 8,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 9,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 10,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 11,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 12,"NoOfPoints:="        , 2],
                ],
                [
                    "NAME:PolylineXSection",
                    "XSectionType:="    , "None",
                    "XSectionOrient:="    , "Auto",
                    "XSectionWidth:="    , "0mm",
                    "XSectionTopWidth:="    , "0mm",
                    "XSectionHeight:="    , "0mm",
                    "XSectionNumSegments:="    , "0",
                    "XSectionBendType:="    , "Corner"
                ]
            ], 
            [
                "NAME:Attributes",
                "Name:="        , "Polyline3",
                "Flags:="        , "",
                "Color:="        , "(143 175 143)",
                "Transparency:="    , 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="        , "",
                "MaterialValue:="    , "\"copper\"",
                "SurfaceMaterialValue:=", "\"\"",
                "SolveInside:="        , False,
                "ShellElement:="    , False,
                "ShellElementThickness:=", "0mm",
                "IsMaterialEditable:="    , True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="    , False
            ])
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DAttributeTab",
                    [
                        "NAME:PropServers", 
                        "Polyline3"
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Name",
                            "Value:="        , "bottom_outside"
                        ]
                    ]
                ]
            ])
        # Lower finger inserts (inside)
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.CreatePolyline(
            [
                "NAME:PolylineParameters",
                "IsPolylineCovered:="    , True,
                "IsPolylineClosed:="    , True,
                [
                    "NAME:PolylinePoints",
                    
                    ["NAME:PLPoint","X:=", str(x4+cg+x)+"um","Y:=" , str(y4+cl-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4+cg+cw+x)+"um","Y:=" , str(y4+cl-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4+cg+cw+x)+"um","Y:=" , str(y4-cg-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl+x)+"um","Y:=" , str(y4-cg-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl+x)+"um","Y:=" , str(y4-cg-cw-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl-cw+x)+"um","Y:=" , str(y4-cg-cw-cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl-cw+x)+"um","Y:=" , str(y4-cg-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl*2-cw*2-cg+x)+"um","Y:=" , str(y4-cg-cw+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl*2-cw*2-cg+x)+"um","Y:=" , str(y4-cg+cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl*2-cw-cg+x)+"um","Y:=" , str(y4-cg+cl+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4-cl*2-cw-cg+x)+"um","Y:=" , str(y4-cg+y)+"um","Z:=", "1e-5"],
                    ["NAME:PLPoint","X:=", str(x4+cg+x)+"um","Y:=" , str(y4-cg+y)+"um","Z:=", "1e-5"],#24
                    ["NAME:PLPoint","X:=", str(x4+cg+x)+"um","Y:=" , str(y4+cl-cg+y)+"um","Z:=", "1e-5"],
                ],
                [
                    "NAME:PolylineSegments",
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 0,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 1,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 2,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 3,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 4,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 5,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 6,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 7,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 8,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 9,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 10,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 11,"NoOfPoints:="        , 2],
                    ["NAME:PLSegment","SegmentType:="        , "Line","StartIndex:="        , 12,"NoOfPoints:="        , 2],
                ],
                [
                    "NAME:PolylineXSection",
                    "XSectionType:="    , "None",
                    "XSectionOrient:="    , "Auto",
                    "XSectionWidth:="    , "0mm",
                    "XSectionTopWidth:="    , "0mm",
                    "XSectionHeight:="    , "0mm",
                    "XSectionNumSegments:="    , "0",
                    "XSectionBendType:="    , "Corner"
                ]
            ], 
            [
                "NAME:Attributes",
                "Name:="        , "Polyline4",
                "Flags:="        , "",
                "Color:="        , "(143 175 143)",
                "Transparency:="    , 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="        , "",
                "MaterialValue:="    , "\"copper\"",
                "SurfaceMaterialValue:=", "\"\"",
                "SolveInside:="        , False,
                "ShellElement:="    , False,
                "ShellElementThickness:=", "0mm",
                "IsMaterialEditable:="    , True,
                "UseMaterialAppearance:=", False,
                "IsLightweight:="    , False
            ])
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DAttributeTab",
                    [
                        "NAME:PropServers", 
                        "Polyline4"
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Name",
                            "Value:="        , "bottom_inside"
                        ]
                    ]
                ]
            ])
        # Subtract the outside
        oEditor.Subtract(
        [
            "NAME:Selections",
            "Blank Parts:="        , "ground_Q_chip_plane",
            "Tool Parts:="        , "bottom_outside"
        ], 
        
        [
            "NAME:SubtractParameters",
            "KeepOriginals:="    , False
        ])
        # Set material
        oModule = oDesign.GetModule("BoundarySetup")
        oModule.AssignThinConductor(
        [
            "NAME:ThinCond4",
            "Objects:="        , ["bottom_inside"],
            "Material:="        , "pec",
            "Thickness:="        , "200nm"
        ])
    oEditor.Subtract(
    [
        "NAME:Selections",
        "Blank Parts:="        , "ground_Q_chip_plane",
        "Tool Parts:="        , "n_polygon_ngon_negative"
    ], 
    [
        "NAME:SubtractParameters",
        "KeepOriginals:="    , False
    ])
    
    
    oModule = oDesign.GetModule("BoundarySetup")
    oModule.AssignThinConductor(
        [
            "NAME:ThinCond5",
            "Objects:="        , ["bt_Xmon","ground_Q_chip_plane"],
            "Material:="        , "pec",
            "Thickness:="        , "200nm"
        ])
    oModule.AutoIdentifyNets()
    oProject.Save()
    oDesign.AnalyzeAllNominal()

    if path == Dict() or path is None:
        path = "C:/sim_proj/PlaneXmon_sim/Xmon_random_capacity_{}.txt".format(q_name)    # Default path
        print("The default save path for the capacitor matrix is {}".format(path))
    import toolbox
    toolbox.jg_and_create_path_plus(path)

    oDesign.ExportMatrixData(path, "C", "", "Setup:LastAdaptive", "Original", "ohm", "nH", "fF", "mSie", 5000000000, "Maxwell,Spice,Couple", 0, False, 15, 20, 1)
    print("The capacitor matrix has been saved to {}".format(path))

    p=pathlib.Path(path)
    m=p.read_text().split('\n')

    cm=m[m.index('Capacitance Matrix'):m.index('Conductance Matrix')-1]

    pattern='(?<=C Units:)(.+?)((?<![^a-zA-Z0-9_\u4e00-\u9fa5])(?=[^a-zA-Z0-9_\u4e00-\u9fa5])|(?<=[^a-zA-Z0-9_\u4e00-\u9fa5])(?![^a-zA-Z0-9_\u4e00-\u9fa5])|$)'

    unit=re.findall(pattern, p.read_text())[0][0]

    rowLabels = []
    column_labels = []
    data=[]
    j=[]
    for i in range(len(cm)):
            a=[x for x in cm[i].split('\t') if x!='']
            if(len(a)==0):
                break
            if i==1:
                j=a.copy()
                    
            if i==1:
                column_labels=a
            elif i>1:
                rowLabels.append(a[0])
                data.append([f"{str(round(float(x),5))}" for x in a[1:]])

    df1 = pd.DataFrame(data, index=column_labels, columns=rowLabels) 
    display(df1)
    # Bit Cq
    Cq = -float(df1.loc['bt_Xmon', 'ground_Q_chip_plane'])     # Unit fF
    print("Cq =", Cq,'fF')
    #Ec
    Ec = e**2 / 2 / Cq*1e15 / hbar # Angular frequency, unit Mhz angular frequency /2pi= frequency
    print("Ec =", Ec/2/np.pi/1e6,'MHz')