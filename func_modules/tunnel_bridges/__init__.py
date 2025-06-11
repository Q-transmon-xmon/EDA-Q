import os
import copy
import toolbox

from func_modules.tunnel_bridges import tunnel_bridges_czy
from func_modules.air_bridges import optimize_air_bridges_layout_code

import toolbox
import copy

def auto_generate_tunnel_bridges_ops(gds_ops, 
                                  line_type, 
                                  line_name, 
                                  spacing=120, 
                                  chip_name="chip3", 
                                  width=10, 
                                  tunnel_bridge_type="CoverBridge"):
    return tunnel_bridges_czy.auto_generate_tunnel_bridges_ops_czy(gds_ops=gds_ops, 
                                                            line_type=line_type, 
                                                            line_name=line_name, 
                                                            spacing=spacing, 
                                                            chip_name=chip_name, 
                                                            width=width, 
                                                            tunnel_bridge_type=tunnel_bridge_type)
