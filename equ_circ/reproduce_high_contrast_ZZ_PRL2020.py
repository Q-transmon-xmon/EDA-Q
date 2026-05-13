"""
Reproduction of the effective circuit model from:

"High-Contrast ZZ Interaction Using Superconducting Qubits
with Opposite-Sign Anharmonicity"

Peng Zhao et al.
Physical Review Letters 125, 200503 (2020)

DOI: 10.1103/PhysRevLett.125.200503

This script reproduces:

1. Energy-level diagrams similar to Fig. 2
2. ZZ coupling strength versus qubit detuning similar to Fig. 3(a)

Model:
------
Each superconducting qubit is modeled as a truncated
three-level anharmonic oscillator:

    H_q = ω q†q + α/2 * q†q(q†q - 1)

Two qubits are coupled through:

    H_int = g(a†b + ab†)

The total Hamiltonian is:

    H = H_a + H_b + H_int

Units:
------
All frequencies are expressed in GHz.
"""

import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. Three-level truncated operators
# ============================================================

N = 3  # Hilbert space dimension for each qubit


def destroy(N):
    """
    Create annihilation operator for N-level system.
    """
    a = np.zeros((N, N), dtype=complex)

    for n in range(1, N):
        a[n - 1, n] = np.sqrt(n)

    return a


# Single-qubit operators
I = np.eye(N)

q = destroy(N)
qd = q.conj().T

# Two-qubit tensor-product operators
qa = np.kron(q, I)
qb = np.kron(I, q)

qad = qa.conj().T
qbd = qb.conj().T

# Number operators
na = qad @ qa
nb = qbd @ qb

Id = np.eye(N * N)


# ============================================================
# 2. Bare basis states |ij>
# ============================================================

basis = {}

for i in range(N):
    for j in range(N):

        vec = np.zeros(N * N, dtype=complex)

        # Tensor basis ordering:
        # |00>, |01>, |02>, |10>, ...
        vec[i * N + j] = 1.0

        basis[(i, j)] = vec


# ============================================================
# 3. Hamiltonian construction
# ============================================================

def hamiltonian(wa, wb, alpha_a, alpha_b, g):
    """
    Construct total Hamiltonian:

        H = H_a + H_b + H_int

    where

        H_q = ω q†q + α/2 * n(n-1)

        H_int = g(a†b + ab†)

    Parameters
    ----------
    wa, wb : float
        Qubit frequencies (GHz)

    alpha_a, alpha_b : float
        Anharmonicities (GHz)

    g : float
        Coupling strength (GHz)
    """

    # Anharmonic oscillator Hamiltonian for qubit A
    Ha = wa * na + alpha_a / 2 * (na @ (na - Id))

    # Anharmonic oscillator Hamiltonian for qubit B
    Hb = wb * nb + alpha_b / 2 * (nb @ (nb - Id))

    # Exchange-type coupling interaction
    Hint = g * (qad @ qb + qa @ qbd)

    return Ha + Hb + Hint


# ============================================================
# 4. Label eigenstates by maximum overlap
# ============================================================

def label_eigenenergies(H):
    """
    Diagonalize Hamiltonian and assign eigenenergies
    according to maximum overlap with bare basis states.

    Returns
    -------
    labeled : dict
        Example:
            labeled[(1,0)] = energy of |10>_e
    """

    evals, evecs = np.linalg.eigh(H)

    labeled = {}
    used = set()

    for state, bare_vec in basis.items():

        # Overlap between eigenstates and bare state
        overlaps = np.abs(evecs.conj().T @ bare_vec) ** 2

        # Sort by descending overlap
        order = np.argsort(overlaps)[::-1]

        for idx in order:

            # Prevent duplicate assignment
            if idx not in used:
                labeled[state] = evals[idx].real
                used.add(idx)
                break

    return labeled


# ============================================================
# 5. ZZ coupling strength
# ============================================================

def zz_coupling(wa, wb, alpha_a, alpha_b, g):
    """
    Compute ZZ coupling strength:

        ζ = (E11 - E01) - (E10 - E00)

    Returns
    -------
    zeta : float
        ZZ coupling strength (GHz)
    """

    H = hamiltonian(wa, wb, alpha_a, alpha_b, g)

    E = label_eigenenergies(H)

    zeta = (
        (E[(1, 1)] - E[(0, 1)])
        - (E[(1, 0)] - E[(0, 0)])
    )

    return zeta


# ============================================================
# 6. Parameters from the paper
# ============================================================

wb = 5.5        # GHz
alpha = 0.250   # GHz = 250 MHz
g = 0.015       # GHz = 15 MHz

# Detuning:
# Δ = wa - wb
Delta_list = np.linspace(-0.5, 0.5, 801)  # GHz

wa_list = wb + Delta_list


# ============================================================
# 7. Plot energy-level diagrams (similar to Fig. 2)
# ============================================================

def plot_energy_levels(alpha_a, alpha_b, title):
    """
    Plot energy levels versus detuning.
    """

    states_to_plot = [
        (0, 1),
        (1, 0),
        (1, 1),
        (0, 2),
        (2, 0),
    ]

    energy_data = {s: [] for s in states_to_plot}

    # Sweep qubit frequency wa
    for wa in wa_list:

        H = hamiltonian(
            wa=wa,
            wb=wb,
            alpha_a=alpha_a,
            alpha_b=alpha_b,
            g=g
        )

        E = label_eigenenergies(H)

        for s in states_to_plot:
            energy_data[s].append(E[s])

    # Plot
    plt.figure(figsize=(7, 5))

    for s in states_to_plot:

        plt.plot(
            Delta_list * 1000,  # convert GHz -> MHz
            energy_data[s],
            label=fr"$|{s[0]}{s[1]}\rangle_e$"
        )

    plt.xlabel(r"Detuning $\Delta = \omega_a - \omega_b$ (MHz)")
    plt.ylabel("Energy (GHz)")

    # Match paper visualization range
    plt.ylim(4, 12)

    plt.title(title)

    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()


# ============================================================
# 8. AA-type system
#    Two qubits with same-sign anharmonicity
# ============================================================

plot_energy_levels(
    alpha_a=-alpha,
    alpha_b=-alpha,
    title="AA-type: Same-sign Negative Anharmonicity"
)


# ============================================================
# 9. AB-type system
#    Opposite-sign anharmonicity
# ============================================================

plot_energy_levels(
    alpha_a=-alpha,
    alpha_b=+alpha,
    title="AB-type: Opposite-sign Anharmonicity"
)


# ============================================================
# 10. ZZ coupling vs detuning (similar to Fig. 3a)
# ============================================================

zeta_AA = []
zeta_AB = []

for Delta in Delta_list:

    wa = wb + Delta

    # AA-type
    zeta_AA.append(
        zz_coupling(
            wa=wa,
            wb=wb,
            alpha_a=-alpha,
            alpha_b=-alpha,
            g=g
        )
    )

    # AB-type
    zeta_AB.append(
        zz_coupling(
            wa=wa,
            wb=wb,
            alpha_a=-alpha,
            alpha_b=+alpha,
            g=g
        )
    )

zeta_AA = np.array(zeta_AA)
zeta_AB = np.array(zeta_AB)


# ============================================================
# 11. Plot ZZ coupling
# ============================================================

plt.figure(figsize=(7, 5))

# AB-type
plt.plot(
    Delta_list * 1000,
    np.abs(zeta_AB) * 1000,
    label="AB type"
)

# AA-type
plt.plot(
    Delta_list * 1000,
    np.abs(zeta_AA) * 1000,
    "--",
    label="AA type"
)

plt.xlabel(r"Detuning $\Delta$ (MHz)")
plt.ylabel(r"$|\zeta|$ (MHz)")

plt.title("ZZ Coupling Strength vs Detuning")

plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
