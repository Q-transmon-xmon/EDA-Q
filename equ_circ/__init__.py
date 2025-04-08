###############################################################################################
# File Name: __init__.py
# Description: This file serves as the initialization file for the module and provides
#              function interfaces related to plasma circuits (equ_circ).
############################################################################################

from equ_circ import primitives
from equ_circ import equ_circ_old
from addict import Dict
import copy


def generate_equ_circ(topo_ops, txt_path, qcsv_path, rcsv_path):
    """
    Generate plasma circuit files.

    Input:
        topo_ops: Topology operation parameters.
        txt_path: Text file path.
        qcsv_path: Quantum bit parameter CSV file path.
        rcsv_path: Coupling parameter CSV file path.

    Output:
        None.
    """
    primitives.generate_equ_circ_files(topo_ops, txt_path, qcsv_path, rcsv_path)
    return


def display_equ_circ(txt_path):
    """
    Display plasma circuit text information.

    Input:
        txt_path: Text file path.

    Output:
        None.
    """
    primitives.display_equ_circ(txt_path=txt_path)
    return


def save_equ_circ_image(txt_path, image_path):
    """
    Save plasma circuit image.

    Input:
        txt_path: Text file path.
        image_path: Image save path.

    Output:
        None.
    """
    primitives.save_equ_circ_image(txt_path=txt_path, image_path=image_path)
    return


def change_qubit_options(txt_path, qcsv_path, qubit_name, value):
    """
    Modify quantum bit options.

    Input:
        txt_path: Text file path.
        qcsv_path: Quantum bit parameter CSV file path.
        qubit_name: Quantum bit name.
        value: New parameter value.

    Output:
        None.
    """
    primitives.change_qubit_options(txt_path=txt_path,
                                    qcsv_path=qcsv_path,
                                    qubit_name=qubit_name,
                                    value=value)
    return


def change_coupling_options(txt_path, rcsv_path, coupling_line_name, op_name, op_value):
    """
    Modify coupling options.

    Input:
        txt_path: Text file path.
        rcsv_path: Coupling parameter CSV file path.
        coupling_line_name: Coupling line name.
        op_name: Operation name.
        op_value: New operation value.

    Output:
        None.
    """
    primitives.change_coupling_options(txt_path=txt_path,
                                       rcsv_path=rcsv_path,
                                       coupling_line_name=coupling_line_name,
                                       op_name=op_name,
                                       op_value=op_value)
    return


def find_qubit_options(qcsv_path, qubit_name):
    """
    Find quantum bit options.

    Input:
        qcsv_path: Quantum bit parameter CSV file path.
        qubit_name: Quantum bit name.

    Output:
        Quantum bit options.
    """
    ans = primitives.find_qubit_options(qcsv_path=qcsv_path, qubit_name=qubit_name)
    return ans


def find_coupling_options(rcsv_path, coupling_line_name, op_name):
    """
    Find coupling options.

    Input:
        rcsv_path: Coupling parameter CSV file path.
        coupling_line_name: Coupling line name.
        op_name: Operation name.

    Output:
        Coupling options.
    """
    ans = primitives.find_coupling_options(rcsv_path=rcsv_path, coupling_line_name=coupling_line_name, op_name=op_name)
    return ans