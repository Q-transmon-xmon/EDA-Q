import scqubits
# Initialize a transmon qubit
def scTransmon(EJ, EC, ng, ncut):
    transmon = scqubits.Transmon(EJ, EC, ng, ncut)
    return transmon

# Returns Hamiltonian in the charge basis. If True, the energy eigenspectrum is computed; returns Hamiltonian in the energy eigenbasis
# If para = esys, where esys is a tuple containing two ndarrays (eigenvalues and energy eigenvectors); then return the Hamiltonian in the energy eigenbasis, do not recalculate eigenspectrum
def scHamiltonian(Transmon, para = False):
    return Transmon.hamiltonian(energy_esys = para)
    
# Calculates eigenvalues using scipy.linalg.eigh, returns numpy array of eigenvalues
def scEigenvals(Transmon, evalscount = 6, file = None, returnspectrumdata = False):
    return Transmon.eigenvals(evals_count = evalscount, filename = file, return_spectrumdata = returnspectrumdata)

# Calculates eigenvalues and corresponding eigenvectors using scipy.linalg.eigh. Returns two numpy arrays containing the eigenvalues and eigenvectors, respectively
def scEigensys(Transmon, evalscount = 6, file = None, returnspectrumdata = False):
    return Transmon.eigensys(evals_count = evalscount, filename = file, return_spectrumdata = returnspectrumdata)

# Calculates eigenvalues/eigenstates for a varying system parameter, given an array of parameter values. Returns a SpectrumData object with energy_table[n] containing eigenvalues calculated for parameter value param_vals[n]
def scGet_spectrum_vs_paramvals(Transmon, param_name, param_vals, evalscount = 6, subtractground = False, geteigenstates = False, file = None, numcpus = None):
    return Transmon.get_spectrum_vs_paramvals(param_name, param_vals, evals_count = evalscount, subtract_ground = subtractground
                                              , get_eigenstates = geteigenstates, filename = file, num_cpus = numcpus)

# Return the transmon wave function in number basis. The specific index of the wave function to be returned is which
def scNumberbasis_wavefunction(Transmon, para = None, whichnum = 0):
    return Transmon.numberbasis_wavefunction(esys = para, which = whichnum)

# Return the transmon wave function in phase basis. The specific index of the wavefunction is which. esys can be provided, but if set to None then it is calculated on the fly
def scWavefunction(Transmon, para = None, whichnum = 0, phigrid = None):
    return Transmon.wavefunction(esys = para, which = whichnum, phi_grid = phigrid)

# Plots transmon wave function in charge basis
def scPlot_n_wavefunction(Transmon, para = None, smode = 'real', whichnum = 0, n_range = None, **kwargs):
    return Transmon.plot_n_wavefunction(esys = para, mode = smode, which = whichnum, nrange = n_range, **kwargs)

# Alias for plot_wavefunction
def scPlot_phi_wavefunction(Transmon, para = None, whichnum = 0, phogrid = None, smod = 'abs_sqr', caling = None,**kwargs):
    return Transmon.plot_phi_wavefunction(esys = para, which = whichnum, phi_grid = phogrid, mode = smod, scaling = caling, **kwargs)

# Returns charge operator n in the charge or eigenenergy basis
def scN_operator(Transmon, para = False):
    return Transmon.n_operator(energy_esys = para)

# Returns operator exp_i_phi in the charge or eigenenergy basis
def scExp_i_phi_operator(Transmon, para = False):
    return Transmon.exp_i_phi_operator(energy_esys = para)

# Returns operator cos phi in the charge or eigenenergy basis
def scCos_phi_operator(Transmon, para = False):
    return Transmon.cos_phi_operator(energy_esys = para)

# Returns operator sin phi in the charge or eigenenergy basis
def scSin_phi_operator(Transmon, para = False):
    return Transmon.sin_phi_operator(energy_esys = para)

# Returns table of matrix elements for operator with respect to the eigenstates of the qubit. The operator is given as a string matching a class method returning an operator matrix. E.g., for an instance trm of Transmon, 
# The matrix element table for the charge operator is given by trm.op_matrixelement_table(‘n_operator’). When esys is set to None, the eigensystem is calculated on-the-fly
def scMatrixelement_table(Transmon, op, evec = None, evalscount = 6, file = None, returndatastore = False):
    return Transmon.matrixelement_table(operator = op, evecs = evec, evals_count = evalscount, filename = file, return_datastore = returndatastore)

# Plots matrix elements for operator, given as a string referring to a class method that returns an operator matrix. E.g., for instance trm of Transmon
# The matrix element plot for the charge operator n is obtained by trm.plot_matrixelements(‘n’). When esys is set to None, the eigensystem with which eigenvectors is calculated
def scPlot_matrixelements(Transmon, op, evec = None, evalscount = 6, smode = 'abs', shownumbers = False, s3d = True, **kwargs):
    return Transmon.plot_matrixelements(operator = op, evecs = evec, evals_count = evalscount, mode = smode, show_numbers = shownumbers, show3d = s3d, **kwargs)

# Calculates matrix elements for a varying system parameter, given an array of parameter values. Returns a SpectrumData object containing matrix element data, eigenvalue data, and eigenstate data
def scGet_matelements_vs_paramvals(Transmon, op, paramname, paramvals, evalscount = 6, numcpus = None):
    return Transmon.get_matelements_vs_paramvals(operator = op, param_name = paramname, param_vals = paramvals, evals_count = evalscount, num_cpus = numcpus)

# Generates a simple plot of a set of eigenvalues as a function of one parameter. The individual points correspond to the a provided array of parameter values
def scPlot_matelem_vs_paramvals(Transmon, op, paramname, paramvals, selectelems = 4, smode = 'abs', numcpus = None, **kwargs):
    return Transmon.plot_matelem_vs_paramvals(operator = op, param_name = paramname, param_vals = paramvals, select_elems = selectelems, mode = smode, num_cpus = numcpus, **kwargs)

# Show plots of coherence for various channels supported by the qubit as they vary as a function of a changing parameter
def scPlot_coherence_vs_paramvals(Transmon, paramname, paramvals, noisechannels = None, commonnoiseoptions = None, spectrumdata = None, scale1 = 1, numcpus = None, **kwargs):
    return Transmon.plot_coherence_vs_paramvals(param_name = paramname, param_vals = paramvals, noise_channels = noisechannels, common_noise_options = commonnoiseoptions, 
                                                spectrum_data = spectrumdata, scale = scale1, num_cpus = numcpus, **kwargs)


# Plot effective T1 coherence time (rate) as a function of changing parameter
def scPlot_t1_effective_vs_paramvals(Transmon, paramname, paramvals, noisechannels = None, commonnoiseoptions = None, spectrumdata = None, getrate = None, scale1 = 1, numcpus = None, **kwargs):
    return Transmon.plot_t1_effective_vs_paramvals(param_name = paramname, param_vals = paramvals, noise_channels = noisechannels, common_noise_options = commonnoiseoptions, 
                                                   spectrum_data = spectrumdata, get_rate = getrate, scale = scale1, num_cpus = numcpus, **kwargs)


# Plot effective T2 coherence time (rate) as a function of changing parameter
def scPlot_t2_effective_vs_paramvals(Transmon, paramname, paramvals, noisechannels = None, commonnoiseoptions = None, spectrumdata = None, getrate = None, scale1 = 1, numcpus = None, **kwargs):
    return Transmon.plot_t2_effective_vs_paramvals(param_name = paramname, param_vals = paramvals, noise_channels = noisechannels, common_noise_options = commonnoiseoptions, 
                                                   spectrum_data = spectrumdata, get_rate = getrate, scale = scale1, num_cpus = numcpus, **kwargs)

# Calculate the transition time (or rate) using Fermi’s Golden Rule due to a noise channel with a spectral density spectral_density and system noise operator noise_op
def scT1(Transmon, i, j, noise_op, spectral_density, t = 0.015, total1 = True, esys1 = None, getrate = False):
    return Transmon.t1(i, j, noise_op, spectral_density, T = t, total = total1, esys = esys1, get_rate = getrate)

# T1 due to dielectric dissipation in the Josephson junction capacitances
def scT1_capacitive(Transmon, ii = 1, jj = 0, Qcap = None, t = 0.015, total1 = True, esys1 = None, getrate = False, noiseop = None, branchparams = None):
    return Transmon.t1_capacitive(i = ii, j = jj, Q_cap = Qcap, T = t, total = total1, esys = esys1, get_rate = getrate, noise_op = noiseop, branch_params = branchparams)

# Noise due to charge coupling to an impedance (such as a transmission line)
def scT1_charge_impedance(Transmon, ii = 1, jj = 0, zz = 50, t = 0.015, total1 = True, esys1 = None, getrate = False, noiseop = None):
    return Transmon.t1_charge_impedance(i = ii, j = jj, Z=zz, T = t, total = total1, esys = esys1, get_rate = getrate, noise_op = noiseop)

# Calculate the effective T1 time (or rate)
def scT1_effective(Transmon, noisechannels = None, commonnoiseoptions = None, esys1 = None, getrate = False, **kwargs):
    return Transmon.t1_effective(noise_channels = noisechannels, common_noise_options = commonnoiseoptions, esys = esys1, get_rate = getrate, **kwargs)

# Calculate the effective T2 time (or rate)
def scT2_effective(Transmon, noisechannels = None, commonnoiseoptions = None, esys1 = None, getrate = False):
    return Transmon.t2_effective(noise_channels = noisechannels, common_noise_options = commonnoiseoptions, esys = esys1, get_rate = getrate)

# Calculate the 1/f dephasing time (or rate) due to arbitrary noise source
def scTphi_1_over_f(Transmon, Anoise, ii, jj, noiseop, esys1 = None, getrate = False, **kwargs):
    return Transmon.tphi_1_over_f(A_noise = Anoise, i = ii, j = jj, noise_op = noiseop, esys = esys1, get_rate = getrate, **kwargs)

# Calculate the 1/f dephasing time (or rate) due to critical current noise
def scTphi_1_over_f_cc(Transmon, Anoise = 1e-07, ii = 0, jj = 1, esys1 = None, getrate = False, **kwargs):
    return Transmon.tphi_1_over_f_cc(A_noise = Anoise, i = ii, j = jj, esys = esys1, get_rate = getrate, **kwargs)