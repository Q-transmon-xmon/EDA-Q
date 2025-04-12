from addict import Dict
from base.branch_base import BranchBase
import toolbox
import copy

def gene_tag_ops(**gene_ops):
    gto = GeneTagOps(**gene_ops)
    return copy.deepcopy(gto.branch_process())

class GeneTagOps(BranchBase):
    def __init__(self, **gene_ops):
        super().__init__(**gene_ops)
        return