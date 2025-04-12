from addict import Dict
import copy, func_modules
from base.branch_base import BranchBase
from library import chips as chips_lib

def gene_chips_ops(**gene_ops):
    gco = GeneChipsOps(**gene_ops)
    return copy.deepcopy(gco.branch_process())

class GeneChipsOps(BranchBase):
    def __init__(self, **branch_options):
        super().__init__(**branch_options)