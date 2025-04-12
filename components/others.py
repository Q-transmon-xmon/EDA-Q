from base.cmpnts_base import CmpntsBase
from addict import Dict
import func_modules
import copy

class Others(CmpntsBase):
    """
    Others类，继承自CmpntsBase，用于管理和操作其他类型的组件。
    """

    def __init__(self, **init_ops):
        """
        初始化Others对象。

        输入：
            init_ops: dict，初始化所需的参数。

        输出：
            无
        """
        self.initialization(**init_ops)  # 调用初始化方法
        return
    
    def initialization(self, **init_ops):
        """
        初始化其他组件集合。

        输入：
            init_ops: dict，生成其他组件集合的初始化参数。

        输出：
            无
        """
        # 初始化组件名称列表
        self.cmpnt_name_list = []
        # 调用功能模块生成其他组件的选项
        options = func_modules.others.generate_others(**init_ops)
        self.inject_options(options)  # 注入生成的参数
        return
    
    def mirror_ZlineNju(self, name_list):
        """
        对指定的ZlineNju组件进行横向镜像操作。

        输入：
            name_list: list，包含需要镜像的组件名称列表。

        输出：
            无
        """
        # 获取当前ZlineNju组件的参数集合
        zline_njus_ops = self.options
        for name in name_list:
            # 提取原组件参数
            zline_nju_ops = copy.deepcopy(zline_njus_ops[name])
            
            # 创建镜像组件的参数副本
            new_zline_nju_ops = copy.deepcopy(zline_nju_ops)
            new_name = name + "_mirror"  # 镜像组件名称
            new_zline_nju_ops.name = new_name

            # 对初始位置进行横向镜像
            line_init_pos = copy.deepcopy(zline_nju_ops.line_init_pos)
            new_line_init_pos = []
            for pos in line_init_pos:
                new_pos = (-pos[0], pos[1])  # 横向镜像操作（x坐标取负）
                new_line_init_pos.append(copy.deepcopy(new_pos))
            new_zline_nju_ops.line_init_pos = copy.deepcopy(new_line_init_pos)

            # 对结束位置进行横向镜像
            line_end_pos = copy.deepcopy(zline_nju_ops.line_end_pos)
            new_line_end_pos = []
            for pos in line_end_pos:
                new_pos = (-pos[0], pos[1])  # 横向镜像操作（x坐标取负）
                new_line_end_pos.append(copy.deepcopy(new_pos))
            new_zline_nju_ops.line_end_pos = copy.deepcopy(new_line_end_pos)

            # 将镜像后的组件添加到集合中
            zline_njus_ops[new_name] = copy.deepcopy(new_zline_nju_ops)

        # 注入更新后的组件参数集合
        self.inject_options(zline_njus_ops)
        return
