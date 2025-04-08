from base.branch_base import BranchBase
from addict import Dict
import copy

def generate_indium_bumps_ops(**gene_ops):
    goo = GeneIndumpBumpsOps(**gene_ops)
    return copy.deepcopy(goo.branch_process())

class GeneIndumpBumpsOps(BranchBase):
    def __init__(self, **branch_options):
        super().__init__(**branch_options)