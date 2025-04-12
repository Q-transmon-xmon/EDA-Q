#########################################################################
# File Name: coupling_cavity.py
# Description: This file primarily contains the code for constructing coupling cavities.
#########################################################################

from addict import Dict
from base.library_base import LibraryBase
import toolbox
import copy, gdspy, math
import numpy as np


class CouplingCavity(LibraryBase):
    """
    CouplingCavity class for creating coupling cavity structures.

    Attributes:
        default_options: Dict, containing default coupling cavity parameters.
    """
    default_options = Dict(
        # Framework
        name="q0_cp_q1",
        type="CouplingCavity",
        chip='main',
        qubits=["q0", "q1"],
        width=10,
        outline=[],
        gap=5,
        start_pos=(0, 0),
        end_pos=(2000, 0),
        # Geometric parameters
        length=3000,
        start_straight=100,
        end_straight=100,
        r=100,
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the CouplingCavity class.

        Input:
            options: Dict, user-defined coupling cavity parameters.

        Output:
            None.
        """
        super().__init__(options)
        return

    def calc_general_ops(self):
        """
        Calculates general operations.

        Output:
            None.
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shape of the coupling cavity and adds it to the GDS cell.

        Output:
            None.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell_subtract = self.lib.new_cell(self.name + "_subtract")

        options = self.extract_options()

        # Calculate the distance and angle between start_pos and end_pos
        dx = self.end_pos[0] - self.start_pos[0]
        dy = self.end_pos[1] - self.start_pos[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        angle = math.atan2(dy, dx) - math.pi / 2  # Add 90 degrees to make it perpendicular
        if options.length <= distance:
            raise ValueError(
                "Parameter error: The length of the coupling line is less than or equal to the distance between qubits.")
        # Create the gdspy Path with a width of width
        readout_l = gdspy.Path(self.width, (self.start_pos[0], self.start_pos[1]), number_of_paths=1)
        readout_l.segment(options.start_straight, '+y')

        # Calculate the number of segments and their lengths
        num = round((distance - options.start_straight - options.end_straight) // (options.r * 2))
        if num <= 0:
            raise ValueError(
                "Parameter error: The distance between qubits is too short or the start and end segments are too long.")

        segment = round((self.length - options.start_straight - options.end_straight - (
                    num + 1) * math.pi * options.r - (num - 1) * 2 * options.r) / (num))

        # Add segments and turns
        readout_l.turn(options.r, 'l')

        for i in range(num):
            if i != 0:
                readout_l.segment(options.r, '-x' if i % 2 == 0 else '+x')
            readout_l.segment(segment / 2, '-x' if i % 2 == 0 else '+x')
            readout_l.turn(options.r, 'll' if i % 2 == 1 else 'rr')
            readout_l.segment(segment / 2, '-x' if i % 2 == 1 else '+x')
            if i != num - 1:
                readout_l.segment(options.r, '-x' if i % 2 == 1 else '+x')

        readout_l.turn(options.r, 'l' if num % 2 == 1 else 'r')
        readout_l.segment(options.end_straight, '+y')

        # Rotate the entire shape based on the calculated angle
        readout_l.rotate(angle, self.start_pos)

        self.cell_subtract.add(readout_l)

        self.cell_extract = self.lib.new_cell(self.name + "_extract")

        # Calculate the distance and angle between start_pos and end_pos
        dx = self.end_pos[0] - self.start_pos[0]
        dy = self.end_pos[1] - self.start_pos[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        angle = math.atan2(dy, dx) - math.pi / 2  # Add 90 degrees to make it perpendicular
        if options.length <= distance:
            raise ValueError(
                "Parameter error: The length of the coupling line is less than or equal to the distance between qubits.")
        # Create the gdspy Path with a width of width
        readout_l = gdspy.Path(self.width + self.gap * 2, (self.start_pos[0], self.start_pos[1]), number_of_paths=1)
        readout_l.segment(options.start_straight, '+y')

        # Calculate the number of segments and their lengths
        num = round((distance - options.start_straight - options.end_straight) // (options.r * 2))
        if num <= 0:
            raise ValueError(
                "Parameter error: The distance between qubits is too short or the start and end segments are too long.")

        segment = round((self.length - options.start_straight - options.end_straight - (
                    num + 1) * math.pi * options.r - (num - 1) * 2 * options.r) / (num))

        # Add segments and turns
        readout_l.turn(options.r, 'l')

        for i in range(num):
            if i != 0:
                readout_l.segment(options.r, '-x' if i % 2 == 0 else '+x')
            readout_l.segment(segment / 2, '-x' if i % 2 == 0 else '+x')
            readout_l.turn(options.r, 'll' if i % 2 == 1 else 'rr')
            readout_l.segment(segment / 2, '-x' if i % 2 == 1 else '+x')
            if i != num - 1:
                readout_l.segment(options.r, '-x' if i % 2 == 1 else '+x')

        readout_l.turn(options.r, 'l' if num % 2 == 1 else 'r')
        readout_l.segment(options.end_straight, '+y')

        # Rotate the entire shape based on the calculated angle
        readout_l.rotate(angle, self.start_pos)

        self.cell_extract.add(readout_l)

        # Temporary use
        sub_poly = gdspy.boolean(self.cell_extract, self.cell_subtract, "not")
        self.cell = self.lib.new_cell(self.name + "_cell")
        self.cell.add(sub_poly)

        return