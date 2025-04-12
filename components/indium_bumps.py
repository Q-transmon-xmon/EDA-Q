from base.cmpnts_base import CmpntsBase
from addict import Dict
import func_modules

class IndiumBumps(CmpntsBase):
    def __init__(self, **init_ops):
        self.initialization(**init_ops)
        return
    
    def initialization(self, **init_ops):
        # 组件列表
        self.cmpnt_name_list = []
        # 初始化
        options = func_modules.indium_bumps.generate_indium_bumps(**init_ops)
        self.inject_options(options)
        return
    
    def counts(self):
        return len(self.options)