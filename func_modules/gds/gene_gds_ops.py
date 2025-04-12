from addict import Dict
from base.branch_base import BranchBase
import toolbox
import copy

def gene_gds_ops(**gene_ops):
    ggo = GeneGdsOps(**gene_ops)
    return copy.deepcopy(ggo.branch_process())

class GeneGdsOps(BranchBase):
    def __init__(self, **gene_ops):
        super().__init__(**gene_ops)
        return