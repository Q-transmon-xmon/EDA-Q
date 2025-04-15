############################################################################################
# 和跨线有关的参数处理
############################################################################################

from addict import Dict
import toolbox
import copy
from components import cross_overs

def generate_ins_sheets(cpls_ops, tmls_ops):
    """根据耦合线和传输线生成绝缘垫

    输入：
        cpls_ops: 耦合线参数
        tmls_ops: 传输线参数

    输出：
        ins_sheets: 绝缘垫参数
    
    """

    # 接口
    cpls_ops = Dict(cpls_ops)
    tmls_ops = Dict(tmls_ops)

    # 生成绝缘垫
    ins_sheets = Dict()
    idx = 0

    for cpl_name, cpl_ops in cpls_ops.items():
        for tml_name, tml_ops in tmls_ops.items():
            path1 = [cpl_ops.start_pos, cpl_ops.end_pos]
            path2 = tml_ops.pos
            itscts = toolbox.calc_itscts(path1, path2)
            for itsct in itscts:
                ins_sheets["ins_sheet{}".format(idx)].name = "ins_sheet{}".format(idx)
                ins_sheets["ins_sheet{}".format(idx)].pos = itsct
                ins_sheets["ins_sheet{}".format(idx)].type = "InsulatingSheet"
                idx += 1

    return copy.deepcopy(ins_sheets)

def soak_cross_overs(cross_overs_ops):
    """根据类补全跨线参数

    输入：
        cross_overs_ops: 跨线参数

    输出：
        cross_overs_ops: 补全后的跨线参数
    """

    # 接口
    cross_overs_ops = copy.deepcopy(cross_overs_ops)

    # 获得实例
    inst = cross_overs.CrossOvers(cross_overs_ops)

    # 依次修改参数
    for k, v in cross_overs_ops.items():
        cross_overs_ops[k] = inst.options[k]

    return copy.deepcopy(cross_overs_ops)

def set_chips(cross_overs_ops, chip_name):
    """设置跨线的芯片信息

    输入：
        cross_overs_ops: 耦合线参数
        chip_name: 要设置的芯片名称

    输出： 
        cross_overs_ops: 设置芯片名称后的耦合线参数
    """
    
    # 接口
    cross_overs_ops = copy.deepcopy(cross_overs_ops)

    # 依次设置芯片信息
    for k, v in cross_overs_ops.items():
        cross_overs_ops[k].chip = chip_name
        
    return copy.deepcopy(cross_overs_ops)

def generate_crosvs_ops_from_cpls_ops_and_tmls_ops(cpls_ops, tmls_ops, crosvs_type, chip_name):
    """根据耦合线和传输线生成绝缘垫

    输入：
        cpls_ops: 耦合线参数
        tmls_ops: 传输线参数

    输出：
        ins_sheets: 绝缘垫参数
    
    """

    # 接口
    cpls_ops = Dict(cpls_ops)
    tmls_ops = Dict(tmls_ops)
    crosvs_type = crosvs_type
    chip_name = chip_name

    # 生成绝缘垫
    ins_sheets = Dict()
    idx = 0

    for cpl_name, cpl_ops in cpls_ops.items():
        for tml_name, tml_ops in tmls_ops.items():
            if cpl_ops.type != "CouplingLineStraight":
                raise ValueError("自动生成crossover暂时只支持耦合类型为CouplingLineStraight，{}的类型为{}！".format(cpl_name, cpl_ops.type))
            
            path1 = [cpl_ops.start_pos, cpl_ops.end_pos]
            path2 = tml_ops.pos
            itscts = toolbox.calc_itscts(path1, path2)
            for itsct in itscts:
                ins_sheets["ins_sheet{}".format(idx)].name = "ins_sheet{}".format(idx)
                ins_sheets["ins_sheet{}".format(idx)].chip = chip_name
                ins_sheets["ins_sheet{}".format(idx)].pos = itsct
                ins_sheets["ins_sheet{}".format(idx)].type = crosvs_type
                idx += 1

    return copy.deepcopy(ins_sheets)