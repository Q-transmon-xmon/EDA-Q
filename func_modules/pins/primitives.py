############################################################################################
# Modify the parameters of pins
############################################################################################

from addict import Dict
import copy, toolbox
from library import pins as pins_lib

def soak_pins(pins_ops):
    """
    Use the pin class to complete the parameters of the pin.

    Input:
        pins: the original parameters of pins

    Output:
        pins: the parameters of pins after supplementation
    """
    
    # Interface
    pins_ops = copy.deepcopy(pins_ops)

    # Modify the parameters of each pin in sequence
    for pin_name, pin_ops in pins_ops.items():
        pin_inst = getattr(pins_lib, pin_ops.type)(options=pin_ops)
        pins_ops[pin_name] = pin_inst.options
    
    return copy.deepcopy(pins_ops)

def set_chips(pins_ops, chip_name: str = None):
    """
    Set the chip information in pins
    
    Input:
        pins_ops: the parameters of pins
        chip_name: the name of the chip to be set

    Output:
        pins: the parameters of pins after setting the chip information
    """
    # Interface
    pins_ops = Dict(pins_ops)
    
    # Modify the chip information for each pin
    for pin_name, pin_ops in pins_ops.items():
        pins_ops[pin_name].chip = chip_name
        
    return copy.deepcopy(pins_ops)