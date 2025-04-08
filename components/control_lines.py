from base.cmpnts_base import CmpntsBase
from addict import Dict
import func_modules
import copy

class ControlLines(CmpntsBase):
    """
    ControlLines类，继承自CmpntsBase，用于管理和操作控制线组件。
    """

    def __init__(self, **init_ops):
        """
        初始化ControlLines对象。

        输入：
            init_ops: dict，初始化所需的参数。

        输出：
            无
        """
        self.initialization(**init_ops)  # 调用初始化方法
        return
    
    def initialization(self, **init_ops):
        """
        初始化控制线组件集合。

        输入：
            init_ops: dict，生成控制线组件的初始化参数。

        输出：
            无
        """
        # 初始化组件名称列表
        self.cmpnt_name_list = []
        # 调用功能模块生成控制线组件的选项
        options = func_modules.ctls.generate_control_lines(**init_ops)
        self.inject_options(options)  # 注入生成的参数
        return
    
    def mirror_ControlLine(self, name_list):
        """
        对指定控制线组件进行镜像操作（横向镜像）。

        输入：
            name_list: list，包含需要镜像的控制线名称列表。

        输出：
            无
        """
        # 获取当前控制线组件的参数
        ctls_ops = self.options
        for name in name_list:
            # 为镜像后的控制线生成新名称
            new_name = name + "_mirror"
            ctl_ops = copy.deepcopy(ctls_ops[name])  # 获取原控制线的参数
            new_ctl_ops = copy.deepcopy(ctl_ops)  # 创建镜像控制线的参数副本
            new_ctl_ops.name = new_name  # 设置镜像控制线的新名称

            # 对控制线的路径进行镜像操作
            path = copy.deepcopy(ctl_ops.path)
            new_path = []
            for pos in path:
                new_pos = (-pos[0], pos[1])  # 横向镜像操作
                new_path.append(copy.deepcopy(new_pos))
            new_ctl_ops.path = copy.deepcopy(new_path)  # 更新镜像后的路径

            # 将镜像后的控制线参数添加到组件集合中
            ctls_ops[new_name] = copy.deepcopy(new_ctl_ops)

        # 注入更新后的控制线组件参数
        self.inject_options(ctls_ops)
        return
