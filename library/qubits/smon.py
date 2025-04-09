#########################################################################
# File Name: smon.py
# Description: Defines the Smon class, which simulates the geometric structure of a superconducting qubit 
#              and draws elements in the GDS design database.
#              Includes qubit parameter settings, pin calculation, and geometric shape drawing functionality.
#########################################################################

import gdspy
import numpy as np
from addict import Dict
from base.library_base import LibraryBase

class Smon(LibraryBase):
    # Default options
    default_options = Dict(
        # Parameters required for all qubits
        name="q1",  # Qubit name
        type="Transmon",  # Qubit type
        gds_pos=[0, 0],  # GDS position
        topo_pos=[0, 0],  # Topological position
        chip="main",  # Chip name
        readout_pins=[],  # Readout pins
        control_pins=[],  # Control pins
        coupling_pins=[],  # Coupling pins
        outline=[],  # Outline
        # Optional parameters
        # (Parameters for drawing)
        width=455,  # Qubit width
        height=90,  # Qubit height
        gap=30,  # Gap
        connect_pad_options=[1, 1, 1, 1, 1, 1],  # Default selection of all pads, order: a, b, c, d, e, f
        la=93,  # Pad a length
        lb=93,  # Pad b length
        lc=125,  # Pad c length
        ld=93,  # Pad d length
        le=93,  # Pad e length
        lf=93,  # Pad f length
    )

    def __init__(self, options):
        """
        Initialize the Smon class.
        
        Input:
            options: Dictionary containing the component's parameter options.
        """
        super().__init__(options)
        return
    
    def calc_general_ops(self):
        """
        Generate the positions of coupling_pins, readout_pins, and control_pins.
        """
        x = self.gds_pos[0]
        y = self.gds_pos[1]
        a, b, c, d, e, f = self.connect_pad_options
        width = self.width
        height = self.height
        gap = self.gap
        la = self.la
        lb = self.lb
        lc = self.lc
        ld = self.ld
        le = self.le
        lf = self.lf

        # Calculate pin positions
        self.readout_pins.append([x + 650, y + 520 + height - 90 + (gap / 2 - 15)])
        self.control_pins.append([x, y + 130 - height + 90 + (15 - gap / 2)])
        self.control_pins.append([x, y + 520 + height - 90 + (gap / 2 - 15)])
        self.control_pins.append([x + 650, y + (130 - height + 90 + (15 - gap / 2)) * d + (1 - d) * 130])
        self.control_pins.append([x + 325, y + 650])
        self.control_pins.append([x + 325, y])
        
        self.coupling_pins.append([x + 325, y + 650])
        self.coupling_pins.append([x + 325, y])
        self.coupling_pins.append([x, y + 130 - height + 90 + (15 - gap / 2)])
        self.coupling_pins.append([x + 650, y + (130 - height + 90 + (15 - gap / 2)) * d + (1 - d) * 130])

        # Set outline
        self.outline = [[x, y],
                        [x, y + 650],
                        [x + 650, y + 650],
                        [x + 650, y],
                        [x, y]]

        return

    def draw_gds(self):
        """
        Draw the geometric shape of the qubit and add it to the GDS cell.
        """
       # gdspy variables
        gdspy.library.use_current_library = False
        self.lib = gdspy.GdsLibrary()
        self.cell = self.lib.new_cell(self.name)
        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")

        """
        Add your code here
        self.__cell_subtract draws the metal part
        The final red area remaining after subtraction is the substrate
        """

        x = self.gds_pos[0]
        y = self.gds_pos[1]
        a = self.connect_pad_options[0]
        b = self.connect_pad_options[1]
        c = self.connect_pad_options[2]
        d = self.connect_pad_options[3]
        e = self.connect_pad_options[4]
        f = self.connect_pad_options[5]
        width = self.width
        height = self.height
        gap = self.gap
        la = self.la
        lb = self.lb
        lc = self.lc
        ld = self.ld
        le = self.le
        lf = self.lf

        qubit_point = gdspy.Curve(x, y).l(0, (125 - height + 90 + (15 - gap / 2)) * a,
                                          7 * a, (125 - height + 90 + (15 - gap / 2)) * a, (74.5 - width / 2 + 227.5) * a, (190 - height + 90 + (15 - gap / 2)) * a, (112.5) * a, (190 - height + 90 + (15 - gap / 2)) * a, (112.5) * a, (175 - height + 90 + (15 - gap / 2)) * a, (97.5 + la - width / 2 + 227.5 + 15) * a, (175 - height + 90 + (15 - gap / 2)) * a, (97.5 + la - width / 2 + 227.5 + 15) * a, (205 - height + 90 + (15 - gap / 2)) * a, (112.5) * a, (205 - height + 90 + (15 - gap / 2)) * a, (112.5) * a, (200 - height + 90 + (15 - gap / 2)) * a, (70.5 - width / 2 + 227.5) * a, (200 - height + 90 + (15 - gap / 2)) * a, 3 * a, (135 - height + 90 + (15 - gap / 2)) * a,
                                          0, (135 - height + 90 + (15 - gap / 2)) * a, 0, (515 + height - 90 + (gap / 2 - 15)) * b,
                                          3 * b, (515 + height - 90 + (gap / 2 - 15)) * b, (70.5 - width / 2 + 227.5) * b, (450 + height - 90 + (gap / 2 - 15)) * b, (112.5) * b, (450 + height - 90 + (gap / 2 - 15)) * b, (112.5) * b, (445 + height - 90 + (gap / 2 - 15)) * b, (97.5 + lb - width / 2 + 227.5 + 15) * b, (445 + height - 90 + (gap / 2 - 15)) * b, (97.5 + lb - width / 2 + 227.5 + 15) * b, (475 + height - 90 + (gap / 2 - 15)) * b, (112.5) * b, (475 + height - 90 + (gap / 2 - 15)) * b, (112.5) * b, (460 + height - 90 + (gap / 2 - 15)) * b, (74.5 - width / 2 + 227.5) * b, (460 + height - 90 + (gap / 2 - 15)) * b, 7 * b, (525 + height - 90 + (gap / 2 - 15)) * b,
                                          0, (525 + height - 90 + (gap / 2 - 15)) * b, 0, 650,
                                          320, 650, 320 * e, (475 + height - 90 + (gap / 2 - 15)) * e + (1 - e) * 650, (325 - le / 2) * e + (1 - e) * 330, (475 + height - 90 + (gap / 2 - 15)) * e + (1 - e) * 650, (325 - le / 2) * e + (1 - e) * 330, (445 + height - 90 + (gap / 2 - 15)) * e + (1 - e) * 650, (325 + le / 2) * e + (1 - e) * 330, (445 + height - 90 + (gap / 2 - 15)) * e + (1 - e) * 650, (325 + le / 2) * e + (1 - e) * 330, (475 + height - 90 + (gap / 2 - 15)) * e + (1 - e) * 650, 330 * e + (1 - e) * 330, (475 + height - 90 + (gap / 2 - 15)) * e + (1 - e) * 650,
                                          330, 650,
                                          650, 650, 650, (525 + height - 90 + (gap / 2 - 15)) * c,
                                          (643 - 650) * c + 650, (525 + height - 90 - 525 + (gap / 2 - 15)) * c + 525, (575.5 + width / 2 - 227.5 - 650) * c + 650, (460 + height - 90 - 525 + (gap / 2 - 15)) * c + 525, (537.5) * c, (460 + height - 90 - 525 + (gap / 2 - 15)) * c + 525, (537.5) * c, (475 + height - 90 - 525 + (gap / 2 - 15)) * c + 525, (552.5 - lc + width / 2 - 227.5 - 650 - 15) * c + 650, (475 + height - 90 - 525 + (gap / 2 - 15)) * c + 525, (552.5 - lc + width / 2 - 227.5 - 650 - 15) * c + 650, (445 + height - 90 - 525 + (gap / 2 - 15)) * c + 525, (537.5) * c, (445 + height - 90 - 525 + (gap / 2 - 15)) * c + 525, (537.5) * c, (450 + height - 90 - 525 + (gap / 2 - 15)) * c + 525, (579.5 + width / 2 - 227.5 - 650) * c + 650, (450 + height - 90 - 525 + (gap / 2 - 15)) * c + 525,
                                          (647 - 650) * c + 650, (515 + height - 90 - 525 + (gap / 2 - 15)) * c + 525, 650, (515 + height - 90 + (gap / 2 - 15)) * c,
                                          650, (135 - height + 90 + (15 - gap / 2)) * d + (1 - d) * 135,
                                          (647 - 650) * d + 650, (135 - height + 90 + (15 - gap / 2)) * d + (1 - d) * 135,
                                          (579.5 + width / 2 - 227.5 - 650) * d + 650, (200 - height + 90 - 135 + (15 - gap / 2)) * d + 135, (537.5) * d, (200 - height + 90 - 135 + (15 - gap / 2)) * d + 135,
                                          (537.5) * d, (205 - height + 90 - 135 + (15 - gap / 2)) * d + 135,
                                          (552.5 - ld + width / 2 - 227.5 - 650 - 15) * d + 650, (205 - height + 90 - 135 + (15 - gap / 2)) * d + 135, (552.5 - ld + width / 2 - 227.5 - 650 - 15) * d + 650, (175 - height + 90 - 135 + (15 - gap / 2)) * d + 135, (537.5) * d, (175 - height + 90 - 135 + (15 - gap / 2)) * d + 135,
                                          (537.5) * d, (190 - height + 90 - 135 + (15 - gap / 2)) * d + 135, (575.5 + width / 2 - 227.5 - 650) * d + 650, (190 - height + 90 - 135 + (15 - gap / 2)) * d + 135,
                                          (643 - 650) * d + 650, (125 - height + 90 + (15 - gap / 2)) * d + (1 - d) * 135,
                                          650, (125 - height + 90 + (15 - gap / 2)) * d + (1 - d) * 125, 650, 0,
                                          330 * f, 0 * f, 330 * f, (175 - height + 90 + (15 - gap / 2)) * f, (325 + lf / 2) * f, (175 - height + 90 + (15 - gap / 2)) * f, (325 + lf / 2) * f, (205 - height + 90 + (15 - gap / 2)) * f, (325 - lf / 2) * f, (205 - height + 90 + (15 - gap / 2)) * f, (325 - lf / 2) * f, (175 - height + 90 + (15 - gap / 2)) * f, 320 * f, (175 - height + 90 + (15 - gap / 2)) * f, 320 * f, 0 * f
                                          , 0, 0)
        qubit = gdspy.Polygon(qubit_point.get_points())

        rect = gdspy.Rectangle((x + 112.5, y + 220), (x + 112.5 + 425, y + 220 + 90 + 15))
        circle0 = gdspy.Round((x + 115 + 30 - 90, y + 220 + 105), 60, tolerance=0.01)
        qubit1 = gdspy.boolean(rect, circle0, "not")
        circle1 = gdspy.Round((x + 115 + 30, y + 220 + 105), 30, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1, circle1, "or")
        circle2 = gdspy.Round((x + 115 + 30 + 90, y + 220 + 105), 60, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1, circle2, "not")
        circle3 = gdspy.Round((x + 115 + 30 + 90 + 90, y + 220 + 105), 30, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1, circle3, "or")
        circle4 = gdspy.Round((x + 115 + 30 + 90 + 90 + 90, y + 220 + 105), 60, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1, circle4, "not")
        circle5 = gdspy.Round((x + 115 + 30 + 90 + 90 + 90 + 90, y + 220 + 105), 30, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1, circle5, "or")
        circle6 = gdspy.Round((x + 115 + 30 + 90 + 90 + 90 + 90 + 90, y + 220 + 105), 60, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1, circle6, "not")
        qubit2 = gdspy.boolean(qubit, qubit1, "not")
        
        rect = gdspy.Rectangle((x + 112.5, y + 220 + 105), (x + 112.5 + 425, y + 220 + 90 + 15 + 105))
        circle0 = gdspy.Round((x + 325, y + 220 + 105), 60, tolerance=0.01)
        qubit1 = gdspy.boolean(rect, circle0, "not")
        circle1 = gdspy.Round((x + 325 - 90, y + 220 + 105), 30, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1, circle1, "or")
        circle2 = gdspy.Round((x + 325 + 90, y + 220 + 105), 30, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1, circle2, "or")
        circle3 = gdspy.Round((x + 325 - 90 - 90, y + 220 + 105), 60, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1, circle3, "not")
        circle4 = gdspy.Round((x + 325 + 90 + 90, y + 220 + 105), 60, tolerance=0.01)
        qubit1 = gdspy.boolean(qubit1, circle4, "not")
        qubit2 = gdspy.boolean(qubit2, qubit1, "not")
        # sub_poly = gdspy.boolean(self.__cell_extract, self.__cell_subtract, "not")
        self.cell.add(qubit2)
        return