from addict import Dict
from base.library_base import LibraryBase

class Qubit(LibraryBase):
    default_options = Dict(
        name = "q0",
        type = "Qubit",
        gds_pos = (0, 0),
        topo_pos = (0, 0),
        chip = "chip0",
        outline = [],
        sub_outline = [],
        readout_pins = [],
        control_pins = [],
        coupling_pins = []
    )
    def __init__(self, options):
        super().__init__(options)
        return
    
    def calc_general_ops(self):
        return

    def draw_gds(self):
        return