from base.cmpnts_base import CmpntsBase
from addict import Dict
import func_modules

class CrossOvers(CmpntsBase):
    def __init__(self, **init_ops):
        self.initialization(**init_ops)
        return
    
    def initialization(self, **init_ops):
        # Component List
        self.cmpnt_name_list = []
        # initialization
        options = func_modules.crosvs.generate_cross_overs(**init_ops)
        self.inject_options(options)
        return
    
    def generate_cross_overs(self, **gene_ops):
        crosvs_ops = func_modules.crosvs.generate_cross_overs(**gene_ops)
        self.inject_options(crosvs_ops)
        return