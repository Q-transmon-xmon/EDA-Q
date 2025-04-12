from base.cmpnts_base import CmpntsBase
from addict import Dict
import func_modules

class AirBridges(CmpntsBase):
    """
    AirBridges类，继承自CmpntsBase，用于管理和操作空气桥组件（AirBridge）。
    """

    def __init__(self, **init_ops):
        """
        初始化AirBridges对象。

        输入：
            init_ops: dict，初始化所需的参数。

        输出：
            无
        """
        self.initialization(**init_ops)  # 调用初始化方法
        return
    
    def initialization(self, **init_ops):
        """
        初始化空气桥组件集合。

        输入：
            init_ops: dict，生成空气桥组件的初始化参数。

        输出：
            无
        """
        # 初始化组件名称列表
        self.cmpnt_name_list = []
        # 调用功能模块生成空气桥组件的参数
        options = func_modules.tmls.generate_transmission_lines(**init_ops)
        self.inject_options(options)  # 注入生成的参数
        return
    
    def counts(self):
        """
        统计当前空气桥组件的数量。

        输入：
            无

        输出：
            count: int，当前空气桥组件的数量。
        """
        ops = self.options  # 提取当前组件参数
        return len(ops)  # 返回组件数量
