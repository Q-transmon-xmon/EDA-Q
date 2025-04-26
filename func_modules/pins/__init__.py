import os
import copy
import toolbox

from func_modules.pins import gene_pins_ops
from func_modules.pins import primitives

############################################################################################
# modifypinsParameters for
############################################################################################

from addict import Dict
import copy, toolbox
from func_modules.pins import primitives
from cmpnt_frame.pin import Pin as Pin_frame

def soak_pins(pins_ops):
    """usepinThe class willpinComplete parameter supplementation

    input：
        pins: originallypinsParameters for

    output：
        pins: After supplementationpinsParameters for
    """
    pins_ops = primitives.soak_pins(pins_ops=pins_ops)
    return copy.deepcopy(pins_ops)

def set_chips(pins_ops, chip_name: str = None):
    """set uppinsChip information in
    
    input：
        pins_ops: pinsParameters for
        chip_name: 所set up的chipthe name of

    output：
        pins: set up芯片信息后的pinsParameters for
    """
    pins_ops = primitives.set_chips(pins_ops=pins_ops, chip_name=chip_name)
    return copy.deepcopy(pins_ops)

def set_types(pins_ops, pins_type):
    for pin_name, pin_ops in pins_ops.items():
        pins_ops[pin_name].type = pins_type
    return copy.deepcopy(pins_ops)

def dehy_pins(pins_ops):
    pins_ops = copy.deepcopy(pins_ops)
    for pin_name, pin_ops in pins_ops.items():
        pin_ops.type = "Pin"
        pins_ops[pin_name] = copy.deepcopy(Pin_frame(options=pin_ops).options)
    return copy.deepcopy(pins_ops)

def generate_pins(**gene_ops):
    return copy.deepcopy(gene_pins_ops.gene_pins_ops(**gene_ops))