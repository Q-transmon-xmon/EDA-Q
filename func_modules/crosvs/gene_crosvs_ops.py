from base.branch_base import BranchBase
from addict import Dict
import copy
from func_modules.crosvs import primitives

def gene_crosvs_ops(**gene_ops):
    gco = GeneCrosvsOps(**gene_ops)
    return copy.deepcopy(gco.branch_process())

class GeneCrosvsOps(BranchBase):
    def __init__(self, **branch_options):
        super().__init__(**branch_options)

    def cpls_ops__tmls_ops(self, branch_options):
        branch_options = copy.deepcopy(branch_options)
        cpls_ops = copy.deepcopy(branch_options.cpls_ops)
        tmls_ops = copy.deepcopy(branch_options.tmls_ops)
        crosvs_type = "InsulatingSheet"
        chip_name = "chip0"

        crosvs_ops = primitives.generate_crosvs_ops_from_cpls_ops_and_tmls_ops(cpls_ops, tmls_ops, crosvs_type, chip_name)

        return copy.deepcopy(crosvs_ops)
    
    def chip_name__cpls_ops__tmls_ops(self, branch_options):
        branch_options = copy.deepcopy(branch_options)
        cpls_ops = copy.deepcopy(branch_options.cpls_ops)
        tmls_ops = copy.deepcopy(branch_options.tmls_ops)
        crosvs_type = "InsulatingSheet"
        chip_name = branch_options.chip_name

        crosvs_ops = primitives.generate_crosvs_ops_from_cpls_ops_and_tmls_ops(cpls_ops, tmls_ops, crosvs_type, chip_name)

        return copy.deepcopy(crosvs_ops)