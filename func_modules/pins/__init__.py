import os
import copy
import toolbox

from func_modules.pins import gene_pins_ops
from func_modules.pins import primitives

############################################################################################
# 修改pins的参数
############################################################################################

from addict import Dict
import copy, toolbox
from func_modules.pins import primitives
from cmpnt_frame.pin import Pin as Pin_frame

def soak_pins(pins_ops):
    """使用pin的类将pin的参数补充完整

    输入：
        pins: 原来pins的参数

    输出：
        pins: 补充之后pins的参数
    """
    pins_ops = primitives.soak_pins(pins_ops=pins_ops)
    return copy.deepcopy(pins_ops)

def set_chips(pins_ops, chip_name: str = None):
    """设置pins中的芯片信息
    
    输入：
        pins_ops: pins的参数
        chip_name: 所设置的chip的名字

    输出：
        pins: 设置芯片信息后的pins的参数
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