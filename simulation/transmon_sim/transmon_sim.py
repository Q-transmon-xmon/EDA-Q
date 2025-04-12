#########################################################################
# File Name: transmon_sim.py
# Function Description: Module for superconducting qubit simulation.
#                       Includes functions for modeling qubits, frequency sweeping, and capacitance matrix computation.
#########################################################################

import win32com.client
import numpy as np
import pathlib
import pandas as pd
import re
import toolbox
from addict import Dict

from simulation.transmon_sim import couple_pad
from IPython.display import display


def simulation(qubit, freq, dir_name, file_name, result_name):
    """
    Main function for simulating qubits, setting frequency points to obtain the capacitance matrix.

    Inputs:
        qubit: Qubit object with varying coupled pads.
        freq: Float, specifies the frequency of the qubit.
        dir_name: String, folder path for storing simulation results.
        file_name: String, name of the simulation input file.
        result_name: String, name of the file storing simulation results.

    Outputs:
        Cq: Float, capacitance parameter of the qubit.
        Ec: Float, Josephson energy of the qubit.

    """
    ######################## Interface ##############################
    print("Transmon simulation")
    frequency = freq

    toolbox.jg_and_create_path(dir_name)

    pad_options = qubit.pad_options

    ground = Dict()
    ground['x'] = -1
    ground['y'] = -1
    ground['width'] = 3
    ground['height'] = 3

    # Large pocket
    chip = Dict()
    chip['left_lower'] = [qubit.gds_pos[0] - qubit.width / 2 - qubit.cpw_extend[0],
                          qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[4] - qubit.pad_height[4] -
                          qubit.cpw_extend[4]]
    chip['width'] = qubit.width + qubit.cpw_extend[0] + qubit.cpw_extend[2]
    chip['height'] = qubit.gap + qubit.height * 2 + qubit.pad_gap[1] + qubit.pad_gap[4] + qubit.pad_height[1] + \
                     qubit.pad_height[4] + qubit.cpw_extend[1] + qubit.cpw_extend[4]

    # Upper and lower pads
    pocket = Dict()
    pocket['upper_lower'] = [qubit.gds_pos[0] - qubit.width / 2, qubit.gds_pos[1] + qubit.gap / 2]
    pocket['lower_lower'] = [qubit.gds_pos[0] - qubit.width / 2, qubit.gds_pos[1] - qubit.gap / 2 - qubit.height]
    pocket['height'] = qubit.height
    pocket['width'] = qubit.width

    # Pads
    pad = Dict()
    if pad_options[0] == 1:
        pad_points = []
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2 - qubit.cpw_extend[0],
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[0] + qubit.pad_height[
                               0] / 2 + qubit.cpw_width[0] / 2])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[0] + qubit.pad_height[
                               0] / 2 + qubit.cpw_width[0] / 2])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[0] + qubit.pad_height[0]])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2 + qubit.pad_width[0],
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[0] + qubit.pad_height[0]])

        pad_points.append([qubit.gds_pos[0] - qubit.width / 2 + qubit.pad_width[0],
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[0]])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[0]])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[0] + qubit.pad_height[
                               0] / 2 - qubit.cpw_width[0] / 2])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2 - qubit.cpw_extend[0],
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[0] + qubit.pad_height[
                               0] / 2 - qubit.cpw_width[0] / 2])
        for i in range(len(pad_points)):
            pad_points[i] = [pad_points[i][0] * 10e-4, pad_points[i][1] * 10e-4]
        pad['upper_left'] = pad_points

    if pad_options[1] == 1:
        pad_points = []
        pad_points.append([qubit.gds_pos[0] + qubit.cpw_width[1] / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[1] + qubit.pad_height[1] +
                           qubit.cpw_extend[1]])
        pad_points.append([qubit.gds_pos[0] + qubit.cpw_width[1] / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[1] + qubit.pad_height[1]])
        pad_points.append([qubit.gds_pos[0] + qubit.pad_width[1] / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[1] + qubit.pad_height[1]])
        pad_points.append([qubit.gds_pos[0] + qubit.pad_width[1] / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[1]])

        pad_points.append([qubit.gds_pos[0] - qubit.pad_width[1] / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[1]])
        pad_points.append([qubit.gds_pos[0] - qubit.pad_width[1] / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[1] + qubit.pad_height[1]])
        pad_points.append([qubit.gds_pos[0] - qubit.cpw_width[1] / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[1] + qubit.pad_height[1]])
        pad_points.append([qubit.gds_pos[0] - qubit.cpw_width[1] / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[1] + qubit.pad_height[1] +
                           qubit.cpw_extend[1]])
        for i in range(len(pad_points)):
            pad_points[i] = [pad_points[i][0] * 10e-4, pad_points[i][1] * 10e-4]
        pad['upper_middle'] = pad_points

    if pad_options[2] == 1:
        pad_points = []
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2 + qubit.cpw_extend[2],
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[2] + qubit.pad_height[
                               2] / 2 + qubit.cpw_width[2] / 2])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[2] + qubit.pad_height[
                               2] / 2 + qubit.cpw_width[2] / 2])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[2] + qubit.pad_height[2]])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2 - qubit.pad_width[2],
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[2] + qubit.pad_height[2]])

        pad_points.append([qubit.gds_pos[0] + qubit.width / 2 - qubit.pad_width[2],
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[2]])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[2]])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2,
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[2] + qubit.pad_height[
                               2] / 2 - qubit.cpw_width[2] / 2])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2 + qubit.cpw_extend[2],
                           qubit.gds_pos[1] + qubit.gap / 2 + qubit.height + qubit.pad_gap[2] + qubit.pad_height[
                               2] / 2 - qubit.cpw_width[2] / 2])
        for i in range(len(pad_points)):
            pad_points[i] = [pad_points[i][0] * 10e-4, pad_points[i][1] * 10e-4]
        pad['upper_right'] = pad_points

    if pad_options[3] == 1:
        pad_points = []
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2 - qubit.cpw_extend[3],
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[3] - qubit.pad_height[
                               3] / 2 - qubit.cpw_width[3] / 2])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[3] - qubit.pad_height[
                               3] / 2 - qubit.cpw_width[3] / 2])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[3] - qubit.pad_height[3]])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2 + qubit.pad_width[3],
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[3] - qubit.pad_height[3]])

        pad_points.append([qubit.gds_pos[0] - qubit.width / 2 + qubit.pad_width[3],
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[3]])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[3]])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[3] - qubit.pad_height[
                               3] / 2 + qubit.cpw_width[3] / 2])
        pad_points.append([qubit.gds_pos[0] - qubit.width / 2 - qubit.cpw_extend[3],
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[3] - qubit.pad_height[
                               3] / 2 + qubit.cpw_width[3] / 2])
        for i in range(len(pad_points)):
            pad_points[i] = [pad_points[i][0] * 10e-4, pad_points[i][1] * 10e-4]
        pad['lower_left'] = pad_points

    if pad_options[4] == 1:
        pad_points = []
        pad_points.append([qubit.gds_pos[0] + qubit.cpw_width[4] / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[4] - qubit.pad_height[4] -
                           qubit.cpw_extend[4]])
        pad_points.append([qubit.gds_pos[0] + qubit.cpw_width[4] / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[4] - qubit.pad_height[4]])
        pad_points.append([qubit.gds_pos[0] + qubit.pad_width[4] / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[4] - qubit.pad_height[4]])
        pad_points.append([qubit.gds_pos[0] + qubit.pad_width[4] / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[4]])

        pad_points.append([qubit.gds_pos[0] - qubit.pad_width[4] / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[4]])
        pad_points.append([qubit.gds_pos[0] - qubit.pad_width[4] / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[4] - qubit.pad_height[4]])
        pad_points.append([qubit.gds_pos[0] - qubit.cpw_width[4] / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[4] - qubit.pad_height[4]])
        pad_points.append([qubit.gds_pos[0] - qubit.cpw_width[4] / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[4] - qubit.pad_height[4] -
                           qubit.cpw_extend[4]])
        for i in range(len(pad_points)):
            pad_points[i] = [pad_points[i][0] * 10e-4, pad_points[i][1] * 10e-4]
        pad['lower_middle'] = pad_points

    if pad_options[5] == 1:
        pad_points = []
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2 + qubit.cpw_extend[5],
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[5] - qubit.pad_height[
                               5] / 2 - qubit.cpw_width[5] / 2])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[5] - qubit.pad_height[
                               5] / 2 - qubit.cpw_width[5] / 2])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[5] - qubit.pad_height[5]])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2 - qubit.pad_width[5],
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[5] - qubit.pad_height[5]])

        pad_points.append([qubit.gds_pos[0] + qubit.width / 2 - qubit.pad_width[5],
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[5]])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[5]])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2,
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[5] - qubit.pad_height[
                               2] / 2 + qubit.cpw_width[5] / 2])
        pad_points.append([qubit.gds_pos[0] + qubit.width / 2 + qubit.cpw_extend[5],
                           qubit.gds_pos[1] - qubit.gap / 2 - qubit.height - qubit.pad_gap[5] - qubit.pad_height[
                               5] / 2 + qubit.cpw_width[2] / 2])
        for i in range(len(pad_points)):
            pad_points[i] = [pad_points[i][0] * 10e-4, pad_points[i][1] * 10e-4]
        pad['lower_right'] = pad_points

    ######################## Interface ##############################

    oEditor, oDesign, oProject = create_Q3D(toolbox.get_file_name_from_path(file_name))
    name = []
    # Metallically
    couple_pad.create_rectangle(oEditor, ground.x, ground.y, ground.width, ground.height, 'Ground')
    name.append('Ground')
    # pocket chip[left_lower]

    couple_pad.create_rectangle(oEditor, chip.left_lower[0] * 10e-4, chip.left_lower[1] * 10e-4, chip.width * 10e-4,
                                chip.height * 10e-4, 'cut')
    # Minus operation

    couple_pad.subtract(oEditor, 'Ground', 'cut')

    # pocket.upper_lower[0]
    couple_pad.create_rectangle(oEditor, pocket.upper_lower[0] * 10e-4, pocket.upper_lower[1] * 10e-4,
                                pocket.width * 10e-4, pocket.height * 10e-4, 'top_pad')
    name.append('top_pad')

    couple_pad.create_rectangle(oEditor, pocket.lower_lower[0] * 10e-4, pocket.lower_lower[1] * 10e-4,
                                pocket.width * 10e-4, pocket.height * 10e-4, 'bottom_pad')
    name.append('bottom_pad')

    # Each pad is drawn according to the small pads of qubits
    couple_pad.couple_pad_auto(oEditor, pad)

    # Substrate modeling
    create_solids(oEditor, -1, -1, 0, 3, 3)
    if pad_options[0] == 1:
        name.append('upper_left')
    if pad_options[1] == 1:
        name.append('upper_middle')
    if pad_options[2] == 1:
        name.append('upper_right')
    if pad_options[3] == 1:
        name.append('lower_left')
    if pad_options[4] == 1:
        name.append('lower_middle')
    if pad_options[5] == 1:
        name.append('lower_right')
    # Set the metal excitation
    oModule = boundarysetup(oDesign, name)

    autoidentifyNets(oModule)

    analysissetup(oDesign, frequency)  # frequency of the qubit
    SaveAs(oProject, dir_name + file_name)
    analyzeallnominal(oDesign)
    exportMatrixData(oDesign, frequency, dir_name + result_name)
    Cq, Ec = show_result(dir_name + result_name)

    return Cq, Ec


def show_result(path):
    """
    Plot the capacitance matrix.

    Inputs:
        path: String, path of the stored file.

    Outputs:
        Computed Maxwell capacitance matrix.
    """

    # Compute parameters
    e = 1.60217657e-19  # Electron charge
    h = 6.62606957e-34  # Planck's constant
    hbar = 1.0545718E-34  # Reduced Planck's constant

    p = pathlib.Path(path)

    m = p.read_text().split('\n')

    cm = m[m.index('Capacitance Matrix'):m.index('Conductance Matrix') - 1]

    pattern = '(?<=C Units:)(.+?)((?<![^a-zA-Z0-9_\u4e00-\u9fa5])(?=[^a-zA-Z0-9_\u4e00-\u9fa5])|(?<=[^a-zA-Z0-9_\u4e00-\u9fa5])(?![^a-zA-Z0-9_\u4e00-\u9fa5])|$)'

    rowLabels = []
    column_labels = []
    data = []

    for i in range(len(cm)):
        a = [x for x in cm[i].split('\t') if x != '']
        if i == 1:
            column_labels = a
        elif i > 1:
            rowLabels.append(a[0])
            data.append([f"{str(round(float(x), 2))}" for x in a[1:]])

    df = pd.DataFrame(data, index=rowLabels, columns=column_labels)
    display(df)

    upper_label = []
    lower_label = []

    for item in column_labels:
        if 'upper' in item:
            upper_label.append(item)
        if 'lower' in item:
            lower_label.append(item)

    Cs = -float(df["bottom_pad"]["top_pad"])
    Cg = np.zeros(2)
    Cg[0] = -float(df["bottom_pad"]["Ground"])
    Cg[1] = -float(df["top_pad"]["Ground"])
    Cbus = np.zeros(2)
    if not upper_label:
        for i in range(len(upper_label)):
            Cbus[0] -= float(df["bottom_pad"][upper_label[i]])
            Cbus[1] -= float(df["top_pad"][upper_label[i]])

    if not lower_label:
        for i in range(len(lower_label)):
            Cbus[0] -= float(df["bottom_pad"][lower_label[i]])
            Cbus[1] -= float(df["top_pad"][lower_label[i]])

    C1S = Cg[0] + Cbus[0]
    C2S = Cg[1] + Cbus[1]
    Cq = Cs + C1S * C2S / (C1S + C2S)
    print(f"Cq={str(round(Cq, 2)) + 'fF'}")
    EC_a = e ** 2 / (2 * Cq * 1e15) / hbar  # Angular frequency, unit MHz
    EC = EC_a / (2 * np.pi * 1e6)
    print(f"EC={str(round(EC, 2)) + 'MHz'}")

    return Cq, EC


def create_Q3D(project_name):
    """
    Open the HFSS software and create a Q3D project.

    Outputs:
        oEditor: Q3D editor object.
        oDesign: Q3D design object.
        oProject: Q3D project object.
    """
    print("Starting Q3D simulation")
    oAnsoftApp = win32com.client.Dispatch('AnsoftHfss.HfssScriptInterface')
    oDesktop = oAnsoftApp.GetAppDesktop()
    oProject = oDesktop.NewProject()
    oProject.InsertDesign("Q3D Extractor", project_name, "", "")
    oDesign = oProject.SetActiveDesign(project_name)  # "Q3DDesign1"
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    return oEditor, oDesign, oProject


def create_solids(oEditor, X, Y, Z, width, height):
    """
    Substrate modeling.

    Inputs:
        X: Float, X coordinate of the substrate.
        Y: Float, Y coordinate of the substrate.
        Z: Float, Z coordinate of the substrate.
        width: Float, width of the substrate.
        height: Float, height of the substrate.

    Outputs:
        None
    """
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:=", f"{X} mm",
            "YPosition:=", f"{Y} mm",
            "ZPosition:=", f"{Z} mm",
            "XSize:=", f"{width} mm",
            "YSize:=", f"{height} mm",
            "ZSize:=", "-430um"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Box1",
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


def boundarysetup(oDesign, list):
    """
    Set boundary conditions according to the actual low-temperature test environment of the quantum chip.

    Inputs:
        oDesign: Q3D design object.
        list: List of boundary objects.

    Outputs:
        oModule: Boundary setup module object.
    """
    oModule = oDesign.GetModule("BoundarySetup")
    oModule.AssignThinConductor(
        [
            "NAME:ThinCond1",
            "Objects:=", list,
            "Material:=", "pec",
            "Thickness:=", "100nm"
        ])
    return oModule


def autoidentifyNets(oModule):
    """
    Automatically identify nets.

    Inputs:
        oModule: Q3D module object.
    """
    oModule.AutoIdentifyNets()


def analysissetup(oDesign, F):
    """
    Set up analysis parameters.

    Inputs:
        oDesign: Q3D design object.
        F: Float, frequency.

    Outputs:
        None
    """
    oModule = oDesign.GetModule("AnalysisSetup")
    oModule.InsertSetup("Matrix",
                        [
                            "NAME:Setup1",
                            "AdaptiveFreq:=", f"{F}GHz",
                            "SaveFields:=", False,
                            "Enabled:=", True,
                            [
                                "NAME:Cap",
                                "MaxPass:=", 10,
                                "MinPass:=", 1,
                                "MinConvPass:=", 1,
                                "PerError:=", 1,
                                "PerRefine:=", 30,
                                "AutoIncreaseSolutionOrder:=", True,
                                "SolutionOrder:=", "High",
                                "Solver Type:=", "Iterative"
                            ]
                        ])


def SaveAs(oProject, path):
    """
    Save the project.

    Inputs:
        oProject: Q3D project object.
        path: String, save path.
    """
    oProject.SaveAs(path, True)


def analyzeallnominal(oDesign):
    """
    Analyze all nominal conditions.

    Inputs:
        oDesign: Q3D design object.
    """
    oDesign.AnalyzeAllNominal()


def exportMatrixData(oDesign, F, path):
    """
    Export matrix data.

    Inputs:
        oDesign: Q3D design object.
        F: Float, frequency.
        path: String, export path.
    """
    import toolbox
    oDesign.ExportMatrixData(path, "C", "", "Setup1:LastAdaptive", "Original", "ohm", "nH", "fF", "mSie", F * 10 ** 9,
                             "Maxwell", 0, False, 15, 20, 1)
