import os
import copy
import toolbox

from func_modules.air_bridges import air_bridge_lzh
from func_modules.air_bridges import air_bridge_yxh
from func_modules.air_bridges import gene_air_bridges_ops

import toolbox
import copy

def generate_air_bridges(**gene_ops):
    # deprecated
    return copy.deepcopy(gene_air_bridges_ops.gene_air_bridges_ops(**gene_ops))

def auto_generate_air_bridges_ops(gds_ops, 
                                  line_type, 
                                  line_name, 
                                  spacing=120, 
                                  chip_name="chip3", 
                                  width=10, 
                                  air_bridge_type="AirBridge"):
    return air_bridge_lzh.auto_generate_air_bridges_ops_lzh(gds_ops=gds_ops, 
                                                            line_type=line_type, 
                                                            line_name=line_name, 
                                                            spacing=spacing, 
                                                            chip_name=chip_name, 
                                                            width=width, 
                                                            air_bridge_type=air_bridge_type)