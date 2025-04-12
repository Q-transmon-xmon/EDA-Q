#########################################################################
# File Name: couple_pad.py
# Function Description: This module contains functions for creating geometric
#                      shapes and performing Boolean operations.
#                      It provides functionality for creating rectangles and
#                      polygons, as well as subtraction and union operations.
#########################################################################

def subtract(oEditor, Name1, Name2):
    """
    Perform a subtraction operation to remove a specified part of a geometric shape.

    Inputs:
        oEditor: The editor object used to execute geometric operations.
        Name1: String, the name of the geometric body to be subtracted.
        Name2: String, the name of the geometric body to be subtracted from.

    Outputs:
        No return value.
    """
    oEditor.Subtract(
        [
            "NAME:Selections",
            "Blank Parts:=", f"{Name1}",
            "Tool Parts:=", f"{Name2}"
        ],
        [
            "NAME:SubtractParameters",
            "KeepOriginals:=", False
        ]
    )


def create_rectangle(oEditor, X, Y, width, height, Name):
    """
    Create a rectangle and add it to the specified editor.

    Inputs:
        oEditor: The editor object used to execute geometric operations.
        X: Float, the X coordinate of the rectangle's bottom-left corner.
        Y: Float, the Y coordinate of the rectangle's bottom-left corner.
        width: Float, the width of the rectangle.
        height: Float, the height of the rectangle.
        Name: String, the name of the rectangle.

    Outputs:
        No return value.
    """
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", f"{X} mm",
            "YStart:=", f"{Y} mm",
            "ZStart:=", "0 mm",
            "Width:=", f"{width} mm",
            "Height:=", f"{height} mm",
            "WhichAxis:=", "Z"
        ],
        [
            "NAME:Attributes",
            "Name:=", f"{Name}",
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
        ]
    )


# Automatically create coupling pads based on the provided point dictionary
def couple_pad_auto(oEditor, points_dict):
    """
    Automatically create coupling pads by generating a polygon from the provided
    point dictionary and performing necessary subtraction operations.

    Inputs:
        oEditor: The editor object used to execute geometric operations.
        points_dict: Dictionary containing arrays of points for different positions.

    Outputs:
        No return value.
    """
    for k, v in points_dict.items():
        points = v
        points_x = []
        points_y = []
        for i in range(len(points)):
            points_x.append(points[i][0])
            points_y.append(points[i][1])

        add = ["NAME:PolylineParameters",
               "IsPolylineCovered:=", True,
               "IsPolylineClosed:=", True]

        add1 = ["NAME:PolylinePoints"]
        for i in range(len(points)):
            add1.append(["NAME:PLPoint",
                         "X:=", f"{points_x[i]}mm",
                         "Y:=", f"{points_y[i]}mm",
                         "Z:=", "0mm"])
        add1.append(["NAME:PLPoint",
                     "X:=", f"{points_x[0]}mm",
                     "Y:=", f"{points_y[0]}mm",
                     "Z:=", "0mm"])
        add.append(add1)

        add2 = ["NAME:PolylineSegments"]
        for i in range(len(points)):
            add2.append(["NAME:PLSegment",
                         "SegmentType:=", "Line",
                         "StartIndex:=", i,
                         "NoOfPoints:=", 2])
        add.append(add2)
        add.append([
            "NAME:PolylineXSection",
            "XSectionType:=", "None",
            "XSectionOrient:=", "Auto",
            "XSectionWidth:=", "0mm",
            "XSectionTopWidth:=", "0mm",
            "XSectionHeight:=", "0mm",
            "XSectionNumSegments:=", "0",
            "XSectionBendType:=", "Corner"
        ])

        last_add = [
            "NAME:Attributes",
            "Name:=", f"{k}",
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
        ]

        oEditor.CreatePolyline(add, last_add)

        if k == 'upper_left':
            create_rectangle(oEditor, points[-1][0], points[-1][1] - 0.01, -0.03, 0.03, f"{k}_cut")
            subtract(oEditor, 'Ground', f"{k}_cut")
        elif k == 'upper_middle':
            create_rectangle(oEditor, points[-1][0] - 0.01, points[-1][1], 0.03, 0.03, f"{k}_cut")
            subtract(oEditor, 'Ground', f"{k}_cut")
        elif k == 'upper_right':
            create_rectangle(oEditor, points[-1][0], points[-1][1] - 0.01, 0.03, 0.03, f"{k}_cut")
            subtract(oEditor, 'Ground', f"{k}_cut")
        elif k == 'lower_left':
            create_rectangle(oEditor, points[0][0], points[0][1] - 0.01, -0.03, 0.03, f"{k}_cut")
            subtract(oEditor, 'Ground', f"{k}_cut")
        elif k == 'lower_middle':
            create_rectangle(oEditor, points[-1][0] - 0.01, points[-1][1], 0.03, -0.03, f"{k}_cut")
            subtract(oEditor, 'Ground', f"{k}_cut")
        elif k == 'lower_right':
            create_rectangle(oEditor, points[0][0], points[1][1] - 0.01, 0.03, 0.03, f"{k}_cut")
            subtract(oEditor, 'Ground', f"{k}_cut")


def top_left(oEditor, points, name):
    """
    Create a polygon in the upper-left region and perform necessary subtraction operations.

    Inputs:
        oEditor: The editor object used to execute geometric operations.
        points: List containing the coordinates of the polygon vertices.
        name: String, the name of the region.

    Outputs:
        No return value.
    """
    points_x = []
    points_y = []
    for i in range(len(points)):
        points_x.append(points[i][0])
        points_y.append(points[i][1])

    add = ["NAME:PolylineParameters",
           "IsPolylineCovered:=", True,
           "IsPolylineClosed:=", True]

    add1 = ["NAME:PolylinePoints"]
    for i in range(len(points)):
        add1.append(["NAME:PLPoint",
                     "X:=", f"{points_x[i]}mm",
                     "Y:=", f"{points_y[i]}mm",
                     "Z:=", "0mm"])
    add1.append(["NAME:PLPoint",
                 "X:=", f"{points_x[0]}mm",
                 "Y:=", f"{points_y[0]}mm",
                 "Z:=", "0mm"])
    add.append(add1)

    add2 = ["NAME:PolylineSegments"]
    for i in range(len(points)):
        add2.append(["NAME:PLSegment",
                     "SegmentType:=", "Line",
                     "StartIndex:=", i,
                     "NoOfPoints:=", 2])
    add.append(add2)
    add.append([
        "NAME:PolylineXSection",
        "XSectionType:=", "None",
        "XSectionOrient:=", "Auto",
        "XSectionWidth:=", "0mm",
        "XSectionTopWidth:=", "0mm",
        "XSectionHeight:=", "0mm",
        "XSectionNumSegments:=", "0",
        "XSectionBendType:=", "Corner"
    ])

    last_add = [
        "NAME:Attributes",
        "Name:=", f"{name}",
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
    ]

    oEditor.CreatePolyline(add, last_add)

    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", "0mm",
            "YStart:=", f"{points[-1][1] - 0.010}mm",
            "ZStart:=", "0mm",
            "Width:=", f"{-0.03}mm",
            "Height:=", f"{0.03}mm",
            "WhichAxis:=", "Z"
        ],
        [
            "NAME:Attributes",
            "Name:=", "top_left_cut",
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

    subtract(oEditor, 'Ground', 'top_left_cut')


def top_left_1(oEditor, x, y, width, height, name):
    """
    Create a rectangle and merge it with the polygon while performing subtraction operations.

    Inputs:
        oEditor: The editor object used to execute geometric operations.
        x: Float, the X coordinate of the rectangle's bottom-left corner.
        y: Float, the Y coordinate of the rectangle's bottom-left corner.
        width: Float, the width of the rectangle.
        height: Float, the height of the rectangle.
        name: String, the name of the rectangle.

    Outputs:
        No return value.
    """
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", f"{x}mm",
            "YStart:=", f"{y}mm",
            "ZStart:=", "0mm",
            "Width:=", f"{width}mm",
            "Height:=", f"{height}mm",
            "WhichAxis:=", "Z"
        ],
        [
            "NAME:Attributes",
            "Name:=", "Rectangle8",
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

    oEditor.CreatePolyline(
        [
            "NAME:PolylineParameters",
            "IsPolylineCovered:=", True,
            "IsPolylineClosed:=", True,
            [
                "NAME:PolylinePoints",
                [
                    "NAME:PLPoint",
                    "X:=", "0mm",
                    "Y:=", "0.515mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.003mm",
                    "Y:=", "0.515mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.07mm",
                    "Y:=", "0.45mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.0975mm",
                    "Y:=", "0.45mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.0975mm",
                    "Y:=", "0.46mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.0745mm",
                    "Y:=", "0.46mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.007mm",
                    "Y:=", "0.525mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0mm",
                    "Y:=", "0.525mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0mm",
                    "Y:=", "0.515mm",
                    "Z:=", "0mm"
                ],
            ],
            [
                "NAME:PolylineSegments",
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 0,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 1,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 2,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 3,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 4,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 5,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 6,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 7,
                    "NoOfPoints:=", 2
                ],
            ],
            [
                "NAME:PolylineXSection",
                "XSectionType:=", "None",
                "XSectionOrient:=", "Auto",
                "XSectionWidth:=", "0mm",
                "XSectionTopWidth:=", "0mm",
                "XSectionHeight:=", "0mm",
                "XSectionNumSegments:=", "0",
                "XSectionBendType:=", "Corner"
            ]
        ],
        [
            "NAME:Attributes",
            "Name:=", f"{name}",
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

    oEditor.Unite(
        [
            "NAME:Selections",
            "Selections:=", f"{name},Rectangle8"
        ],
        [
            "NAME:UniteParameters",
            "KeepOriginals:=", False
        ])

    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", "0mm",
            "YStart:=", "0.505mm",
            "ZStart:=", "0mm",
            "Width:=", f"{-0.03}mm",
            "Height:=", f"{0.03}mm",
            "WhichAxis:=", "Z"
        ],
        [
            "NAME:Attributes",
            "Name:=", "top_left_cut",
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

    subtract(oEditor, 'Ground', 'top_left_cut')


def top_middle(oEditor, x, y, width, height, name):
    """
    Create a geometric shape for the upper middle region and perform union and subtraction operations.

    Inputs:
        oEditor: The editor object used to execute geometric operations.
        x: Float, the X coordinate for the middle upper region.
        y: Float, the Y coordinate for the middle upper region.
        width: Float, the width of the region.
        height: Float, the height of the region.
        name: String, the name of the region.

    Outputs:
        No return value.
    """
    create_rectangle(oEditor, 0.32, 0.475, 0.01, 0.175, name)
    create_rectangle(oEditor, 0.325 - width / 2, 0.475, width, -height, f"{name}_pad")

    oEditor.Unite(
        [
            "NAME:Selections",
            "Selections:=", f"{name},{name}_pad"
        ],
        [
            "NAME:UniteParameters",
            "KeepOriginals:=", False
        ])

    create_rectangle(oEditor, 0.31, 0.65, 0.03, 0.03, f"{name}_cut")
    subtract(oEditor, 'Ground', f"{name}_cut")


def top_right(oEditor, width, height, name):
    """
    Create a polygon in the upper right region and perform union and subtraction operations.

    Inputs:
        oEditor: The editor object used to execute geometric operations.
        width: Float, the width of the region.
        height: Float, the height of the region.
        name: String, the name of the region.

    Outputs:
        No return value.
    """
    oEditor.CreatePolyline(
        [
            "NAME:PolylineParameters",
            "IsPolylineCovered:=", True,
            "IsPolylineClosed:=", True,
            [
                "NAME:PolylinePoints",
                [
                    "NAME:PLPoint",
                    "X:=", "0.65mm",
                    "Y:=", "0.525mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.643mm",
                    "Y:=", "0.525mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.5755mm",
                    "Y:=", "0.46mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.5525mm",
                    "Y:=", "0.46mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.5525mm",
                    "Y:=", "0.45mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.5795mm",
                    "Y:=", "0.45mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.647mm",
                    "Y:=", "0.515mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.65mm",
                    "Y:=", "0.515mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.65mm",
                    "Y:=", "0.525mm",
                    "Z:=", "0mm"
                ],
            ],
            [
                "NAME:PolylineSegments",
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 0,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 1,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 2,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 3,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 4,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 5,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 6,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 7,
                    "NoOfPoints:=", 2
                ],
            ],
            [
                "NAME:PolylineXSection",
                "XSectionType:=", "None",
                "XSectionOrient:=", "Auto",
                "XSectionWidth:=", "0mm",
                "XSectionTopWidth:=", "0mm",
                "XSectionHeight:=", "0mm",
                "XSectionNumSegments:=", "0",
                "XSectionBendType:=", "Corner"
            ]
        ],
        [
            "NAME:Attributes",
            "Name:=", f"{name}",
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

    create_rectangle(oEditor, 0.5525, 0.445, -width, height, f"{name}_pad")

    oEditor.Unite(
        [
            "NAME:Selections",
            "Selections:=", f"{name},{name}_pad"
        ],
        [
            "NAME:UniteParameters",
            "KeepOriginals:=", False
        ])

    create_rectangle(oEditor, 0.6500, 0.505, 0.03, 0.03, f"{name}_cut")
    subtract(oEditor, 'Ground', f"{name}_cut")


def bottom_left(oEditor, width, height, name):
    """
    Create a polygon in the lower left region and perform union and subtraction operations.

    Inputs:
        oEditor: The editor object used to execute geometric operations.
        width: Float, the width of the region.
        height: Float, the height of the region.
        name: String, the name of the region.

    Outputs:
        No return value.
    """
    oEditor.CreatePolyline(
        [
            "NAME:PolylineParameters",
            "IsPolylineCovered:=", True,
            "IsPolylineClosed:=", True,
            [
                "NAME:PolylinePoints",
                [
                    "NAME:PLPoint",
                    "X:=", "0mm",
                    "Y:=", "0.125mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.007mm",
                    "Y:=", "0.125mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.0745mm",
                    "Y:=", "0.19mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.0975mm",
                    "Y:=", "0.19mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.0975mm",
                    "Y:=", "0.2mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.0705mm",
                    "Y:=", "0.2mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.003mm",
                    "Y:=", "0.135mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0mm",
                    "Y:=", "0.135mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0mm",
                    "Y:=", "0.125mm",
                    "Z:=", "0mm"
                ],
            ],
            [
                "NAME:PolylineSegments",
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 0,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 1,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 2,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 3,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 4,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 5,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 6,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 7,
                    "NoOfPoints:=", 2
                ],
            ],
            [
                "NAME:PolylineXSection",
                "XSectionType:=", "None",
                "XSectionOrient:=", "Auto",
                "XSectionWidth:=", "0mm",
                "XSectionTopWidth:=", "0mm",
                "XSectionHeight:=", "0mm",
                "XSectionNumSegments:=", "0",
                "XSectionBendType:=", "Corner"
            ]
        ],
        [
            "NAME:Attributes",
            "Name:=", f"{name}",
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

    create_rectangle(oEditor, 0.0975, 0.175, width, height, f"{name}_pad")

    oEditor.Unite(
        [
            "NAME:Selections",
            "Selections:=", f"{name},{name}_pad"
        ],
        [
            "NAME:UniteParameters",
            "KeepOriginals:=", False
        ])

    create_rectangle(oEditor, 0, 0.115, -0.03, 0.03, f"{name}_cut")
    subtract(oEditor, 'Ground', f"{name}_cut")


def bottom_middle(oEditor, width, height, name):
    """
    Create a geometric shape for the lower middle region and perform union and subtraction operations.

    Inputs:
        oEditor: The editor object used to execute geometric operations.
        width: Float, the width of the region.
        height: Float, the height of the region.
        name: String, the name of the region.

    Outputs:
        No return value.
    """
    create_rectangle(oEditor, 0.32, 0.175, 0.01, -0.175, name)
    create_rectangle(oEditor, 0.325 - width / 2, 0.175, width, height, f"{name}_pad")

    oEditor.Unite(
        [
            "NAME:Selections",
            "Selections:=", f"{name},{name}_pad"
        ],
        [
            "NAME:UniteParameters",
            "KeepOriginals:=", False
        ])

    create_rectangle(oEditor, 0.31, 0, 0.03, -0.03, f"{name}_cut")
    subtract(oEditor, 'Ground', f"{name}_cut")


def bottom_right(oEditor, width, height, name):
    """
    Create a polygon in the lower right region and perform union and subtraction operations.

    Inputs:
        oEditor: The editor object used to execute geometric operations.
        width: Float, the width of the region.
        height: Float, the height of the region.
        name: String, the name of the region.

    Outputs:
        No return value.
    """
    oEditor.CreatePolyline(
        [
            "NAME:PolylineParameters",
            "IsPolylineCovered:=", True,
            "IsPolylineClosed:=", True,
            [
                "NAME:PolylinePoints",
                [
                    "NAME:PLPoint",
                    "X:=", "0.65mm",
                    "Y:=", "0.125mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.643mm",
                    "Y:=", "0.125mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.5755mm",
                    "Y:=", "0.19mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.5525mm",
                    "Y:=", "0.19mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.5525mm",
                    "Y:=", "0.2mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.5795mm",
                    "Y:=", "0.2mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.647mm",
                    "Y:=", "0.135mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.65mm",
                    "Y:=", "0.135mm",
                    "Z:=", "0mm"
                ],
                [
                    "NAME:PLPoint",
                    "X:=", "0.65mm",
                    "Y:=", "0.125mm",
                    "Z:=", "0mm"
                ],
            ],
            [
                "NAME:PolylineSegments",
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 0,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 1,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 2,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 3,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 4,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 5,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 6,
                    "NoOfPoints:=", 2
                ],
                [
                    "NAME:PLSegment",
                    "SegmentType:=", "Line",
                    "StartIndex:=", 7,
                    "NoOfPoints:=", 2
                ],
            ],
            [
                "NAME:PolylineXSection",
                "XSectionType:=", "None",
                "XSectionOrient:=", "Auto",
                "XSectionWidth:=", "0mm",
                "XSectionTopWidth:=", "0mm",
                "XSectionHeight:=", "0mm",
                "XSectionNumSegments:=", "0",
                "XSectionBendType:=", "Corner"
            ]
        ],
        [
            "NAME:Attributes",
            "Name:=", f"{name}",
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

    create_rectangle(oEditor, 0.5525, 0.175, -width, height, f"{name}_pad")

    oEditor.Unite(
        [
            "NAME:Selections",
            "Selections:=", f"{name},{name}_pad"
        ],
        [
            "NAME:UniteParameters",
            "KeepOriginals:=", False
        ])

    create_rectangle(oEditor, 0.65, 0.115, 0.03, 0.03, f"{name}_cut")
    subtract(oEditor, 'Ground', f"{name}_cut")
