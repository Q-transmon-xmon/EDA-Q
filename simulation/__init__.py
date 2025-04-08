#########################################################################
# File Name: __init__.py
# Function Description: Initialization module for quantum chip simulation.
#                       Includes various simulation classes and their processing methods.
#########################################################################

from addict import Dict
import copy, toolbox
from base.branch_base import BranchBase
from simulation import xmon_sim, xmon_sim_plane, rdls_tmls, transmon_sim


def simulation(**sim_ops):
    """
    Main simulation function that initializes the SimBranch class and
    processes the simulation based on provided options.

    Inputs:
        sim_ops: Dictionary, simulation operation parameters.

    Outputs:
        Result of the branch process as a Dict.
    """
    sb = SimBranch(**sim_ops)
    return sb.branch_process()


class SimBranch(BranchBase):
    def branch_process(self):
        """
        Handles the branch processing by determining the simulation module 
        and executing the corresponding simulation method.

        Outputs:
            result: Dictionary containing the results of the simulation.
        """
        # Interface
        branch_options = copy.deepcopy(self.branch_options)
        hash_num = branch_options.sim_module

        # Check for empty module
        if hash_num == "":
            return Dict()

        # Check for errors
        if not hasattr(self, hash_num):
            raise ValueError("Method {} not found".format(hash_num))

        # Branch processing
        result = getattr(self, hash_num)(branch_options)

        return copy.deepcopy(result)

    def Flipchip_Xmon(self, sim_ops):
        """
        Process the Flipchip Xmon simulation.

        Inputs:
            sim_ops: Dictionary, simulation operation parameters for Flipchip Xmon.
        """
        fcx = FlipchipXmon(**sim_ops)
        fcx.branch_process()
        return

    def s21(self, sim_ops):
        """
        Process the S21 simulation.

        Inputs:
            sim_ops: Dictionary, simulation operation parameters for S21.
        """
        sss = S21(**sim_ops)
        sss.branch_process()
        return

    def TransmonSim(self, sim_ops):
        """
        Process the Transmon simulation.

        Inputs:
            sim_ops: Dictionary, simulation operation parameters for Transmon.
        """
        ts = TransmonSim(**sim_ops)
        ts.branch_process()
        return

    def PlaneXmonSim(self, sim_ops):
        """
        Process the Plane Xmon simulation.

        Inputs:
            sim_ops: Dictionary, simulation operation parameters for Plane Xmon.
        """
        pxs = PlaneXmonSim(**sim_ops)
        pxs.branch_process()
        return


class PlaneXmonSim(BranchBase):
    def gds_ops__qubit_name__sim_module(self, sim_ops):
        """
        Execute the Plane Xmon simulation based on GDS operations and qubit name.

        Inputs:
            sim_ops: Dictionary, simulation operation parameters 
                     including GDS operations and qubit name.
        """
        sim_ops = copy.deepcopy(sim_ops)
        gds_ops = copy.deepcopy(sim_ops.gds_ops)
        qubit_name = sim_ops.qubit_name
        dir_name = "C:/sim_proj/PlaneXmon_sim/Xmon_random_capacity_{}.txt".format(qubit_name)

        toolbox.jg_and_create_path(dir_name)

        qubit_ops = gds_ops.qubits[qubit_name]
        xmon_sim_plane.simulation(qubit=qubit_ops, path=dir_name)

        return


class FlipchipXmon(BranchBase):
    def ctl_name__gds_ops__path__q_name__sim_module(self, sim_ops):
        """
        Execute Flipchip Xmon simulation with control line, GDS operations, and path.

        Inputs:
            sim_ops: Dictionary, simulation operation parameters 
                     including control line name, GDS operations, and path.

        Outputs:
            Cq: Float, capacitance parameter of the qubit.
            Ec: Float, Josephson energy of the qubit.
        """
        gds_ops = copy.deepcopy(sim_ops.gds_ops)
        q_name = sim_ops.q_name
        ctl_name = sim_ops.ctl_name
        path = sim_ops.path

        q_ops = gds_ops.qubits[q_name]
        ctl_ops = gds_ops.control_lines[ctl_name]

        Cq, Ec = xmon_sim.simulation(qubit=q_ops, ctl=ctl_ops, path=path)

        return Cq, Ec

    def ctl_name__gds_ops__q_name__sim_module(self, sim_ops):
        """
        Execute Flipchip Xmon simulation using control line and GDS operations 
        with a default path.

        Inputs:
            sim_ops: Dictionary, simulation operation parameters 
                     including control line name, GDS operations, and qubit name.

        Outputs:
            Cq: Float, capacitance parameter of the qubit.
            Ec: Float, Josephson energy of the qubit.
        """
        gds_ops = copy.deepcopy(sim_ops.gds_ops)
        q_name = sim_ops.q_name
        ctl_name = sim_ops.ctl_name
        path = "./sim/Flipchip_Xmon/capacitance_matrix.txt"

        q_ops = gds_ops.qubits[q_name]
        ctl_ops = gds_ops.control_lines[ctl_name]

        Cq, Ec = xmon_sim.simulation(qubit=q_ops, ctl=ctl_ops, path=path)

        return Cq, Ec


class S21(BranchBase):
    def gds_ops__mode__pin0_name__pin1_name__rdl_name__sim_module__tml_name(self, sim_ops):
        """
        Execute S21 simulation based on GDS operations and various components.

        Inputs:
            sim_ops: Dictionary, simulation operation parameters 
                     including GDS operations, mode, pin names, RDL name, and TML name.

        Outputs:
            ideal_freq: Float, ideal frequency result from the simulation.
        """
        print("==========================================================s21")
        gds_ops = copy.deepcopy(sim_ops.gds_ops)
        mode = sim_ops.mode
        pin0_name = sim_ops.pin0_name
        pin1_name = sim_ops.pin1_name
        rdl_name = sim_ops.rdl_name
        tml_name = sim_ops.tml_name

        rdl_ops = gds_ops.readout_lines[rdl_name]
        tml_ops = gds_ops.transmission_lines[tml_name]
        pin0_ops = gds_ops.pins[pin0_name]
        pin1_ops = gds_ops.pins[pin1_name]

        ideal_freq = rdls_tmls.simulation(rdl_ops=rdl_ops,
                                          tml_ops=tml_ops,
                                          pin0_ops=pin0_ops,
                                          pin1_ops=pin1_ops,
                                          mode=mode)
        return ideal_freq


class TransmonSim(BranchBase):
    def frequency__gds_ops__qubit_name__sim_module(self, sim_ops):
        """
        Execute Transmon simulation based on frequency and GDS operations.

        Inputs:
            sim_ops: Dictionary, simulation operation parameters 
                     including frequency, GDS operations, and qubit name.

        Outputs:
            Cq: Float, capacitance parameter of the qubit.
            Ec: Float, Josephson energy of the qubit.
        """
        sim_ops = copy.deepcopy(sim_ops)
        gds_ops = copy.deepcopy(sim_ops.gds_ops)
        qubit_name = sim_ops.qubit_name
        freq = sim_ops.frequency
        dir_name = "C:/sim_proj/transmon_sim/"
        file_name = "transmon_sim.aedt"
        result_name = "capacitance_matrix.txt"

        toolbox.jg_and_create_path(dir_name)

        qubit_ops = gds_ops.qubits[qubit_name]
        Cq, Ec = transmon_sim.simulation(qubit_ops,
                                         freq=freq,
                                         dir_name=dir_name,
                                         file_name=file_name,
                                         result_name=result_name)

        return Cq, Ec

    def frequency__gds_ops__path__qubit_name__sim_module(self, sim_ops):
        """
        Execute Transmon simulation with a specified path based on frequency and GDS operations.

        Inputs:
            sim_ops: Dictionary, simulation operation parameters 
                     including frequency, GDS operations, qubit name, and path.

        Outputs:
            Cq: Float, capacitance parameter of the qubit.
            Ec: Float, Josephson energy of the qubit.
        """
        sim_ops = copy.deepcopy(sim_ops)
        gds_ops = copy.deepcopy(sim_ops.gds_ops)
        qubit_name = sim_ops.qubit_name
        freq = sim_ops.frequency
        workpath = sim_ops.path

        import os
        file_name = os.path.basename(workpath)
        dir_name = os.path.dirname(workpath)
        dir_name += "/"
        print("dir_name = {}".format(dir_name))
        print("file_name = {}".format(file_name))
        result_name = "capacitance_matrix.txt"

        toolbox.jg_and_create_path(dir_name)

        qubit_ops = gds_ops.qubits[qubit_name]
        Cq, Ec = transmon_sim.simulation(qubit_ops,
                                         freq=freq,
                                         dir_name=dir_name,
                                         file_name=file_name,
                                         result_name=result_name)

        return Cq, Ec

def new_sim_method(gds_ops):
    ################################ 
    # simultion (your code)
    print("new simulation method to be continued...")
    import toolbox
    toolbox.show_options(gds_ops)
    ################################
    return