from base.branch_base import BranchBase
from addict import Dict
import copy

def gene_others_ops(**gene_ops):
    goo = GeneOthersOps(**gene_ops)
    return copy.deepcopy(goo.branch_process())

class GeneOthersOps(BranchBase):
    def __init__(self, **branch_options):
        super().__init__(**branch_options)