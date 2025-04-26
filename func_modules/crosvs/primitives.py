############################################################################################
# Parameter processing related to crossing lines
############################################################################################

from addict import Dict
import toolbox
import copy
from components import cross_overs

def generate_ins_sheets(cpls_ops, tmls_ops):
    """Generate insulation pads based on coupling lines and transmission lines

    input：
        cpls_ops: Coupling line parameters
        tmls_ops: Transmission line parameters

    output：
        ins_sheets: Insulation pad parameters
    
    """

    # interface
    cpls_ops = Dict(cpls_ops)
    tmls_ops = Dict(tmls_ops)

    # Generate insulation pad
    ins_sheets = Dict()
    idx = 0

    for cpl_name, cpl_ops in cpls_ops.items():
        for tml_name, tml_ops in tmls_ops.items():
            path1 = [cpl_ops.start_pos, cpl_ops.end_pos]
            path2 = tml_ops.pos
            itscts = toolbox.calc_itscts(path1, path2)
            for itsct in itscts:
                ins_sheets["ins_sheet{}".format(idx)].name = "ins_sheet{}".format(idx)
                ins_sheets["ins_sheet{}".format(idx)].pos = itsct
                ins_sheets["ins_sheet{}".format(idx)].type = "InsulatingSheet"
                idx += 1

    return copy.deepcopy(ins_sheets)

def soak_cross_overs(cross_overs_ops):
    """Complete cross line parameters based on class

    input：
        cross_overs_ops: Cross line parameters

    output：
        cross_overs_ops: The completed Cross line parameters
    """

    # interface
    cross_overs_ops = copy.deepcopy(cross_overs_ops)

    # Obtain examples
    inst = cross_overs.CrossOvers(cross_overs_ops)

    # Modify parameters sequentially
    for k, v in cross_overs_ops.items():
        cross_overs_ops[k] = inst.options[k]

    return copy.deepcopy(cross_overs_ops)

def set_chips(cross_overs_ops, chip_name):
    """Set cross line chip information

    input：
        cross_overs_ops: Coupling line parameters
        chip_name: The chip name to be set

    output： 
        cross_overs_ops: Set the Coupling line parameters after the chip name
    """
    
    # interface
    cross_overs_ops = copy.deepcopy(cross_overs_ops)

    # Set chip information sequentially
    for k, v in cross_overs_ops.items():
        cross_overs_ops[k].chip = chip_name
        
    return copy.deepcopy(cross_overs_ops)

def generate_crosvs_ops_from_cpls_ops_and_tmls_ops(cpls_ops, tmls_ops, crosvs_type, chip_name):
    """Generate insulation pads based on coupling lines and transmission lines

    input：
        cpls_ops: Coupling line parameters
        tmls_ops: Transmission line parameters

    output：
        ins_sheets: Insulation pad parameters
    
    """

    # interface
    cpls_ops = Dict(cpls_ops)
    tmls_ops = Dict(tmls_ops)
    crosvs_type = crosvs_type
    chip_name = chip_name

    # Generate insulation pad
    ins_sheets = Dict()
    idx = 0

    for cpl_name, cpl_ops in cpls_ops.items():
        for tml_name, tml_ops in tmls_ops.items():
            if cpl_ops.type != "CouplingLineStraight":
                raise ValueError("The automatic generation of crossover currently only supports the coupling type of CouplingLineStraight, and the type of {} is {}!".format(cpl_name, cpl_ops.type))
            
            path1 = [cpl_ops.start_pos, cpl_ops.end_pos]
            path2 = tml_ops.pos
            itscts = toolbox.calc_itscts(path1, path2)
            for itsct in itscts:
                ins_sheets["ins_sheet{}".format(idx)].name = "ins_sheet{}".format(idx)
                ins_sheets["ins_sheet{}".format(idx)].chip = chip_name
                ins_sheets["ins_sheet{}".format(idx)].pos = itsct
                ins_sheets["ins_sheet{}".format(idx)].type = crosvs_type
                idx += 1

    return copy.deepcopy(ins_sheets)