#########################################################################
# File Name: __init__.py
# Description: Manages the initialization of qubit modules.
#              Includes functionality for dynamically importing qubit-related classes 
#              and maintaining module information.
#########################################################################

from library.qubits.circlemon import Circlemon
from library.qubits.custom_qubit import CustomQubit
from library.qubits.transmon_interdigitated import TransmonInterdigitated
from library.qubits.transmon_rotate import TransmonRotate
from library.qubits.transmon_teeth import TransmonTeeth
from library.qubits.transmon import Transmon
from library.qubits.xmon import Xmon
from library.qubits.xmon_rotate import XmonRotate
from library.qubits.smon import Smon
from library.qubits.transmon_benzheng import TransmonBenzheng
from library.qubits.xmon_nju import XmonNju

module_name_list = ["circlemon", 
                    "custom_qubit",  
                    "transmon_interdigitated", 
                    "transmon_rotate", 
                    "transmon_teeth", 
                    "transmon", 
                    "xmon",
                    "xmon_rotate",
                    "smon",
                    "transmon_benzheng",
                    "xmon_nju"]