from func_modules.tunnel_bridges import generate_tunnel_bridges
import copy

def auto_generate_tunnel_bridges_ops_czy(gds_ops, line_type, line_name, spacing=120, chip_name="chip3", width=10, tunnel_bridge_type="CoverBridge"):
    gds_ops = copy.deepcopy(gds_ops)
    """
    Automatically generate air bridges.

    Input:
        gds_ops: dict, parameters for the GDS layout.
        line_type: str, the type of line where the air bridge is located.
        line_name: str, the name of the line where the air bridge is located.
        spacing: int or float, the spacing of the air bridge.
        chip_name: str, the name of the chip where the air bridge is located.
        width: int or float, the width of the air bridge.
        air_bridge_type: str, the type of air bridge.

    Output:
        ops: dict, the generated air bridge parameters.

    """

    # Interface with yxh
    ## pos
    line_ops = gds_ops[line_type][line_name]
    if "pos" in line_ops.keys():
        path = gds_ops[line_type][line_name].pos
    elif "path" in line_ops.keys():
        path = gds_ops[line_type][line_name].path
    else:
        #print(line_ops.keys())
        raise ValueError("The selected component properties do not have pos or path, unable to automatically generate air bridges")
    pos = path
    ## bend_radius
    bend_radius = gds_ops[line_type][line_name].corner_radius
    ## spacing
    spacing = spacing
    ## chip_type
    chip_type = chip_name
    width1 = gds_ops[line_type][line_name].width
    gap = gds_ops[line_type][line_name].gap
    ## width
    width = width
    ## air_bridge
    
    
    ops = generate_tunnel_bridges.add_tunnel_bridges_czy(pos=path,
                                                   bend_radius=bend_radius,
                                                   width1 = width1,
                                                   gap = gap,
                                                   spacing=spacing,
                                                   chip_type=chip_type,
                                                   width=width,
                                                   tunnel_bridge_type=tunnel_bridge_type)
    return ops