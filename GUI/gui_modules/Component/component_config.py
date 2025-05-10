DEFAULT_CATEGORIES = [
    {
        "name": "Qubit Structures",
        "components": [
            {"name": "Transmon", "command": "transmon"},
            {"name": "Xmon", "command": "xmon"}
        ]
    },
    {
        "name": "Qubit Coupling Structures",
        "components": [
            {"name": "Coupling Cavity", "command": "coupling_cavity"},
            {"name": "Coupling Line Straight", "command": "coupling_line_straight"}
        ]
    },
    {
        "name": "Readout and Measurement Structures",
        "components": [
            {"name": "Readout Cavity", "command": "readout_cavity"},
            {"name": "Readout Cavity Plus", "command": "readout_cavity_plus"},
            {"name": "Readout Cavity Flipchip", "command": "readout_cavity_flipchip"},
            {"name": "Readout Arrow", "command": "readout_arrow"},
            {"name": "Readout Arrow Plus", "command": "readout_arrow_plus"},
            {"name": "Launch Pad", "command": "launch_pad"}
        ]
    },
    {
        "name": "Control Lines and Signal Transmission Structures",
        "components": [
            {"name": "Control Line Circle", "command": "control_line_circle"},
            {"name": "Control Line Width Diff", "command": "control_line_width_diff"},
            {"name": "Transmission Path", "command": "transmission_path"},
            {"name": "Charge Line", "command": "charge_line"}
        ]
    },
    {
        "name": "Packaging and Interconnect Structures",
        "components": [
            {"name": "AirBridge", "command": "airbridge"},
            {"name": "AirbriageNb", "command": "airbriage_nb"},
            {"name": "Indium Bump", "command": "indium_bump"}
        ]
    },
    {
        "name": "Auxiliary Structures",
        "components": [
            {"name": "Coupler Base", "command": "coupler_base"}
        ]
    }
]

def get_component_config():
    """Get the default component categories configuration"""
    return DEFAULT_CATEGORIES