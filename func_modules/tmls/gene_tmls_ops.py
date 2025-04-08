from addict import Dict
import copy
from base.branch_base import BranchBase

def gene_tmls_ops(**gene_ops):
    gto = GeneTmlsOps(**gene_ops)
    return copy.deepcopy(gto.branch_process())

class GeneTmlsOps(BranchBase):
    def options(self, gene_ops):
        return super().options(gene_ops)