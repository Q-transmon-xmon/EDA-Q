from base.branch_base import BranchBase
from addict import Dict
import copy

def gene_ctls_ops(**gene_ops):
    gco = GeneCtlsOps(**gene_ops)
    return copy.deepcopy(gco.branch_process())

class GeneCtlsOps(BranchBase):
    def __init__(self, **branch_options):
        super().__init__(**branch_options)