######################################################################################################################
#The GeneAirBridgesOps class, inherited from BranchBase, is used for generating operational parameters for air bridges.
######################################################################################################################

from base.branch_base import BranchBase
from addict import Dict
import copy
from func_modules.air_bridges import air_bridge_lzh

def gene_air_bridges_ops(**gene_ops):
    """
    Generate a set of operations for air bridges.

    Input:
        gene_ops: dict, a collection of parameters for generating air bridge operations.

    Output:
        ops: dict, the generated set of air bridge operations.

    Functions:
        1. Create a `GeneAirBridgesOps` object and pass in parameters.
        2. Call the `branch_process` method to process the generation operations.
        3. Return a deep copy of the generation result to ensure the original object is not modified.
    """
    # Create a GeneAirBridgesOps object
    goo = GeneAirBridgesOps(**gene_ops)
    # Return a deep copy of the branch processing result
    return copy.deepcopy(goo.branch_process())

class GeneAirBridgesOps(BranchBase):
    """
    The GeneAirBridgesOps class, inherited from BranchBase, is used to generate operational parameters for air bridges.

    Functions:
        1. Provide basic logic for generating air bridge operations.
        2. Support dynamic generation of air bridge parameters through branch methods.
    """

    def __init__(self, **branch_options):
        """
        Initialize the GeneAirBridgesOps object.

        Input:
            branch_options: dict, a collection of branch option parameters.

        Output:
            None

        Functions:
            Call the initialization method of the parent class BranchBase.
        """
        super().__init__(**branch_options)  # Call the parent class initialization method

    def gds_ops__line_type__line_name__spacing__chip_name__width__air_bridge_type(**gene_ops):
        """
        Generate operational parameters for air bridges.

        Input:
            gene_ops: dict, parameters required for air bridge generation.
                - gds_ops: GDS operation object, representing the geometric operation collection of the path.
                - line_type: str, the type of the path line.
                - line_name: str, the name of the path line.
                - spacing: float, the spacing of the air bridge.
                - chip_name: str, the name of the chip to which the air bridge belongs.
                - width: float, the width of the path line.
                - air_bridge_type: str, the type of the air bridge.

        Output:
            ops: dict, the generated collection of air bridge parameters.

        """
        # Deep copy the input GDS operation object
        gds_ops = copy.deepcopy(gene_ops.gds_ops)
        # Extract other generation parameters
        line_type = gene_ops.line_type
        line_name = gene_ops.line_name
        spacing = gene_ops.spacing
        chip_name = gene_ops.chip_name
        width = gene_ops.width
        air_bridge_type = gene_ops.air_bridge_type

        # Call the module method to generate air bridge operational parameters
        ops = air_bridge_lzh.auto_generate_air_bridges_ops(
            gds_ops=gds_ops,
            line_type=line_type,
            line_name=line_name,
            spacing=spacing,
            chip_name=chip_name,
            width=width,
            air_bridge_type=air_bridge_type
        )
        # Return the generated operational parameter collection
        return ops