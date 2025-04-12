#########################################################################
# File Name: __init__.py
# Description: Provides an interface for equivalent circuit operations.
#              Includes functionality to modify qubit parameters and readout parameters.
#########################################################################

from addict import Dict
import copy
from base.branch_base import BranchBase
from equ_circ.change_equ_circ_ops.change_qubit import change_qubit
from equ_circ.change_equ_circ_ops.change_readout import change_readout

__all__ = ["change_equ_circ_ops"]


def change_equ_circ_ops(**change_ops):
    """
    Modify equivalent circuit operations based on the provided parameters.

    Args:
        **change_ops: Arbitrary keyword arguments containing details of the modification operations.

    Returns:
        A deep copy of the modified branch processing result.
    """
    cec = ChangeEquCirc(**change_ops)
    return copy.deepcopy(cec.branch_process())


class ChangeEquCirc(BranchBase):
    def equ_circ_ops__op_name__op_value__qubit_name(self, change_ops):
        """
        Modify qubit parameters.

        Args:
            change_ops: An object containing the parameters for the modification operations.

        Returns:
            A deep copy of the modified equivalent circuit operations.
        """
        change_ops = copy.deepcopy(change_ops)
        equ_circ_ops = copy.deepcopy(change_ops.equ_circ_ops)
        qubit_name = change_ops.qubit_name
        op_name = change_ops.op_name
        op_value = change_ops.op_value

        equ_circ_ops = change_qubit.change_qubit(equ_circ_ops=equ_circ_ops,
                                                 qubit_name=qubit_name,
                                                 op_name=op_name,
                                                 op_value=op_value)

        return copy.deepcopy(equ_circ_ops)

    def equ_circ_ops__op_name__op_value__rdl_name(self, change_ops):
        """
        Modify readout parameters.

        Args:
            change_ops: An object containing the parameters for the modification operations.

        Returns:
            A deep copy of the modified equivalent circuit operations.
        """
        change_ops = copy.deepcopy(change_ops)
        equ_circ_ops = copy.deepcopy(change_ops.equ_circ_ops)
        rdl_name = change_ops.rdl_name
        op_name = change_ops.op_name
        op_value = change_ops.op_value

        equ_circ_ops = change_readout.change_readout(equ_circ_ops=equ_circ_ops,
                                                     rdl_name=rdl_name,
                                                     op_name=op_name,
                                                     op_value=op_value)

        return copy.deepcopy(equ_circ_ops)