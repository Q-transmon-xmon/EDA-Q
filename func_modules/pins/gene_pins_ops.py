from base.branch_base import BranchBase
from addict import Dict
import copy

def gene_pins_ops(**gene_ops):
    gpo = GenePinsOps(**gene_ops)
    return copy.deepcopy(gpo.branch_process())

class GenePinsOps(BranchBase):
    def __init__(self, **branch_options):
        super().__init__(**branch_options)