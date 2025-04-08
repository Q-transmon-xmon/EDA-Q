#########################################################################
# File Name: change_readout.py
# Description: Provides functionality to modify readout parameters.
#              Allows users to specify the readout name, operation name, and operation value to update readout parameters.
#########################################################################

from addict import Dict
import copy


def change_readout(equ_circ_ops, rdl_name, op_name, op_value):
    """
    Modify the parameters of the readout section in the equivalent circuit.

    Args:
        equ_circ_ops: An object containing the equivalent circuit operation parameters.
        rdl_name: A string specifying the name of the readout to be modified.
        op_name: A string specifying the name of the operation to be modified.
        op_value: The value to be set for the specified operation.

    Returns:
        A deep copy of the modified equivalent circuit operation parameters.
    """
    equ_circ_ops = copy.deepcopy(equ_circ_ops)

    return copy.deepcopy(equ_circ_ops)