#########################################################################
# File Name: rdls_tmls.py
# Function Description: Simulation module for readout cavities and transmission lines,
#                       containing functions and constant definitions related to simulation.
#########################################################################

from addict import Dict
import gdspy, os
import library
import numpy as np

# Define constants
e = 1.60217657e-19  # Electron charge
h = 6.62606957e-34  # Planck's constant
hbar = 1.0545718E-34  # Reduced Planck's constant
phinot = 2.067 * 1E-15  # Magnetic flux quantum h/2e
phi0 = phinot / (2 * np.pi)  # Reduced magnetic flux quantum
c = 3 * 10 ** 8  # Speed of light
Cq = 65
Ec = e ** 2 / 2 / Cq * 1e15 / hbar  # Angular frequency, unit: MHz, angular frequency / 2π = frequency


def simulation(rdl_ops, tml_ops, pin0_ops, pin1_ops, mode):
    """
    Perform the simulation of readout cavities and transmission lines.

    Input:
        rdl_ops: Dict, parameters for the readout cavity operations.
        tml_ops: Dict, parameters for the transmission line operations.
        pin0_ops: Dict, parameters for Pin0 operations.
        pin1_ops: Dict, parameters for Pin1 operations.
        mode: String, simulation mode (e.g., "DrivenModel" or "EigenMode").

    Output:
        ideal_freq: Float, calculated ideal frequency.
    """
    print("Simulating readout cavity and transmission line...")
    # Interface
    rdl_ops = Dict(rdl_ops)
    tml_ops = Dict(tml_ops)
    pin0_ops = Dict(pin0_ops)
    pin1_ops = Dict(pin1_ops)

    # Simulation process

    move_x = rdl_ops['start_pos'][0]
    move_y = rdl_ops['start_pos'][1]
    end_y = rdl_ops['end_pos'][1] - move_y
    rdl_ops['start_pos'] = [0, 0]
    rdl_ops['end_pos'] = [rdl_ops['end_pos'][0] - move_x, rdl_ops['end_pos'][1] - move_y]
    rdl_ops['space'] = 26.5

    # Display the simulation layout
    gds_library = gdspy.GdsLibrary()
    gdspy.library.use_current_library = False
    cell = gds_library.new_cell("rdls_tmls_simulation")

    p1 = library.pins.LaunchPad(options=Dict(pos=[-2000, end_y], orientation=90))
    p2 = library.pins.LaunchPad(options=Dict(pos=[2000, end_y], orientation=270))
    p1.draw_gds()
    p2.draw_gds()
    cell.add(p1.cell)
    cell.add(p2.cell)

    t = library.transmission_lines.TransmissionPath(options=Dict(pos=[[-2000, end_y], [2000, end_y]]))
    t.draw_gds()
    cell.add(t.cell)

    c = library.readout_lines.ReadoutCavity(options=rdl_ops)
    c.draw_gds()
    cell.add(c.cell)
    gdspy.LayoutViewer(gds_library)

    path = "C:/tianyan/simulation/rdls_tmls_simulation.gds"
    dirname = os.path.dirname(path)
    basename = os.path.dirname(path)
    if not os.path.exists(dirname):  # Check if the directory exists, create if not
        os.makedirs(dirname)
    gds_library.write_gds(path)

    ideal_freq = CPW_frequency_4(rdl_ops['length'])
    ideal_freq = round(ideal_freq, 0)

    print("mode = {}".format(mode))

    if mode == "DrivenModel":
        start_freq = str(ideal_freq - 2) + "GHz"
        end_freq = str(ideal_freq + 2) + "GHz"
        dri_2_0(dirname, path, start_freq, end_freq, end_y=end_y)
    elif mode == "EigenMode":
        eig_2_0(dirname, path, ideal_freq, end_y=end_y)

    return ideal_freq


def caculate_qubits_parms(f_q):
    """
    Calculate parameters for the qubit.

    Input:
        f_q: Float, frequency of the qubit (GHz).
    """
    Ej = (f_q * 10 ** 9 + Ec) ** 2 / 8 / Ec
    print("If fq =", f_q, 'GHz')
    print("Then, Ej =", round((Ej / 10 ** 9), 2), "GHz")
    Ic = Ej * h / phi0
    print("Then, Ic =", round((Ic * 10 ** 9), 2), "nA")
    Rn = np.pi * 0.182 * 10 ** -3 / 2 / Ic
    print("Then, Rn =", round(Rn, 4), "Ω")
    return


def CPW_frequency_4(l, k=10):
    """
    Calculate λ/4 CPW frequency.

    Args:
        l (float): λ/4 CPW length.
        k (float): Relative permittivity of the substrate.

    Returns:
        f (float): Frequency.
    """
    f = (c / 4 / l) * np.sqrt(2 / (k + 1))
    print("For λ/4, if l =", l, "um", "then fr =", f / 10 ** 3, "GHz")
    return f / 10 ** 3


def eig_2_0(folder_path, gds_path, freq, end_y):
    """
    Execute the eigenmode simulation.

    Input:
        folder_path: String, save path.
        gds_path: String, GDS file path.
        freq: Float, frequency.
        end_y: Float, y-axis endpoint.
    """
    import win32com.client
    oAnsoftApp = win32com.client.Dispatch('AnsoftHfss.HfssScriptInterface')
    oDesktop = oAnsoftApp.GetAppDesktop()
    oProject = oDesktop.NewProject("Projecteda3")
    oProject.InsertDesign("HFSS", "HFSSDesign1", "DrivenModal", "")
    oDesign = oProject.SetActiveDesign("HFSSDesign1")
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.ImportGDSII(
        [
            "NAME:options",
            "FileName:=", gds_path,  # Path to import GDS
            "FlattenHierarchy:=", True,
            "ImportMethod:=", 1,
            [
                "NAME:LayerMap",
                [
                    "NAME:LayerMapInfo",
                    "LayerNum:=", 0,
                    "DestLayer:=", "Signal0",
                    "layer_type:=", "signal"
                ]
            ],
            "OrderMap:=", [
            "entry:=", [
                "order:=", 0,
                "layer:=", "Signal0"
            ]
        ]
        ])

    # Create a rectangle to define certain areas
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", "0mm",
            "YStart:=", "-0.01mm",
            "ZStart:=", "0mm",
            "Width:=", "0.002mm",
            "Height:=", "0.02mm",
            "WhichAxis:=", "Z"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Rectangle4",
            "Flags:=", "",
            "Color:=", "(143 175 143)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"vacuum\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])

    # Unite rectangle with signal lines
    oEditor.Unite(
        [
            "NAME:Selections",
            "Selections:=",
            "Rectangle4,Signal0_5,Signal0_6,Signal0_7,Signal0_8,Signal0_9,Signal0_10,Signal0_11,Signal0_12,Signal0_13,Signal0_14,Signal0_15,Signal0_16,Signal0_17,Signal0_18,Signal0_19,Signal0_20,Signal0_21,Signal0_22,Signal0_23,Signal0_24,Signal0_25,Signal0_26,Signal0_27,Signal0_28,Signal0_29,Signal0_30,Signal0_31,Signal0_32,Signal0_33,Signal0_34,Signal0_35,Signal0_36,Signal0_37,Signal0_38,Signal0_39,Signal0_40,Signal0_41,Signal0_42,Signal0_43"
        ],
        [
            "NAME:UniteParameters",
            "KeepOriginals:=", False
        ])

    # Again unite signal lines
    oEditor.Unite(
        [
            "NAME:Selections",
            "Selections:=", "Signal0_1,Signal0_2,Signal0_3,Signal0_4"
        ],
        [
            "NAME:UniteParameters",
            "KeepOriginals:=", False
        ])

    # Create another rectangle
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", "-2.6mm",
            "YStart:=", "-0.6mm",
            "ZStart:=", "0mm",
            "Width:=", "5.2mm",
            "Height:=", "3mm",
            "WhichAxis:=", "Z"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Rectangle1",
            "Flags:=", "",
            "Color:=", "(143 175 143)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"vacuum\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])

    # Subtract rectangle from signal lines
    oEditor.Subtract(
        [
            "NAME:Selections",
            "Blank Parts:=", "Rectangle1",
            "Tool Parts:=", "Signal0_1,Rectangle4"
        ],
        [
            "NAME:SubtractParameters",
            "KeepOriginals:=", False
        ])

    # Create a box
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:=", "-2.6mm",
            "YPosition:=", "-0.6mm",
            "ZPosition:=", "0mm",
            "XSize:=", "5.2mm",
            "YSize:=", "3mm",
            "ZSize:=", "0mm"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Box1",
            "Flags:=", "",
            "Color:=", "(143 175 143)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"vacuum\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])

    # Modify box properties
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DCmdTab",
                [
                    "NAME:PropServers",
                    "Box1:CreateBox:1"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:ZSize",
                        "Value:=", "-450um"
                    ]
                ]
            ]
        ])

    # Again modify box properties
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DAttributeTab",
                [
                    "NAME:PropServers",
                    "Box1"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Color",
                        "R:=", 192,
                        "G:=", 192,
                        "B:=", 192
                    ]
                ]
            ]
        ])

    # Modify box material properties
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DAttributeTab",
                [
                    "NAME:PropServers",
                    "Box1"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Material",
                        "Value:=", "\"sapphire\""
                    ]
                ]
            ]
        ])

    # Set boundary conditions
    oModule = oDesign.GetModule("BoundarySetup")
    oModule.AssignPerfectE(
        [
            "NAME:PerfE1",
            "Objects:=", ["Rectangle1"],
            "InfGroundPlane:=", False
        ])

    # Set solution type to eigenmode
    oDesign.SetSolutionType("Eigenmode", False)

    # Again configure boundary conditions
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", "-2.245mm",
            "YStart:=", str(end_y / 1000 - 0.06) + "mm",  # Position calculation
            "ZStart:=", "0mm",
            "Width:=", "-0.1mm",
            "Height:=", "0.12mm",
            "WhichAxis:=", "Z"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Rectangle2",
            "Flags:=", "",
            "Color:=", "(143 175 143)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"vacuum\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])

    # Copy rectangle
    oEditor.Copy(
        [
            "NAME:Selections",
            "Selections:=", "Rectangle2"
        ])

    # Paste and move rectangle
    oEditor.Paste()
    oEditor.Move(
        [
            "NAME:Selections",
            "Selections:=", "Rectangle5",
            "NewPartsModelFlag:=", "Model"
        ],
        [
            "NAME:TranslateParameters",
            "TranslateVectorX:=", "4.59mm",
            "TranslateVectorY:=", "0mm",
            "TranslateVectorZ:=", "0mm"
        ])

    # Assign lumped RLC to rectangle
    oModule.AssignLumpedRLC(
        [
            "NAME:LumpRLC1",
            "Objects:=", ["Rectangle2"],
            [
                "NAME:CurrentLine",
                "Start:=", ["-2.345mm", str(end_y / 1000) + "mm", "0mm"],  # Position calculation
                "End:=", ["-2.245mm", str(end_y / 1000) + "mm", "0mm"]  # Position calculation
            ],
            "RLC Type:=", "Parallel",
            "UseResist:=", True,
            "Resistance:=", "50ohm",
            "UseInduct:=", False,
            "UseCap:=", False
        ])

    # Assign lumped RLC to another rectangle
    oModule.AssignLumpedRLC(
        [
            "NAME:LumpRLC2",
            "Objects:=", ["Rectangle5"],
            [
                "NAME:CurrentLine",
                "Start:=", ["2.245mm", str(end_y / 1000) + "mm", "0mm"],  # Position calculation
                "End:=", ["2.345mm", str(end_y / 1000) + "mm", "0mm"]  # Position calculation
            ],
            "RLC Type:=", "Parallel",
            "UseResist:=", True,
            "Resistance:=", "50ohm",
            "UseInduct:=", False,
            "UseCap:=", False
        ])

    # Create another box
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:=", "-2.6mm",
            "YPosition:=", "-0.6mm",
            "ZPosition:=", "0mm",
            "XSize:=", "5.2mm",
            "YSize:=", "3mm",
            "ZSize:=", "-1mm"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Box2",
            "Flags:=", "",
            "Color:=", "(143 175 143)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"vacuum\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])

    # Modify box properties
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DCmdTab",
                [
                    "NAME:PropServers",
                    "Box2:CreateBox:1"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Position",
                        "X:=", "-2.6mm",
                        "Y:=", "-0.6mm",
                        "Z:=", "0.85mm"
                    ],
                    [
                        "NAME:ZSize",
                        "Value:=", "-2125um"
                    ]
                ]
            ]
        ])

    # Modify transparency
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DAttributeTab",
                [
                    "NAME:PropServers",
                    "Box2"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Transparent",
                        "Value:=", 0.8
                    ]
                ]
            ]
        ])

    # Set analysis
    oModule = oDesign.GetModule("AnalysisSetup")
    oModule.InsertSetup("HfssEigen",
                        [
                            "NAME:Setup1",
                            "MinimumFrequency:=", str(freq - 1) + "GHz",  # Minimum qubit frequency
                            "NumModes:=", 1,
                            "MaxDeltaFreq:=", 10,  # Delta s
                            "ConvergeOnRealFreq:=", False,
                            "MaximumPasses:=", 99,  # Maximum passes
                            "MinimumPasses:=", 1,
                            "MinimumConvergedPasses:=", 1,
                            "PercentRefinement:=", 30,
                            "IsEnabled:=", True,
                            [
                                "NAME:MeshLink",
                                "ImportMesh:=", False
                            ],
                            "BasisOrder:=", 1,
                            "DoLambdaRefine:=", True,
                            "DoMaterialLambda:=", True,
                            "SetLambdaTarget:=", False,
                            "Target:=", 0.2,
                            "UseMaxTetIncrease:=", False
                        ])

    # Save the project
    oProject.SaveAs(folder_path + "/rdls_tmls_simulation_eig.aedt", True)  # Path
    oDesign = oProject.SetActiveDesign("HFSSDesign1")
    oDesign.AnalyzeAllNominal()

    # Export eigenmodes
    oModule = oDesign.GetModule("Solutions")
    oModule.ExportEigenmodes("Setup1 : LastAdaptive", "",
                             folder_path + "/Projecteda21_HFSSDesign1.eig")  # Path to save eig file

    def open_with_notepad(file_path):
        """
        Open file with Notepad.

        Input:
            file_path: String, file path.
        """
        import subprocess
        try:
            subprocess.Popen(['notepad.exe', file_path])
        except FileNotFoundError:
            print("Notepad application not found.")

    file_path = folder_path + "/Projecteda21_HFSSDesign1.eig"  # Path to save eig file
    open_with_notepad(file_path)


def dri_2_0(folder_path, gds_path, start_freq, end_freq, end_y):
    """
    Execute the driven model simulation.

    Input:
        folder_path: String, save path.
        gds_path: String, GDS file path.
        start_freq: String, starting frequency.
        end_freq: String, ending frequency.
        end_y: Float, y-axis endpoint.
    """
    import win32com.client  # Import win32com library

    oAnsoftApp = win32com.client.Dispatch('AnsoftHfss.HfssScriptInterface')
    oDesktop = oAnsoftApp.GetAppDesktop()
    oProject = oDesktop.NewProject("Projecteda3")
    oProject.InsertDesign("HFSS", "HFSSDesign1", "DrivenModal", "")
    oDesign = oProject.SetActiveDesign("HFSSDesign1")
    oEditor = oDesign.SetActiveEditor("3D Modeler")

    # Import GDS file
    oEditor.ImportGDSII(
        [
            "NAME:options",
            "FileName:=", gds_path,  # Path to import GDS
            "FlattenHierarchy:=", True,
            "ImportMethod:=", 1,
            [
                "NAME:LayerMap",
                [
                    "NAME:LayerMapInfo",
                    "LayerNum:=", 0,
                    "DestLayer:=", "Signal0",
                    "layer_type:=", "signal"
                ]
            ],
            "OrderMap:=", [
            "entry:=", [
                "order:=", 0,
                "layer:=", "Signal0"
            ]
        ]
        ])

    # Create rectangle
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", "0mm",
            "YStart:=", "-0.01mm",
            "ZStart:=", "0mm",
            "Width:=", "0.002mm",
            "Height:=", "0.02mm",
            "WhichAxis:=", "Z"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Rectangle4",
            "Flags:=", "",
            "Color:=", "(143 175 143)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"vacuum\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])

    # Unite rectangle with signal lines
    oEditor.Unite(
        [
            "NAME:Selections",
            "Selections:=",
            "Rectangle4,Signal0_5,Signal0_6,Signal0_7,Signal0_8,Signal0_9,Signal0_10,Signal0_11,Signal0_12,Signal0_13,Signal0_14,Signal0_15,Signal0_16,Signal0_17,Signal0_18,Signal0_19,Signal0_20,Signal0_21,Signal0_22,Signal0_23,Signal0_24,Signal0_25,Signal0_26,Signal0_27,Signal0_28,Signal0_29,Signal0_30,Signal0_31,Signal0_32,Signal0_33,Signal0_34,Signal0_35,Signal0_36,Signal0_37,Signal0_38,Signal0_39,Signal0_40,Signal0_41,Signal0_42,Signal0_43"
        ],
        [
            "NAME:UniteParameters",
            "KeepOriginals:=", False
        ])

    # Again unite signal lines
    oEditor.Unite(
        [
            "NAME:Selections",
            "Selections:=", "Signal0_1,Signal0_2,Signal0_3,Signal0_4"
        ],
        [
            "NAME:UniteParameters",
            "KeepOriginals:=", False
        ])

    # Create another rectangle
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", "-2.6mm",
            "YStart:=", "-0.6mm",
            "ZStart:=", "0mm",
            "Width:=", "5.2mm",
            "Height:=", "3mm",
            "WhichAxis:=", "Z"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Rectangle1",
            "Flags:=", "",
            "Color:=", "(143 175 143)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"vacuum\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])

    # Subtract rectangle from signal lines
    oEditor.Subtract(
        [
            "NAME:Selections",
            "Blank Parts:=", "Rectangle1",
            "Tool Parts:=", "Signal0_1,Rectangle4"
        ],
        [
            "NAME:SubtractParameters",
            "KeepOriginals:=", False
        ])

    # Create a box
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:=", "-2.6mm",
            "YPosition:=", "-0.6mm",
            "ZPosition:=", "0mm",
            "XSize:=", "5.2mm",
            "YSize:=", "3mm",
            "ZSize:=", "0mm"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Box1",
            "Flags:=", "",
            "Color:=", "(143 175 143)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"vacuum\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])

    # Modify box properties
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DCmdTab",
                [
                    "NAME:PropServers",
                    "Box1:CreateBox:1"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:ZSize",
                        "Value:=", "-450um"
                    ]
                ]
            ]
        ])

    # Again modify box properties
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DAttributeTab",
                [
                    "NAME:PropServers",
                    "Box1"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Color",
                        "R:=", 192,
                        "G:=", 192,
                        "B:=", 192
                    ]
                ]
            ]
        ])

    # Modify box material properties
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DAttributeTab",
                [
                    "NAME:PropServers",
                    "Box1"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Material",
                        "Value:=", "\"sapphire\""
                    ]
                ]
            ]
        ])

    # Set boundary conditions
    oModule = oDesign.GetModule("BoundarySetup")
    oModule.AssignPerfectE(
        [
            "NAME:PerfE1",
            "Objects:=", ["Rectangle1"],
            "InfGroundPlane:=", False
        ])

    # Set solution type to driven mode
    oDesign.SetSolutionType("Eigenmode", False)

    # Again configure boundary conditions
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", "-2.245mm",
            "YStart:=", str(end_y / 1000 - 0.06) + "mm",  # Position calculation
            "ZStart:=", "0mm",
            "Width:=", "-0.1mm",
            "Height:=", "0.12mm",
            "WhichAxis:=", "Z"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Rectangle2",
            "Flags:=", "",
            "Color:=", "(143 175 143)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"vacuum\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])

    # Copy rectangle
    oEditor.Copy(
        [
            "NAME:Selections",
            "Selections:=", "Rectangle2"
        ])

    # Paste and move rectangle
    oEditor.Paste()
    oEditor.Move(
        [
            "NAME:Selections",
            "Selections:=", "Rectangle5",
            "NewPartsModelFlag:=", "Model"
        ],
        [
            "NAME:TranslateParameters",
            "TranslateVectorX:=", "4.59mm",
            "TranslateVectorY:=", "0mm",
            "TranslateVectorZ:=", "0mm"
        ])

    # Assign lumped port to rectangle
    oModule.AssignLumpedPort(
        [
            "NAME:1",
            "Objects:=", ["Rectangle2"],
            "DoDeembed:=", False,
            "RenormalizeAllTerminals:=", True,
            [
                "NAME:Modes",
                [
                    "NAME:Mode1",
                    "ModeNum:=", 1,
                    "UseIntLine:=", True,
                    [
                        "NAME:IntLine",
                        "Start:=", ["-2.345mm", str(end_y / 1000) + "mm", "0mm"],  # Position calculation
                        "End:=", ["-2.245mm", str(end_y / 1000) + "mm", "0mm"]  # Position calculation
                    ],
                    "AlignmentGroup:=", 0,
                    "CharImp:=", "Zpi",
                    "RenormImp:=", "50ohm"
                ]
            ],
            "ShowReporterFilter:=", False,
            "ReporterFilter:=", [True],
            "Impedance:=", "50ohm"
        ])

    # Assign lumped port to another rectangle
    oModule.AssignLumpedPort(
        [
            "NAME:2",
            "Objects:=", ["Rectangle5"],
            "DoDeembed:=", False,
            "RenormalizeAllTerminals:=", True,
            [
                "NAME:Modes",
                [
                    "NAME:Mode1",
                    "ModeNum:=", 1,
                    "UseIntLine:=", True,
                    [
                        "NAME:IntLine",
                        "Start:=", ["2.245mm", str(end_y / 1000) + "mm", "0mm"],  # Position calculation
                        "End:=", ["2.345mm", str(end_y / 1000) + "mm", "0mm"]  # Position calculation
                    ],
                    "AlignmentGroup:=", 0,
                    "CharImp:=", "Zpi",
                    "RenormImp:=", "50ohm"
                ]
            ],
            "ShowReporterFilter:=", False,
            "ReporterFilter:=", [True],
            "Impedance:=", "50ohm"
        ])

    # Create a box
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:=", "-2.6mm",
            "YPosition:=", "-0.6mm",
            "ZPosition:=", "0mm",
            "XSize:=", "5.2mm",
            "YSize:=", "3mm",
            "ZSize:=", "-1mm"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Box2",
            "Flags:=", "",
            "Color:=", "(143 175 143)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", "\"vacuum\"",
            "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", True,
            "ShellElement:=", False,
            "ShellElementThickness:=", "0mm",
            "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False,
            "IsLightweight:=", False
        ])

    # Modify box properties
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DCmdTab",
                [
                    "NAME:PropServers",
                    "Box2:CreateBox:1"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Position",
                        "X:=", "-2.6mm",
                        "Y:=", "-0.6mm",
                        "Z:=", "0.85mm"
                    ],
                    [
                        "NAME:ZSize",
                        "Value:=", "-2125um"
                    ]
                ]
            ]
        ])

    # Modify transparency
    oEditor.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DAttributeTab",
                [
                    "NAME:PropServers",
                    "Box2"
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:Transparent",
                        "Value:=", 0.8
                    ]
                ]
            ]
        ])

    # Set analysis
    oModule = oDesign.GetModule("AnalysisSetup")
    oModule.InsertSetup("HfssDriven",
                        [
                            "NAME:Setup1",
                            "SolveType:=", "Broadband",
                            [
                                "NAME:MultipleAdaptiveFreqsSetup",
                                "Low:=", start_freq,
                                "High:=", end_freq
                            ],
                            "MaxDeltaS:=", 0.02,
                            "UseMatrixConv:=", False,
                            "MaximumPasses:=", 99,
                            "MinimumPasses:=", 1,
                            "MinimumConvergedPasses:=", 1,
                            "PercentRefinement:=", 30,
                            "IsEnabled:=", True,
                            [
                                "NAME:MeshLink",
                                "ImportMesh:=", False
                            ],
                            "BasisOrder:=", 1,
                            "DoLambdaRefine:=", True,
                            "DoMaterialLambda:=", True,
                            "SetLambdaTarget:=", False,
                            "Target:=", 0.3333,
                            "UseMaxTetIncrease:=", False,
                            "PortAccuracy:=", 2,
                            "UseABCOnPort:=", False,
                            "SetPortMinMaxTri:=", False,
                            "UseDomains:=", False,
                            "UseIterativeSolver:=", False,
                            "SaveRadFieldsOnly:=", False,
                            "SaveAnyFields:=", True,
                            "IESolverType:=", "Auto",
                            "LambdaTargetForIESolver:=", 0.15,
                            "UseDefaultLambdaTgtForIESolver:=", True,
                            "IE Solver Accuracy:=", "Balanced"
                        ])

    # Save the project
    oProject.SaveAs(folder_path + "/rdls_tmls_simulation_dri.aedt", True)  # Rename 
    oDesign.AnalyzeAllNominal()

    # Create report and export data
    oModule = oDesign.GetModule("ReportSetup")
    oModule.CreateReport("S Parameter Plot 1", "Modal Solution Data", "Rectangular Plot", "Setup1 : Sweep",
                         [
                             "Domain:=", "Sweep"
                         ],
                         [
                             "Freq:=", ["All"]
                         ],
                         [
                             "X Component:=", "Freq",
                             "Y Component:=", ["dB(S(2,1))"]
                         ])

    # Export S parameters to a CSV file
    oModule.ExportToFile("S Parameter Plot 1", folder_path + "/S Parameter Plot 1.csv", False)  # Path
    # Export S parameters to a PNG file
    oModule.ExportImageToFile("S Parameter Plot 1", folder_path + "/S Parameter Plot 1.png", 1129, 674)  # Path