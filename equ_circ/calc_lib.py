###############################################################################################
# File Name: calc_lib.py
# Description: This file provides functionality for calculating quantum bit parameters.
############################################################################################

import numpy as np


def calculate_qubits_parms(f_q, Ec):
    """
    Calculate quantum bit parameters.

    Input:
        f_q: Quantum bit frequency in GHz.
        Ec: Josephson energy of the quantum bit.

    Output:
        None.
    """
    # Convert Josephson energy to Hz
    Ec = Ec * 2 * np.pi * 1e6
    # Physical constants
    e = 1.60217657e-19  # Elementary charge
    h = 6.62606957e-34  # Planck's constant
    hbar = 1.0545718e-34  # Reduced Planck's constant
    phinot = 2.067 * 1e-15  # Magnetic flux quantum
    phi0 = phinot / (2 * np.pi)  # Reduced magnetic flux quantum
    c = 3e8  # Speed of light

    # Calculate Josephson energy
    Ej = ((f_q * 10 ** 9 + Ec) ** 2) / (8 * Ec)
    print("If fq =", f_q, 'GHz')
    print("then, Ej =", round((Ej / 10 ** 9), 2), "GHz")

    # Calculate critical current
    Ic = Ej * h / phi0
    print("then, Ic =", round((Ic * 10 ** 9), 2), "nA")

    # Calculate normal state resistance
    Rn = np.pi * 0.182e-3 / 2 / Ic
    print("then, Rn =", round(Rn, 4), "Ω")
    return