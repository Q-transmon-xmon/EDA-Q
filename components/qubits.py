from base.cmpnts_base import CmpntsBase
from library import qubits
from addict import Dict
import copy, gdspy, func_modules

class Qubits(CmpntsBase):
    def __init__(self, **init_ops):
        self.initialization(**init_ops)
        return
    
    def initialization(self, **init_ops):
        # Component List
        self.cmpnt_name_list = []
        # initialization
        options = func_modules.qubits.generate_qubits(**init_ops)
        self.inject_options(options)
        return
    
    def generate_from_topo(self, topo_positions, qtype: str = "Transmon", dist: float = 2000, geometric_ops: Dict = Dict()):
        # obsolete
        options = func_modules.qubits.generate_qubits(topo_positions = topo_positions,
                                                    qtype = qtype,
                                                    dist = dist,
                                                    geometric_ops = geometric_ops)
        self.inject_options(options)
        return
    
    def calc_general_ops(self):
        for cmpnt_name in self.cmpnt_name_list:
            getattr(self, cmpnt_name).calc_general_ops()
        return
    
    def change_qubits_type(self, qubits_type):
        qubits_ops = self.extract_options()
        qubits_ops = func_modules.qubits.change_qubits_type(qubits_ops, qubits_type)
        self.inject_options(qubits_ops)
        return