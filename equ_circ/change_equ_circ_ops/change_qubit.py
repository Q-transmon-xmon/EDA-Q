#########################################################################
# File Name: change_qubit.py
# Description: Provides functionality to modify qubit parameters.
#              Allows users to specify the qubit name, operation name, and operation value to update qubit parameters.
#########################################################################

from addict import Dict
import copy


def change_qubit(equ_circ_ops, qubit_name, op_name, op_value):
    """
    Modify the parameters of a qubit in the equivalent circuit.

    Args:
        equ_circ_ops: An object containing the equivalent circuit operation parameters.
        qubit_name: A string specifying the name of the qubit to be modified.
        op_name: A string specifying the name of the operation to be modified.
        op_value: The value to be set for the specified operation.

    Returns:
        A deep copy of the modified equivalent circuit operation parameters.
    """
    equ_circ_ops = copy.deepcopy(equ_circ_ops)

    return copy.deepcopy(equ_circ_ops)