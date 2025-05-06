#########################################################################
# File Name: xmon_sim.py
# Description: A module for simulating Xmon qubits.
#             It includes the geometric modeling and electromagnetic field simulation of the qubit.
#########################################################################

# Import required libraries
import win32com.client  # Import the win32com library for calling COM objects
from addict import Dict  # Provides extensions to the dictionary type, making it behave more like an object
import os  # Provides functionality related to the operating system
import pathlib  # Used for path operations
import re  # Regular expression library
import pandas as pd  # Data analysis library
import toolbox  # Custom toolbox module
import numpy as np  # Mathematical library

# Define constants
e = 1.60217657e-19  # Elementary charge
h = 6.62606957e-34  # Planck's constant
hbar = 1.0545718E-34  # Reduced Planck's constant
phinot = 2.067 * 1E-15  # Magnetic flux quantum
phi0 = phinot / (2 * np.pi)  # Reduced magnetic flux quantum
c = 3 * 10 ** 8  # Speed of light


# Generate a set of points on a circle given the center and radius
def generate_circle_points(center_x, center_y, radius, num_points):
    """
    Generate points on a circle based on the given center and radius.

    Inputs:
        center_x: The x-coordinate of the circle's center.
        center_y: The y-coordinate of the circle's center.
        radius: The radius of the circle.
        num_points: The number of points to generate.

    Outputs:
        points: A two-dimensional array containing the coordinates of the points on the circle.
    """
    # Generate a series of angles from 0 to 2π
    angles = np.linspace(0, 2 * np.pi, num_points)

    # Calculate the coordinates of each point on the circle
    points_x = center_x + radius * np.cos(angles)
    points_y = center_y + radius * np.sin(angles)

    # Combine the coordinates into a two-dimensional array, with each row representing the (x, y) coordinates of a point
    points = np.column_stack((points_x, points_y))

    return points


def simulation(qubit, ctl, path):
    """
    Perform the simulation of an Xmon qubit.

    Inputs:
        qubit: Qubit object containing the geometric parameters of the qubit.
        ctl: Controller object containing the geometric parameters of the controller.
        path: The path where the simulation results are saved.

    Outputs:
        Cq: The capacitance parameter of the qubit, in femtofarads.
        Ec: The Josephson energy of the qubit, in MHz.
    """
    ############################### Interface #########################################
    # a = Xmon(x=0,y=0,Q_name='123')      # Instantiate once
    import toolbox
    toolbox.show_options(ctl)
    
    q_name = qubit.name
    width = qubit.cross_width
    height= qubit.cross_height
    gap= qubit.cross_gap
    cl = qubit.claw_length
    gs = qubit.ground_spacing
    cw = qubit.claw_width
    cg = qubit.claw_gap
    in_s = (cl*2+cw-width-gap*2)/2
    x = 0 - height - width/2
    y = 0 - width/2
    # x_m = -155
    # y_m = -5


    x1 = -gap-gs
    y1 = width+gap+in_s
    x2 = height*2+width+gap+gs
    y2 = width+gap+in_s
    x3 = height-gap-in_s
    y3 = width+gap+height+gs
    x4 = height+gap+width+in_s
    y4 = -height-gap-gs

    xiao_r = ctl.radius
    da_r =  ctl.radius + ctl.gap

    A = int(qubit.coupling_qubits.right != None)
    B = int(qubit.coupling_qubits.top != None)
    C = int(qubit.coupling_qubits.left != None)
    D = int(qubit.coupling_qubits.bot != None)
    ############################################################################

    oAnsoftApp=win32com.client.Dispatch('AnsoftHfss.HfssScriptInterface')
    oDesktop=oAnsoftApp.GetAppDesktop()  
    oProject=oDesktop.NewProject()
    oProject.InsertDesign("Q3D Extractor", '123', "", "")
    oDesign = oProject.SetActiveDesign('123')#"Q3DDesign1"

    # Set Analysis
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oModule = oDesign.GetModule("AnalysisSetup")
    oModule.InsertSetup("Matrix", 
        [
            "NAME:Setup",
            "AdaptiveFreq:="    , "5GHz",
            "SaveFields:="        , False,
            "Enabled:="        , True,
            [
                "NAME:Cap",
                "MaxPass:="        , 15,         
                "MinPass:="        , 2,
                "MinConvPass:="        , 2,
                "PerError:="        , 0.5,
                "PerRefine:="        , 30,
                "AutoIncreaseSolutionOrder:=", True,
                "SolutionOrder:="    , "High",
                "Solver Type:="        , "Iterative"
            ]
        ])

    # Add square, add box, Add incentive (Q-chip)
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:="        , True,
            "XStart:="        , str(x-330)+"um",     
            "YStart:="        , str(y-500)+"um",
            "ZStart:="        , "1e-05",
            "Width:="        , "0.002000",   #The base of 1000*1000
            "Height:="        , "0.002000",
            "WhichAxis:="        , "Z"
        ], 
        [
            "NAME:Attributes",
            "Name:="        , "ground_Q_chip_plane",
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
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:="        , str(x-330)+"um",   
            "YPosition:="        , str(y-500)+"um",   
            "ZPosition:="        , "0.00029",
            "XSize:="        , "0.002000",     #The box of 1000*1000
            "YSize:="        , "0.002000",
            "ZSize:="        , "-0.00028"
        ], 
        [
            "NAME:Attributes",
            "Name:="        , "Q_chip",
            "Flags:="        , "",
            "Color:="        , "(186 186 205)",
            "Transparency:="    , 0.2,
            "PartCoordinateSystem:=", "Global",
            "UDMId:="        , "",
            "MaterialValue:="    , "\"silicon\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:="        , False,
            "ShellElement:="    , False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:="    , True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:="    , False
        ])
    # Dot connect, here is the bit
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.CreatePolyline(
        [
            "NAME:PolylineParameters",
            "IsPolylineCovered:="    , True,
            "IsPolylineClosed:="    , True,
            [
                "NAME:PolylinePoints",
                ["NAME:PLPoint","X:=", str(x)+"um","Y:="    , str(y)+"um","Z:="    , "1e-5"],
                ["NAME:PLPoint","X:=", str(height+x)+"um","Y:=", str(0+y)+"um","Z:=", "1e-5"],
                ["NAME:PLPoint","X:=", str(height+x)+"um","Y:=", str(-height+y)+"um","Z:=", "1e-5"],
                ["NAME:PLPoint","X:=", str(height+width+x)+"um","Y:=", str(-height+y)+"um","Z:=", "1e-5"],
                ["NAME:PLPoint","X:=", str(height+width+x)+"um","Y:=", str(0+y)+"um","Z:=", "1e-5"],
                ["NAME:PLPoint","X:=", str(height*2+width+x)+"um","Y:=", str(0+y)+"um","Z:=", "1e-5"],
                ["NAME:PLPoint","X:=", str(height*2+width+x)+"um","Y:=", str(width+y)+"um","Z:=", "1e-5"],
                ["NAME:PLPoint","X:=", str(height+width+x)+"um","Y:=", str(width+y)+"um","Z:=", "1e-5"],
                ["NAME:PLPoint","X:=", str(height+width+x)+"um","Y:=", str(height+width+y)+"um","Z:=", "1e-5"],
                ["NAME:PLPoint","X:=", str(height+x)+"um","Y:=", str(height+width+y)+"um","Z:=", "1e-5"],
                ["NAME:PLPoint","X:=", str(height+x)+"um","Y:=", str(width+y)+"um","Z:=", "1e-5"],
                ["NAME:PLPoint","X:=", str(0+x)+"um","Y:=", str(width+y)+"um","Z:=", "1e-5"],
                ["NAME:PLPoint","X:=", str(x)+"um","Y:=" , str(y)+"um","Z:=", "1e-5"],
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
                        "Value:="        , "bt_Xmon"
                    ]
                ]
            ]
        ])
    # Inside and out, same reason, big
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
        # Left Out
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
        # left inside
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

    # Generate 64 points on the inner circle
    center_x = 0
    center_y = 0
    radius = xiao_r / 1000000
    num_points = 64
    circle_points_inside = generate_circle_points(center_x, center_y, radius, num_points)
    # print(circle_points_inside)

    # Generates 64 points on the outer circle
    center_x = 0
    center_y = 0
    radius = da_r / 1000000
    num_points = 64
    circle_points_outside = generate_circle_points(center_x, center_y, radius, num_points)
    # print(circle_points_outside)

    # Draw the inner circle through the pile of points above
    pointx = []
    pointy = []
    #pointz = []
    for i in range(len(circle_points_inside)):
        pointx.append(circle_points_inside[i][0])
        pointy.append(circle_points_inside[i][1])
        #pointz.append('0')
    # print(pointx)
    # print(pointy)
    polylinepoints=["NAME:PolylinePoints"]
    for i in range(len(circle_points_inside)):
        add=["NAME:PLPoint"]
        add.append("X:=")
        add.append(str(pointx[i]))
        add.append("Y:=")
        add.append(str(pointy[i]))
        add.append("Z:=")
        add.append("0")    
        polylinepoints.append(add)
    add=["NAME:PLPoint"]
    add.append("X:=")
    add.append(str(pointx[0]))
    add.append("Y:=")
    add.append(str(pointy[0]))
    add.append("Z:=")
    add.append("0")    
    polylinepoints.append(add)
    # print(polylinepoints)
    polylinesegments=["NAME:PolylineSegments"]
    for i in range(len(circle_points_inside)+1):
        add=["NAME:PLSegment"]
        add.append("SegmentType:=")
        add.append("Line")
        add.append("StartIndex:=")
        add.append(i)
        add.append("NoOfPoints:=")
        add.append(2)
        polylinesegments.append(add)
    # print(polylinesegments)
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.CreatePolyline( 
            [
                "NAME:PolylineParameters",
                "IsPolylineCovered:="    , True,
                "IsPolylineClosed:="    , True,
                polylinepoints,
                polylinesegments,
                
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
                "Name:="        , "Circle1",
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
    #type(oEditor.CreatePolyline)
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DAttributeTab",
                    [
                        "NAME:PropServers", 
                        "Circle1"
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Name",
                            "Value:="        , "circle_inside"
                        ]
                    ]
                ]
            ])
    # Draw the outer circle through the pile of points above
    pointx = []
    pointy = []
    #pointz = []
    for i in range(len(circle_points_outside)):
        pointx.append(circle_points_outside[i][0])
        pointy.append(circle_points_outside[i][1])
        #pointz.append('0')
    # print(pointx)
    # print(pointy)
    polylinepoints=["NAME:PolylinePoints"]
    for i in range(len(circle_points_outside)):
        add=["NAME:PLPoint"]
        add.append("X:=")
        add.append(str(pointx[i]))
        add.append("Y:=")
        add.append(str(pointy[i]))
        add.append("Z:=")
        add.append("0")    
        polylinepoints.append(add)
    add=["NAME:PLPoint"]
    add.append("X:=")
    add.append(str(pointx[0]))
    add.append("Y:=")
    add.append(str(pointy[0]))
    add.append("Z:=")
    add.append("0")    
    polylinepoints.append(add)
    # print(polylinepoints)
    polylinesegments=["NAME:PolylineSegments"]
    for i in range(len(circle_points_outside)+1):
        add=["NAME:PLSegment"]
        add.append("SegmentType:=")
        add.append("Line")
        add.append("StartIndex:=")
        add.append(i)
        add.append("NoOfPoints:=")
        add.append(2)
        polylinesegments.append(add)
    # print(polylinesegments)
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.CreatePolyline( 
            [
                "NAME:PolylineParameters",
                "IsPolylineCovered:="    , True,
                "IsPolylineClosed:="    , True,
                polylinepoints,
                polylinesegments,
                
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
                "Name:="        , "Circle2",
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
    #type(oEditor.CreatePolyline)
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DAttributeTab",
                    [
                        "NAME:PropServers", 
                        "Circle2"
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Name",
                            "Value:="        , "circle_outside"
                        ]
                    ]
                ]
            ])
    # Add square, Add Box, Add incentive (C-chip)
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:="        , True,
            "XStart:="        , str(x-330)+"um",     
            "YStart:="        , str(y-500)+"um",
            "ZStart:="        , "0",
            "Width:="        , "0.002000",   #Base 1000 x 1000
            "Height:="        , "0.002000",
            "WhichAxis:="        , "Z"
        ], 
        [
            "NAME:Attributes",
            "Name:="        , "ground_C_chip_plane",
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
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:="        , str(x-330)+"um",   
            "YPosition:="        , str(y-500)+"um",   
            "ZPosition:="        , "-0.00028",
            "XSize:="        , "0.002000",     #A 1000 x 1000 box
            "YSize:="        , "0.002000",
            "ZSize:="        , "0.00028"
        ], 
        [
            "NAME:Attributes",
            "Name:="        , "C_chip",
            "Flags:="        , "",
            "Color:="        , "(186 186 205)",
            "Transparency:="    , 0.2,
            "PartCoordinateSystem:=", "Global",
            "UDMId:="        , "",
            "MaterialValue:="    , "\"silicon\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:="        , False,
            "ShellElement:="    , False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:="    , True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:="    , False
        ])
    oEditor.Subtract(
        [
            "NAME:Selections",
            "Blank Parts:="        , "ground_C_chip_plane",
            "Tool Parts:="        , "circle_outside"
        ], 
        [
            "NAME:SubtractParameters",
            "KeepOriginals:="    , False
        ])
    oModule = oDesign.GetModule("BoundarySetup")
    oModule.AssignThinConductor(
        [
            "NAME:ThinCond5",
            "Objects:="        , ["bt_Xmon","ground_Q_chip_plane","circle_inside","ground_C_chip_plane"],
            "Material:="        , "pec",
            "Thickness:="        , "200nm"
        ])
    oModule.AutoIdentifyNets()
    oProject.Save()
    oDesign.AnalyzeAllNominal()

    if path == Dict() or path is None:
        path = "C:/tianyan/sim/Xmon_random_capacity_{}.txt".format(q_name)    # Default path
        print("The default save path for the capacitor matrix is {}".format(path))
        toolbox.jg_and_create_path(path)
    toolbox.jg_and_create_path(path)
    oDesign.ExportMatrixData(path, "C", "", "Setup:LastAdaptive", "Original", "ohm", "nH", "fF", "mSie", 5000000000, "Maxwell,Spice,Couple", 0, False, 15, 20, 1)
    print("The capacitor matrix has been saved to {}".format(path))
    df1 = toolbox.display_dataframe(path)
    # Bit Cq
    Cq = -float(df1.loc['bt_Xmon', 'ground_Q_chip_plane'])     # Unit fF
    print("Cq =", Cq,'fF')
    #Ec
    Ec = e**2 / 2 / Cq*1e15 / hbar # Angular frequency, unit Mhz angular frequency /2pi= frequency
    print("Ec =", Ec/2/np.pi/1e6,'MHz')

    return Cq, Ec/2/np.pi/1e6