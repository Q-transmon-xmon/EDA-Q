#########################################################################
# File Name: __init__.py
# Description: Initialization module for superconducting quantum chip simulation.
#              Includes functionality for simulating and coupling quantum qubits.
#########################################################################

# Import necessary simulation modules
from simulation.transmon_sim import couple_pad
from simulation.transmon_sim import transmon_sim


def simulation(qubit_ops, freq, dir_name, file_name, result_name):
    """
    Main function for simulating quantum qubits.

    Inputs:
        qubit_ops: Dictionary, defines the operational parameters of the qubit.
        freq: Float, specifies the frequency of the qubit.
        dir_name: String, the directory path where simulation results are stored.
        file_name: String, the name of the input file for the simulation.
        result_name: String, the file name where simulation results will be saved.

    Outputs:
        Cq: Float, the capacitance parameter of the qubit.
        Ec: Float, the Josephson energy of the qubit.

    Function Description:
        This function calls the simulation method from the transmon_sim module
        to perform simulation computations for the quantum qubit. Based on the
        input parameters, it calculates the capacitance and Josephson energy
        of the qubit.

    Example Usage:
        qubit_ops = {...}
        freq = 5.0
        dir_name = "sim_results"
        file_name = "input_data"
        result_name = "output_data"
        Cq, Ec = simulation(qubit_ops, freq, dir_name, file_name, result_name)
    """
    # Call the simulation function from the transmon_sim module to calculate qubit parameters
    Cq, Ec = transmon_sim.simulation(qubit_ops, freq, dir_name, file_name, result_name)
    return Cq, Ec
