#########################################################################
# File Name: _constants.py
# Description: Defines some constants used in the program.
#              Includes maximum and minimum values for floating-point numbers, angle constants, and physical constants.
#########################################################################

import sys

# Maximum and minimum values for floating-point numbers
max_float = sys.float_info.max
min_float = sys.float_info.min

# Angle constants (negative values indicate clockwise rotation)
EAST = 0.  # Consistent with the angle generated in core.py
NORTH = 90.
WEST = 180.
SOUTH = 270.

# Physical constants
e = 1.602176620800000092639258660807e-19  # Elementary charge
pi = 3.141592653589793115997963468544  # Pi
h = 6.626070039999999902526276366114e-34  # Planck's constant
hbar = h / (2. * pi)  # Reduced Planck's constant