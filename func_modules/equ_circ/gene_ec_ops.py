from addict import Dict
from base.branch_base import BranchBase
import toolbox
import copy

def gene_ec_ops(**gene_ops):
    geo = GeneEcOps(**gene_ops)
    return copy.deepcopy(geo.branch_process())

class GeneEcOps(BranchBase):
    def __init__(self, **gene_ops):
        super().__init__(**gene_ops)
        return