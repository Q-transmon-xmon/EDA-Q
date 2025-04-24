from base.cmpnts_base import CmpntsBase
from addict import Dict
import func_modules

class TransmissionLines(CmpntsBase):
    def __init__(self, **init_ops):
        self.initialization(**init_ops)
        return
    
    def initialization(self, **init_ops):
        # Component List
        self.cmpnt_name_list = []
        # initialization
        options = func_modules.tmls.generate_transmission_lines(**init_ops)
        self.inject_options(options)
        return