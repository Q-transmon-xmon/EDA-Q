import os
import copy
import toolbox

from func_modules.pins import gene_pins_ops
from func_modules.pins import primitives

############################################################################################
# Modify pin parameters
############################################################################################

from addict import Dict
import copy, toolbox
from func_modules.pins import primitives
from cmpnt_frame.pin import Pin as Pin_frame

def soak_pins(pins_ops):
    """Use the Pin class to supplement pin parameters completely.

    input:
        pins_ops: Original pin parameters

    output:
        pins_ops: Pin parameters after supplementation
    """
    pins_ops = primitives.soak_pins(pins_ops=pins_ops)
    return copy.deepcopy(pins_ops)

def set_chips(pins_ops, chip_name: str = None):
    """Set up chip information for pins.

    input:
        pins_ops: Pin parameters
        chip_name: The name of the chip to set up

    output:
        pins_ops: Pin parameters after setting up chip information
    """
    pins_ops = primitives.set_chips(pins_ops=pins_ops, chip_name=chip_name)
    return copy.deepcopy(pins_ops)

def set_types(pins_ops, pins_type):
    """Set the type for all pins.

    input:
        pins_ops: Pin parameters
        pins_type: The type to set for the pins

    output:
        pins_ops: Pin parameters after setting the type
    """
    for pin_name, pin_ops in pins_ops.items():
        pins_ops[pin_name].type = pins_type
    return copy.deepcopy(pins_ops)

def dehy_pins(pins_ops):
    """Dehydrate pin parameters using the Pin class.

    input:
        pins_ops: Pin parameters

    output:
        pins_ops: Dehydrated pin parameters
    """
    pins_ops = copy.deepcopy(pins_ops)
    for pin_name, pin_ops in pins_ops.items():
        pin_ops.type = "Pin"
        pins_ops[pin_name] = copy.deepcopy(Pin_frame(options=pin_ops).options)
    return copy.deepcopy(pins_ops)

def generate_pins(**gene_ops):
    """Generate pin parameters based on provided options.

    input:
        gene_ops: Options for generating pins

    output:
        pins_ops: Generated pin parameters
    """
    return copy.deepcopy(gene_pins_ops.gene_pins_ops(**gene_ops))