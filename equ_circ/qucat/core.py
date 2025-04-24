#########################################################################
# File Name: core.py
# Description: Defines the core functionalities and classes of the quantum circuit analysis tool QuCAT.
#              Includes circuit construction, Hamiltonian generation, mode frequencies, dissipation rates,
#              nonlinearity, and cross-Kerr interaction calculations.
#########################################################################
import sympy as sp
from sympy.utilities.lambdify import lambdify
import numpy as np
from numpy.polynomial.polynomial import Polynomial as npPoly
from sympy.core.mul import Mul, Pow, Add
from copy import deepcopy
from numbers import Number
from math import floor, factorial
import os
from subprocess import run
import inspect
import matplotlib.pyplot as plt
import time
from warnings import warn
try:
    from equ_circ.qucat._constants import *
    from equ_circ.qucat._utility import *
    from equ_circ.qucat.plotting_settings import plotting_parameters_show,plotting_parameters_normal_modes
except ImportError:
    # When running from source without pip installation
    from _constants import *
    from _utility import *
    from plotting_settings import plotting_parameters_show,plotting_parameters_normal_modes

PROFILING = False

def timeit(method):
    '''
    Decorator which prints the time 
    a function took to execute.
    Only works the global variable PROFILING is set to True.
    '''
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if PROFILING:
            print('calling %r took %2.2f ms' % \
                    (method.__name__, (te - ts) * 1000))
        return result
    return timed

def string_to_component(s, *arg, **kwarg):
    '''
    Allows the creation of a Component object using a string.

    Parameters
    ----------
    s : string
        One of 'W', 'R', 'L', 'J', 'C', 'G', dicatates the type 
        of component to create
    args, kwargs : 
        Arguments needed for the component creation

    Returns
    -------
    A component of type ``s``
    '''
    if s == 'W':
        return W(*arg, **kwarg)
    elif s == 'R':
        return R(*arg, **kwarg)
    elif s == 'L':
        return L(*arg, **kwarg)
    elif s == 'J':
        return J(*arg, **kwarg)
    elif s == 'C':
        return C(*arg, **kwarg)
    elif s == 'G':
        return G(*arg, **kwarg)

class Qcircuit(object):
    """A class representing a quantum circuit.

    Attributes:
        components (dict): Dictionary of components having a label, such that a component 
            with label 'L_1' can be obtained by ``Qcircuit.components['L_1']``
        Q_min (float): Modes with have a quality factor below Q_min will not ignored
        inductors (list): List of inductor objects present in the circuit
        resistors (list): List of inductor objects present in the circuit
        junctions (list): List of junction objects present in the circuit
        capacitors (list): List of capacitor objects present in the circuit
        netlist (list): List of all components present in the circuit
        ref_elt (J or L): list of junction or inductor component used as a reference for the calculation 
                        of zero-point fluctations, each index of the list corresponds to a different mode
    """

    def __init__(self, netlist):
        self.Q_min = 1 # Modes with have a quality factor below Q_min will not ignored

        self.warn_discarded_mode = True # If this is set to True, the user will be notified when a mode is discarded.
        
        # After an initial estimation of the complex eigenfrequenceis using a diaglinalization
        # of the companion matrix, the frequencies are polishd to a tolerence
        # self.root_relative_tolerance using a gradient based root finder, with a maximum number of iterations self.root_max_iterations
        self.root_max_iterations = 1e4 
        self.root_relative_tolerance = 1e-12

        self._plotting_normal_mode = False # Used to keep track of which imported plotting_settings to use 
                                            # only set to true when show_normal_mode is called
        self.plotting_parameters_normal_modes = plotting_parameters_normal_modes
        self.plotting_parameters_show = plotting_parameters_show

        self.netlist = netlist # List of all components present in the circuit

        self._network = _Network(netlist) # Converts the list of components into a network object
                # The Network object has methods to compute of the admittance between two nodes
                # or the tranfer function between two nodes and two others
        
        # We construct (enpty) lists of all the different type of 
        # components that could be present in the circuit
        self.inductors = []
        self.capacitors = []
        self.junctions = []
        self.resistors = []
        self._wire = []
        self._grounds = []

        # Initialize a dictionary of components having a label, such that a component 
        # with label 'L_1' can be obtained by ``Qcircuit.components['L_1']``
        self.components = {}

        # Initialize a list which will contain the labels of the componentns which have
        # no value (these will have to be specified in most methods as a kwarg)
        self._no_value_components = []

        # For each component of the circuit....
        for elt in netlist:
            # ...tell the component what circuit it belongs to
            elt._circuit = self
            # ...and populate the empty lists/dictionaries initialized above with the element if appropriate
            elt._set_component_lists()


        # Check that there is at least one inductive element in the circuit
        if len(self.junctions) == 0 and len(self.inductors) == 0:
            raise ValueError(
                "There should be at least one junction or inductor in the circuit")

        # Check that there is at least one capacitive element in the circuit
        if len(self.capacitors) == 0:
            raise ValueError(
                "There should be at least one capacitor in the circuit")

                
        # define the function which returns the inverse of dY
        # where Y is the admittance at the nodes of an inductive element
        for inductive_element in self.inductors+self.junctions:
            inductive_element._compute_flux_zpf_r()

        # Initialize the flux transformation dictionary,
        # where _flux_transformation_dict[ref_node_minus,ref_node_plus,node_minus,node_plus] 
        # will be populated with a function which gives
        # the voltage transfer function between the nodes surrounding
        # the reference element and (node_plus,node_minus)
        # this function takes as an argument an angular frequency
        # and keyword arguments if component values need to be specified
        self._flux_transformation_dict = {}

        # define the functions which returns the components of the characteristic polynomial
        # (the roots of which are the eigen-frequencies)
        self._char_poly_coeffs = [lambdify(self._no_value_components, c, 'numpy') 
            for c in self._network.compute_char_poly_coeffs(is_lossy = (len(self.resistors)>0))]

    @property
    def _pp(self):
        '''
        Returns the plotting parameters used 
            * in the Qcircuit.show method (if self._plotting_normal_mode is False)
            * in the Qcircuit.show_normal_modes() method (if self._plotting_normal_mode is True)
        '''
        if self._plotting_normal_mode:
            return self.plotting_parameters_normal_modes
        else:
            return self.plotting_parameters_show

    def _parse_kwargs(self, **kwargs):
        '''
        Raises a ValueError 
        * if one of the kwargs is not the label of a circuit element
        * if a component without a value has not had its value specified in the kwargs 

        Called in all functions accepting keyword arguments (for un-specified circuit components).
        
        Parameters
        ----------
        kwargs:     
                    Values for un-specified circuit components, 
                    ex: ``L=1e-9``.
        '''
        for key in kwargs:
            if key in self._no_value_components:
                kwargs[key]  = kwargs[key]
            else:
                if key in self.components:
                    raise ValueError(
                        f"A value for the component labelled '{key}' " 
                        "has already been specified when building the circuit. "
                        "To be able to change it, you should re-build the circuit "
                        "without specifying its value." )
                else:
                    raise ValueError(
                        '%s is not the label of a circuit element' % key)

        for label in self._no_value_components:
            try:
                kwargs[label]
            except Exception:
                raise ValueError(
                    'The value of %s should be specified with the keyword argument %s=... ' % (label, label))

    @timeit
    def _set_zeta(self, **kwargs):
        '''
        Sets the Qcircuit.zeta to the circuit eigenfrequencies
        (including the imaginary part due to losses).

        Parameters
        ----------
        kwargs:     
                    Values for un-specified circuit components, 
                    ex: ``L=1e-9``.
        '''

        # Check if the kwargs provided are correct
        self._parse_kwargs(**kwargs)

        try:
            if kwargs == self._kwargs_previous:
                # Avoid doing the same thing two
                # times in a row
                return
        except AttributeError:
            pass
        self._kwargs_previous = kwargs

        if len(self.resistors) == 0:

            # Compute the coefficients of the characteristic polynomial.
            # The roots of this polynomial will provide the complex eigenfrequencies
            char_poly = npPoly([np.real(coeff(**kwargs)) for coeff in self._char_poly_coeffs])
            
            # char_poly = remove_multiplicity(char_poly)
        
            # In this case, the variable of the characteristic polynomial is \omega^2
            # And we can safely take the real part of the solution as there are no
            # resistors in the circuit.
            w2 = np.real(char_poly.roots())
            w2 = polish_roots(char_poly,w2, self.root_max_iterations,np.sqrt(self.root_relative_tolerance))

            # Sometimes, when the circuits has vastly different
            # values for its circuit components or modes are too
            # decoupled, the symbolic 
            # calculations can yield an incorrect char_poly
            # We can easily discard some of these casese by throwing away
            # negative solutions
            for w2_single in w2:
                if np.real(w2_single) < 0 and self.warn_discarded_mode:
                    error_message = "Imaginary frequency mode f = 1j %f Hz mode found (and discarded).\n"%(np.sqrt(-w2_single)/2/np.pi)
                    warn(error_message)
            w2 = w2[np.nonzero(w2 >= 0.)]

            # Take the square root to get to the eigenfrequencies
            zeta = np.sqrt(w2)

            # Sort solutions with increasing frequency
            order = np.argsort(np.real(zeta))
            zeta = zeta[order]

        else:

            # Compute the coefficients of the characteristic polynomial.
            # The roots of this polynomial will provide the complex eigenfrequencies
            char_poly = npPoly([complex(coeff(**kwargs)) for coeff in self._char_poly_coeffs])
            # char_poly = remove_multiplicity(char_poly)

            zeta = char_poly.roots()
            zeta = polish_roots(char_poly,zeta, self.root_max_iterations,self.root_relative_tolerance)

            # Sort solutions with increasing frequency
            order = np.argsort(np.real(zeta))
            zeta = zeta[order]

            # Negative modes are discarded
            zeta = zeta[np.nonzero(np.real(zeta) >= 0.)]

            # For each solution, its complex conjugate
            # is also a solution, we want to discard the negative
            # imaginary part solutions which correspond to unphysical
            # negative dissipation modes
            zeta = zeta[np.nonzero(np.imag(zeta) >= 0.)]

        # zero frequency modes are discarded
        zeta = zeta[np.nonzero(np.logical_not(np.isclose(np.real(zeta),0*zeta, rtol = self.root_relative_tolerance)))]

        # Only consider modes with Q>self.Q_min (=1 by default)
        # The reason for this measure is that
        # 0-frequency solutions (with real parts close to 0)
        # tend to have frequencies which oscillate between positive and
        # negative values.
        # The negative values are discarded which changes the number of modes
        # and makes parameter sweeps difficult 
        for w in zeta:
            if np.real(w) < self.Q_min*2*np.imag(w) and self.warn_discarded_mode:
                error_message = "Discarding f = %f Hz mode "%(np.real(w/2/np.pi))
                error_message += "since it has a too low quality factor Q = %f < %f"%(np.real(w)/2/np.imag(w),self.Q_min)
                warn(error_message)
        zeta = zeta[np.nonzero(np.real(zeta) >= self.Q_min*2*np.imag(zeta))]

        # Choose reference elements for each mode which 
        # maximize the inverse of dY: we want the reference 
        # element to the element where zero-point fluctuations
        # in flux are most localized.
        inductive_elements = self.junctions+self.inductors
        ref_elt = []
        zeta_copy = deepcopy(zeta)
        zeta = []
        
        for w in zeta_copy:
            largest_dYm1 = 0
            ref_elt_index = None
            for ind_index,ind in enumerate(inductive_elements):
                try:
                    dYm1 = ind._flux_zpf_r(w,**kwargs)
                except Exception:
                    # Computation of dYm1 failed for some reason
                    dYm1 = -1
                    
                if dYm1>largest_dYm1:
                    ref_elt_index = ind_index
                    largest_dYm1 = dYm1

            if ref_elt_index is None and self.warn_discarded_mode:
                # Sometimes, when the circuits has vastly different
                # values for its circuit components or modes are too
                # decoupled, the symbolic 
                # calculations can yield an incorrect char_poly
                # We can easily discard some of these cases by throwing away
                # any solutions with a complex impedance (ImY'<0)
                error_message = "Discarding f = %f Hz mode.\n"%(np.real(w/2/np.pi))
                error_message += "since the calculation of zero-point-fluctuations was unsuccesful.\n"
                warn(error_message)
            else:
                zeta.append(w)
                ref_elt.append(inductive_elements[ref_elt_index])
        zeta = np.array(zeta)

        self.zeta = zeta
        self.ref_elt = ref_elt

    def _anharmonicities_per_junction(self, **kwargs):
        '''
        Returns the contribution of each junction to the anharmonicity of each mode.
        For more details, see the documentation of J.anharmonicity.

        Anharmonicities are given in units of Hz (not angular frequency).

        Parameters
        ----------
        kwargs:     
                    Values for un-specified circuit components, 
                    ex: ``L=1e-9``.

        Returns
        -------
        anh_per_jun: ndarray
            where ``anh_per_jun[j,m]`` corresponds to the contribution of junction ``j``
            to the anharmonicity of mode ``m``
        '''
        self._set_zeta(**kwargs)
        return [[j.anharmonicity(mode, **kwargs) for mode in range(len(self.zeta))] for j in self.junctions]
    
    @vectorize_kwargs
    def eigenfrequencies(self, **kwargs):
        '''Returns the normal mode frequencies of the circuit.

        Frequencies are provided in units of Hertz, 
        not in angular frequency.

        Parameters
        ----------
        kwargs:     
                    Values for un-specified circuit components, 
                    ex: ``L=1e-9``.

        Returns
        -------
        numpy.array
            Normal mode frequencies of the circuit, ordered from lowest
            to highest frequency, given in Hertz.

        Notes
        -----

        These eigen-frequencies :math:`f_m` correspond to the real parts
        of the complex frequencies which make the conductance matrix
        singular, or equivalently the real parts of the poles of the impedance
        calculated between the nodes of an inductor or josephson junction.

        The Hamiltonian of the circuit is

        :math:`\hat{H} = \sum_m hf_m\hat{a}_m^\dagger\hat{a}_m + \hat{U}`,

        where :math:`h` is Plancks constant, 
        :math:`\hat{a}_m` is the annihilation operator of the m-th
        normal mode of the circuit and :math:`f_m` is the frequency of 
        the m-th normal mode. The frequencies :math:`f_m` would
        be the resonance frequencies of the circuit if all junctions
        were replaced with linear inductors. In that case the 
        non-linear part of the Hamiltonian :math:`\hat{U}`, 
        originating in the junction non-linearity, would be 0.

        For more information on the underlying theory, see https://arxiv.org/pdf/1908.10342.pdf.
        '''
        self._set_zeta(**kwargs)
        return np.real(self.zeta)/2./pi
    
    @vectorize_kwargs
    def loss_rates(self, **kwargs):
        '''Returns the loss rates of the circuit normal modes.

        The array is ordered ordered with increasing normal mode frequencies
        such that the first element of the array corresponds to the loss
        rate of the lowest frequency mode. Losses are provided in units of Hertz, 
        **not in angular frequency**.

        Parameters
        ----------
        kwargs:     
                    Values for un-specified circuit components, 
                    ex: ``L=1e-9``.

        Returns
        -------
        numpy.array
            Normal mode losses of the circuit

        Notes
        -----

        These loss rates :math:`\kappa_m` correspond to twice the imaginary parts
        of the complex frequencies which make the conductance matrix
        singular, or equivalently twice the imaginary parts of the poles of the impedance
        calculated between the nodes of an inductor or josephon junction.

        For further details on the underlying theory, see https://arxiv.org/pdf/1908.10342.pdf.
        
        The dynamics of the circuit can be studied in QuTiP
        by considering collapse operators for the m-th mode 
        :math:`\sqrt{2\pi\kappa_m(n_{th,m}+1)}\hat{a}_m` and 
        :math:`\sqrt{2\pi\kappa_m(n_{th,m})}\hat{a}_m^\dagger`
        where :math:`n_{th,m}` is the average thermal occupation
        of mode :math:`m` and :math:`\hat{a}_m` is the annihilation operator of the m-th
        normal mode of the circuit.
        Note that dissipation rates that are obtained from this function
        have to be converted to angular frequencies through the factor :math:`2\pi`.
        If you are also using a hamiltonian generated from qucat, 
        then it too should be converted to angular frequencies by multiplying 
        the entire Hamiltonian by :math:`2\pi` when performing time-dependant 
        simulations.
        '''
        self._set_zeta(**kwargs)
        return 2*np.imag(self.zeta)/2./pi
    
    @vectorize_kwargs
    def anharmonicities(self, **kwargs):
        r'''Returns the anharmonicity of the circuit normal modes.

        The array is ordered ordered with increasing normal mode frequencies
        such that the first element of the array corresponds to the 
        anharmonicity of the lowest frequency mode. 
        Anharmonicities are provided in units of Hertz, 
        not in angular frequency.


        Parameters
        ----------
        kwargs:     
                    Values for un-specified circuit components, 
                    ex: ``L=1e-9``.

        Returns
        -------
        numpy.array
            Normal mode anharmonicities

        Notes
        -----
        The Hamiltonian of a circuit in first order perturbation theory is given by

        :math:`\hat{H} = \sum_m\sum_{n\ne m} (\hbar\omega_m-A_m-\frac{\chi_{mn}}{2})\hat{a}_m^\dagger\hat{a}_m -\frac{A_m}{2}\hat{a}_m^\dagger\hat{a}_m^\dagger\hat{a}_m\hat{a}_m -\chi_{mn}\hat{a}_m^\dagger\hat{a}_m\hat{a}_n^\dagger\hat{a}_n`,

        valid for weak anharmonicity :math:`\chi_{mn},A_m\ll \omega_m`.

        Here 

        * :math:`\omega_m` are the frequencies of the normal modes of the circuit where all junctions have been replaced with inductors characterized by their Josephson inductance
        
        * :math:`A_m` is the anharmonicity of mode :math:`m` , the difference in frequency of the first two transitions of the mode
        
        * :math:`\chi_{mn}` is the shift in mode :math:`m` that incurs if an excitation is created in mode :math:`n`

        This function returns the values of :math:`A_m`.

        For more information on the underlying theory, see https://arxiv.org/pdf/1908.10342.pdf.
        '''
        Ks = self.kerr(**kwargs)
        return np.array([Ks[i, i] for i in range(Ks.shape[0])])
    
    @vectorize_kwargs
    def kerr(self, **kwargs):
        r'''Returns the Kerr parameters for the circuit normal modes.

        The diagonal component ``K[m,m]`` of the returned matrix correspond to the
        anharmonicity (or self-Kerr) of mode ``m``.
        An off-diagonal component ``K[m,n]`` corresponds to the cross-Kerr coupling
        between modes ``m`` and ``n``.
        The modes are indexed with increasing normal mode frequencies, 
        for example ``K[0,1]`` corresponds to the cross-Kerr interaction
        between the lowest frequency mode and next highest frequency mode.
        Kerr parameters are provided in units of Hertz, 
        not in angular frequency.

        Parameters
        ----------
        kwargs:     
                    Values for un-specified circuit components, 
                    ex: ``L=1e-9``.

        Returns
        -------
        numpy.array of dimension 2
            Kerr parameters

        Notes
        -----
        The Hamiltonian of a circuit in first order perturbation theory is given by

        :math:`\hat{H} = \sum_m\sum_{n\ne m} (\hbar\omega_m-A_m-\frac{\chi_{mn}}{2})\hat{a}_m^\dagger\hat{a}_m -\frac{A_m}{2}\hat{a}_m^\dagger\hat{a}_m^\dagger\hat{a}_m\hat{a}_m -\chi_{mn}\hat{a}_m^\dagger\hat{a}_m\hat{a}_n^\dagger\hat{a}_n`,

        valid for weak anharmonicity :math:`\chi_{mn},A_m\ll \omega_m`.

        Here 

        * :math:`\omega_m` are the frequencies of the normal modes of the circuit where all junctions have been replaced with inductors characterized by their Josephson inductance
        
        * :math:`A_m` is the anharmonicity of mode :math:`m` , the difference in frequency of the first two transitions of the mode
        
        * :math:`\chi_{mn}` is the shift in mode :math:`m` that incurs if an excitation is created in mode :math:`n`

        This function returns the values of :math:`A_m` and :math:`\chi_{mn}` .

        For more information on the underlying theory, see https://arxiv.org/pdf/1908.10342.pdf.
        '''

        # Compute anharmonicity per junction ``As``
        # where ``As[j,m]`` corresponds to the contribution of junction ``j``
        # to the anharmonicity of mode ``m``
        As = self._anharmonicities_per_junction(**kwargs)

        # Number of modes in the circuit
        N_modes = len(self.zeta)

        # Number of junctions in the circuit
        N_junctions = len(self.junctions)

        # initialize the vector of Kerr coefficients
        Ks = np.zeros((N_modes, N_modes))

        for i in range(N_modes):
            for j in range(N_modes):
                for k in range(N_junctions):
                    if i == j:
                        # Add contribution to self-Kerr
                        Ks[i, i] += np.real(As[k][i])
                    else:
                        # Add contribution to cross-Kerr
                        # Note that taking the square root here is fine
                        # since Ks[i, j]~phi_ki^2*phi_kj^2 is necessarily a positive real
                        # since phi_ki,phi_kj are real numbers
                        Ks[i, j] += 2. * np.sqrt(As[k][i]*As[k][j])
        return Ks

    def f_k_A_chi(self, pretty_print=False, **kwargs):
        r'''Returns the eigenfrequency, loss-rates, anharmonicity, and Kerr parameters of the circuit. 

        Returns these quantities in the form ``[[f_0,f_1,..],[k_0,k_1,..],[A_0,A_1,..],[[A_0,chi_01,..],[chi_10,A_1,..]..]]``

        Each quantity is returned as a numpy arrays, 
        where each index corresponds to a normal mode, ordered with 
        increasing normal mode frequency.
        All quantities are provided in units of Hertz, 
        not in angular frequency.

        This method is equivalent to calling

        ``[_.eigenfrequencies(**kwargs),_.loss_rates(**kwargs), _.anharmonicities(**kwargs),_.kerr(**kwargs)]``

        For more details, refer to the functions

        :meth:`qucat.Qcircuit.eigenfrequencies`

        :meth:`qucat.Qcircuit.loss_rates`

        :meth:`qucat.Qcircuit.anharmonicities`

        :meth:`qucat.Qcircuit.kerr`

        Parameters
        ----------
        pretty_print:   Boolean, optional
                        If set to True, this method will print a summary
                        of the system parameters as a table.
        kwargs:     
                    Values for un-specified circuit components, 
                    ex: ``L=1e-9``.

        Returns
        -------
        List of numpy arrays
            ``[[f_0,f_1,..],[k_0,k_1,..],[A_0,A_1,..],[[A_0,chi_01,..],[chi_10,A_1,..]..]]``
        '''
        
        # Quantity to be returned: 
        # eigenfrequency, loss-rates, anharmonicity, and Kerr parameters of the circuit
        to_return = self.eigenfrequencies(**kwargs),\
            self.loss_rates(**kwargs),\
            self.anharmonicities(**kwargs),\
            self.kerr(**kwargs)


        if pretty_print:

            # Number of modes in the circuit
            N_modes = len(to_return[0])

            # Setup a template for the mode/frequency/dissipation/anharmonicity
            # table row in the form `` 7 spaces | 7 spaces |  7 spaces | 7 spaces |``
            table_line = ""
            for i in range(4):
                table_line += " %12s |"
            table_line += "\n"

            # Top row for content of columns
            to_print = table_line % (
                "mode", " freq. ", " diss. ", " anha. ")

            # add all the other rows (each row is a mode)
            for i, w in enumerate(to_return[0]):
                to_print += table_line % tuple([str(i)]+[pretty_value(
                    to_return[j][i], use_unicode=False)+'Hz' for j in range(3)])

            to_print += "\nKerr coefficients (diagonal = Kerr, off-diagonal = cross-Kerr)\n"
            
            # Setup template for the rows of the Kerr coefficients table row
            # in the form `` 7 spaces | 7 spaces | ...``
            table_line = ""
            for i in range(N_modes+1):
                table_line += " %12s |"
            table_line += "\n"

            # Top row indexing each column as a mode
            to_print += table_line % tuple(['mode'] +
                                            [str(i)+'   ' for i in range(N_modes)])

            # Add other rows
            for i in range(N_modes):
                line_elements = [str(i)]
                for j in range(N_modes):
                    if i >= j:
                        line_elements.append(pretty_value(
                            to_return[3][i][j], use_unicode=False)+'Hz')
                    else:
                        line_elements.append("")
                to_print += table_line % tuple(line_elements)

            # Print the two tables
            print(to_print)

        return to_return

    @refuse_vectorize_kwargs(exclude = ['modes','taylor','excitations','return_ops'])
    def hamiltonian(self, modes='all', taylor=4, excitations=6, return_ops = False, **kwargs):
        r'''Returns the circuits Hamiltonian for further analysis with QuTiP.
        The Hamiltonian is provided in units of frequency (not angular frequency), 
        such that :math:`h=1`.

        Parameters
        ----------
        modes:      array of integers, optional
                    List of modes to consider, where the modes are 
                    ordered with increasing frequency, such that
                    ``modes = [0,1]`` would lead to considering only
                    the two lowest frequency modes of the circuit.
                    By default all modes are considered.
        taylor:     integer, optional
                    Order to which the potential of all josephson
                    junctions should be taylor-expanded. Default
                    is `4`.
        excitations:integer or array of integers, optional  
                    Number of energy levels considered for each
                    junction. If one number is given, all modes 
                    have the same number of levels, if an array
                    is given, its length should match the number
                    of modes considered. For example if ``modes = [0,1]`` and
                    ``excitations = [5,10]``, then we will consider
                    5 excitation levels for mode 0 and 10 for mode 1.
        return_ops: Boolean, optional
                    If set to True, a list of the annihilation operators
                    will be returned along with the hamiltonian in the form
                    ``<Hamiltonian>, <list of operators>``. 
                    The form of the return is then ``H,[a_0,a_1,..]``
                    where ``a_i`` is the annihilation operator of the
                    i-th considered mode, a QuTiP Qobj
        kwargs:     
                    Values for un-specified circuit components, 
                    ex: ``L=1e-9``.

        Returns
        -------
        qutip.qobj
            Hamiltonian of the circuit
        
        Notes
        -----
        
        The Hamiltonian of the circuit, with the non-linearity of the Josephson junctions
        Taylor-expanded, is given in the limit of low dissipation by

        :math:`\hat{H} = \sum_{m\in\text{modes}} \hbar \omega_m\hat{a}_m^\dagger\hat{a}_m + \sum_j\sum_{2n\le\text{taylor}}E_j\frac{(-1)^{n+1}}{(2n)!}\left[\frac{\phi_{zpf,m,j}}{\phi_0}(\hat{a}_m^\dagger+\hat{a}_m)\right]^{2n}`,
        
        where :math:`\hat{a}_m` is the annihilation operator of the m-th
        normal mode of the circuit, :math:`\omega_m` is the frequency of 
        the m-th normal mode, :math:`E_j` is the Josephson energy of
        the j-th junction and :math:`\phi_0 = \hbar/2e` and :math:`\phi_{zpf,m,j}` 
        is the zero point fluctuation of mode 
        :math:`m` through junction :math:`j`.

        In the expression above, ``modes`` and ``taylor`` are arguments of the ``hamiltonian`` function.

        For more details on the underlying theory, see https://arxiv.org/pdf/1908.10342.pdf
        '''
        from qutip import destroy, qeye, tensor

        self.hamiltonian_modes = modes
        self.hamiltonian_taylor = taylor
        self.hamiltonian_excitations = excitations

        fs = self.eigenfrequencies(**kwargs)

        if modes == 'all':
            modes = range(len(fs))
        for m in modes:
            try:
                fs[m]
            except IndexError:
                error_message ="There are only %d modes in the circuit, and you specified mode index %d "%(len(fs),m)
                error_message +="corresponding to the %d-th mode."%(m+1)
                # error_message +="\nNote that the numer of modes may change as one sweeps a parameter"
                # error_message +=" for example if a 0 frequency, spurious mode becomes negative due to "
                # error_message +="numerical imprecision. Adding a resistance to the circuit may help with this."
                raise ValueError(error_message)

        if not isinstance(excitations,list):
            excitations = [int(excitations) for i in modes]
        else:
            if len(excitations)!=len(modes):
                raise ValueError("excitations and modes should have the same length")


        H = 0
        operators = []
        phi = [0 for junction in self.junctions]
        qeye_list = [qeye(n) for n in excitations]

        for index,mode in enumerate(modes):
            a_to_tensor = deepcopy(qeye_list)
            a_to_tensor[index] = destroy(excitations[index])
            a = tensor(a_to_tensor)
            operators.append(a)
            H += fs[mode]*a.dag()*a

            for j, junction in enumerate(self.junctions):
                # Note that zpf returns the flux in units of phi_0 = hbar/2./e
                phi[j] += np.real(junction.zpf(quantity='flux',mode=mode, **kwargs))*(a+a.dag()) 
                # a = x+iy => -i*(a-a^) = -i(iy+iy) = --1
                phi[j] += -1j*np.imag(junction.zpf(quantity='flux',mode=mode, **kwargs))*(a-a.dag()) 

        for j, junction in enumerate(self.junctions):
            n = 2
            EJ = (hbar/2./e)**2/(junction._get_value(**kwargs)*h)
            while 2*n <= taylor:
                H += (-1)**(n+1)*EJ/factorial(2*n)*phi[j]**(2*n)
                n += 1

        if return_ops:
            return H, operators
        return H

    @refuse_vectorize_kwargs(exclude = ['plot','return_fig_ax'])
    def show(self,
             plot=True,
             return_fig_ax=False,
             **kwargs):
        '''Plots the circuit.

        Only works if the circuit was created using the GUI.

        
        Parameters
        ----------
        plot:           Boolean, optional
                        If set to True (default), the function will call
                        plt.show() to display the circuit
        return_fig_ax:  Boolean, optional
                        If set to True (default is False), the function will 
                        return figure and axis for further processing using
                        matplotlib.
        '''
        pp = self._pp

        if isinstance(self,Network):
            #TODO recognize if the network is of series/parallel type
            # in which case the circuit can be constructed anyway
            raise TypeError('''
            Plotting functions not available if the circuit was not constructed
            using the GUI.
            ''')
        

        xs = []
        ys = []
        line_type = []
        for elt in self.netlist:
            x, y, lt = elt._draw()
            xs += x
            ys += y
            line_type += lt

        x_min = min([np.amin(x) for x in xs])
        x_max = max([np.amax(x) for x in xs])
        y_min = min([np.amin(x) for x in ys])
        y_max = max([np.amax(x) for x in ys])

        x_margin = pp['x_fig_margin']
        # ensures that any text labels are not cutoff
        y_margin = pp['y_fig_margin']
        fig = plt.figure(figsize=(
            ((x_max-x_min)+2.*x_margin)*pp["figsize_scaling"],
            ((y_max-y_min)+2.*y_margin)*pp["figsize_scaling"]))
        ax = fig.add_subplot(111)
        plt.subplots_adjust(left=0., right=1., top=1., bottom=0.)

        for i, _ in enumerate(xs):
            if line_type[i] == "node":
                ax.scatter(xs[i], ys[i], color=pp["color"], s=pp['node']['diameter'])
            else:
                ax.plot(xs[i], ys[i], color=pp["color"], lw=pp[line_type[i]]['lw'])

        for elt in self.netlist:
            elt._draw_label(ax)

        ax.set_axis_off()
        ax.set_xlim(x_min-x_margin, x_max+x_margin)
        ax.set_ylim(y_min-y_margin, y_max+y_margin)
        plt.margins(x=0., y=0.)

        if return_fig_ax:
            return fig, ax

        if plot:
            plt.show()

        plt.close()

    @refuse_vectorize_kwargs(exclude = ['quantity'])
    def show_normal_mode(self, 
        mode, 
        quantity='current',
        plot=True,
        return_fig_ax=False,
        add_title = True, 
        add_legend = True,
        **kwargs):
        r'''Plots a visual representation of a normal mode.

        Only works if the circuit was created using the GUI.
        Plots a schematic of the circuit overlayed with 
        arrows representing the complex amplitude of a certain quantity 
        :math:`X` which can be flux, current, charge or voltage.

        More specifically, the complex amplitude of :math:`X` if a 
        single-photon amplitude coherent state were populating a given mode ``mode``.

        Current is shown in units of Ampere, voltage in Volts, 
        charge in electron charge, and flux in units of the
        reduced flux quantum 
        (defined as :math:`\hbar/2e`)

        The direction of the arrows show what we are defining 
        as positive current for that component.

        Parameters
        ----------
        mode:           integer
                        Determine what mode to plot, where 0 designates
                        the lowest frequency mode, and the others
                        are arranged in order of increasing frequency
        quantity:           string
                        One of 'current' (default), 'flux','charge','voltage'
                        Determines what quantity the arrows should represent.
        plot:           Boolean, optional
                        If set to True (default), the function will call
                        plt.show() to display the circuit
        return_fig_ax:  Boolean, optional
                        If set to True (default is False), the function will 
                        return figure and axis for further processing using
                        matplotlib.
        add_title:      Boolean, optional
                        If set to True (default), the function will 
                        add a title detailing the modes frequency, anharmonicity
                        and dissipation rate
        add_legend:     Boolean, optional
                        If set to True (default), the function will 
                        add a legend detailing the definition of 
                        arrow size and arrow direction

        Notes
        -----

        This annotated quantity, called a phasor, is calculated by multiplying the
        voltage transfer function :math:`T_{rc}` (between a reference component :math:`r`
        and the annotated component  :math:`c` ), with
        :math:`X_{zpf,m,r}`, the zero-point fluctuations of :math:`\hat{X}` at the reference component.
        
        Note that resistors make the transfer function :math:`T_{rc}`, and hence the phasors complex.

        Since this is plotted for a single-photon amplitude coherent state, the absolute value
        of the annotation is equal to the
        contribution of a mode to the zero-point fluctuations accross this component.

        For more detail on the underlying theory, see https://arxiv.org/pdf/1908.10342.pdf.
        '''

        # This changes the default plotting settings 
        # to those defined in plotting_settings.py
        # under plotting_parameters_normal_modes
        self._plotting_normal_mode = True

        # This will set pp to plotting_parameters_normal_modes
        # (see the definition of the Qcircuit._pp propoerty function)
        pp = self._pp

        # Make sure this has been called on a 
        # Qcircuit defined with the GUI
        if isinstance(self,Network):
            raise TypeError('''
            Plotting functions not available if the circuit was not constructed
            using the GUI.
            ''')

        def pretty(v, quantity):
            # Utility function to print a pretty 
            # value for the phasor
            if quantity == 'flux':
                return pretty_value(v, is_complex = True)+u"\u03A6_0"
            elif quantity == 'charge':
                return pretty_value(v, is_complex = True, use_power_10=True)+'e'
            elif quantity == 'voltage':
                return pretty_value(v, is_complex = True)+'V'
            elif quantity == 'current':
                return pretty_value(v, is_complex = True)+'A'

        # Plot the circuit and return the 
        # figure and axis for further 
        # editing below
        fig, ax = self.show(
            plot=False,
            return_fig_ax=True)

        # Determine smallest and largest arrow size
        # Based on the absolute value of the
        # phasor through all components
        all_values = []
        for el in self.netlist:
            if not isinstance(el,W):
                all_values.append(el.zpf(mode = mode, quantity = quantity, **kwargs))
        all_values = np.absolute(all_values)
        max_value = np.amax(all_values)
        min_value = np.amin(all_values)

        def value_to_01_range(value):
            # Returns a number between 0 and 1
            # where 0 corresponds to the smallest
            # phasor and 1 to the largest

            if pretty(np.absolute(max_value), quantity) == pretty(np.absolute(min_value), quantity):
                # Case where all the components have
                # the same phasor magnitude
                return 1.
            else:
                return (np.absolute(value)-min_value)/(max_value-min_value)

        def arrow_width(value=None,value_01 = None):
            # Converts value between 0 and 1
            # to an arrow width where 0 will
            # get the ``min_width`` and
            # 1 will get the ``max_width```

            if value_01 is None:
                value_01 = value_to_01_range(value)

            # part of the plotting parameters
            # which concern the arrow
            ppnm = pp['normal_mode_arrow']

            return np.absolute(ppnm['min_width']+value_01*(ppnm['max_width']-ppnm['min_width']))

        def arrow_kwargs(value=None,value_01 = None):
            # Constructs the keyword arguments to be passed 
            # in the construction of an arrow based on the 
            # zpf value

            if value_01 is None:
                value_01 = value_to_01_range(value)

            # part of the plotting parameters
            # which concern the arrow
            ppnm = pp['normal_mode_arrow']

            # linewidth
            lw = ppnm['min_lw']+value_01*(ppnm['max_lw']-ppnm['min_lw'])

            # head size
            head = ppnm['min_head']+value_01 * \
                (ppnm['max_head']-ppnm['min_head'])

            return {'lw': lw,
                    'head_width': head,
                    'head_length': head,
                    'clip_on': False}

        # For each element in the circuit, if it 
        # isn't a ground, add an arrow and a label
        for el in self.netlist:
            if not isinstance(el,W):

                # phasor for the quantity and for the current
                value = el.zpf(mode = mode, quantity = quantity, **kwargs)

                # location of the element center
                x = el.x_plot_center
                y = el.y_plot_center

                if el.angle==EAST or el.angle==WEST:
                    # Case of horizontal element

                    # Text position
                    x_text = x+pp["normal_mode_label"]["text_position_horizontal"][0]
                    y_text = y+pp["normal_mode_label"]["text_position_horizontal"][1]

                    # text alignment
                    ha = 'center'
                    va = 'top'

                    # Arrow position in y
                    y_arrow = y+pp["normal_mode_label"]["y_arrow"]
                    dy_arrow = 0.

                    # Arrow position in x
                    if el.angle == EAST:
                        # Define the direction for positive values
                        # and the positive node on the east
                        x_arrow = x-arrow_width(value)/2.
                        dx_arrow = arrow_width(value)
                    elif el.angle == WEST:
                        # Define the direction for positive values
                        # and the positive node on the west
                        x_arrow = x+arrow_width(value)/2.
                        dx_arrow = -arrow_width(value)

                if el.angle==NORTH or el.angle==SOUTH:
                    # Case of vertical element

                    # Text position
                    x_text = x+pp["normal_mode_label"]["text_position_vertical"][0]
                    y_text = y+pp["normal_mode_label"]["text_position_vertical"][1]

                    # Text alignment
                    ha = 'right'
                    va = 'center'

                    # Arrow x position
                    x_arrow = x-pp["normal_mode_label"]["y_arrow"]
                    dx_arrow = 0.
                    
                    
                    # Arrow position in y
                    if el.angle==NORTH:
                        # Define the direction for positive values
                        # and the positive node on the north
                        y_arrow = y-arrow_width(value)/2.
                        dy_arrow = arrow_width(value)
                    elif el.angle==SOUTH:
                        # Define the direction for positive values
                        # and the positive node on the south
                        y_arrow = y+arrow_width(value)/2.
                        dy_arrow = -arrow_width(value)


                # Add the arrow
                if np.real(value)+np.imag(value)<0:
                    # If the dominating part of the complex number is negative
                    # Flip the arrow and the value
                    arrow_coords = [x_arrow+dx_arrow, y_arrow+dy_arrow, -dx_arrow, -dy_arrow]
                    value = -value
                else:
                    arrow_coords = [x_arrow, y_arrow, dx_arrow, dy_arrow]
                
                ax.arrow(*arrow_coords,
                        fc=pp['normal_mode_arrow']['color'],
                        ec=pp['normal_mode_arrow']['color'],
                        **arrow_kwargs(value))

                # Add the annotation
                ax.text(x_text, y_text,
                        pretty(value, quantity),
                        fontsize=pp["normal_mode_label"]["fontsize"],
                        ha=ha, va=va, weight='normal',color =pp["normal_mode_label"]["color"] )

        # Add the title
        if add_title:
            w,k,A,chi = self.f_k_A_chi(**kwargs)
            ax.annotate(r'Mode %d, f=%sHz, k=%sHz, A=%sHz,'%
                (mode,
                pretty_value(w[mode]),
                pretty_value(k[mode]),
                pretty_value(A[mode])),
                xy=(0.05, 0.97),
                horizontalalignment='left',
                verticalalignment='top',
                xycoords='axes fraction',
                fontsize=12, 
                weight='bold')
                
            ax.annotate('populated by single-photon amplitude coherent state',
                xy=(0.05, 0.97-0.045),
                horizontalalignment='left',
                verticalalignment='top',
                xycoords='axes fraction',
                fontsize=12)

        if add_legend:
            if quantity == 'current':
                value_text= "|I|"
            elif quantity == 'voltage':
                value_text= u"|V|"
            if quantity == 'flux':
                value_text= u"|\u03A6|"
            elif quantity == 'charge':
                value_text= "|Q|"
            value_text += u"exp(i\u03B8)"
        
            x_legend = ax.get_xlim()[0]+0.4
            y_legend = ax.get_ylim()[0]+0.25

            legend_text_kwargs = {
                'ha':'center',
                'va':'center',
                'fontsize':12, 
                'weight':'normal'
            }
            
            ax.text(x_legend, y_legend,
                value_text,
                **legend_text_kwargs)

            v01 = 0.7
            ax.arrow(x_legend-arrow_width(value_01 = v01)/2, 
                    y_legend-0.15,
                    arrow_width(value_01 = v01), 0,
                    fc=pp['normal_mode_arrow']['color'],
                    ec=pp['normal_mode_arrow']['color'], 
                    **arrow_kwargs(value_01 =v01))
       

        if plot == True:
            plt.show()
        plt.close()
        self._plotting_normal_mode = False

        if return_fig_ax:
            return fig, ax

class Network(Qcircuit):
    r'''Constructs a Qcircuit object from a list of components without resorting to a graphical user interface.

    The list can be composed of instances of the :class:`qucat.L`, :class:`qucat.C`, 
    :class:`qucat.R` or :class:`qucat.J` classes
    for inductors, capacitors, resistors or junctions respectively.

    This Qcircuit construction method offers the advantage of programmatically constructing
    the circuit of the GUI class.
    On could, for example, construct an array of LC-resonators using a python ``for`` loop, which
    would be tedious using a graphical user interface.
    The disadvantage is that one cannot use the plotting tools :meth:`show` or 
    :meth:`show_normal_modes` to visualize the circuit or its innerworkings.

    Parameters
    ----------
    netlist:    list of :class:`qucat.Component`
                See examples
                
    Returns
    -------
    qucat.Qcircuit
        A Qcircuit object, see qucat.Qcircuit

    Examples
    --------
    Here we construct a parallel combination of a capacitor, inductor and junction, grounded
    on one end and connected at the other end through a capacitor to a 50 Ohm resistor to ground.

    .. image:: Network_example_circuit.png

    Import the Network class, and the components we will need

    >>> from qucat import Network, R,L,C,J

    Note that the components (R,L,C,J) accept node indexes as their two first arguments, 
    here we will use the node ``0`` to designate ground. The last arguments should be 
    a label (``str``) or a value (``float``) or both, the order in which these
    arguments are provided are unimportant.

    >>> circuit = Network([
    ... L(0,1,'L',1e-9), # Add the inductor between ground and node 1
    ... C(0,1,100e-15,'C'), # Add the capacitor
    ... J(0,1,'L_J'), # Add the junction
    ... C(1,2,1e-15), # Add a capacitor which will connect to a resistor
    ... R(2,0,50) # Add a 50 Ohm resistance to ground
    ... ])

    The junction was parametrized only by a string ``L_J`` , 
    this is the best way to proceed if one wants to sweep the value of a 
    component. Indeed, the most computationally expensive part of the 
    analysis is performed upon initializing the Network, subsequently
    changing the value of a component and re-calculating a quantity 
    such as the frequency or anharmonicity can be performed much faster.

    For example, we can compute the eigenfrequency, loss-rates, anharmonicity, and Kerr parameters of the circuit
    for a specific junction inductance.

    >>> circuit.f_k_A_chi(L_J = 1e-9) 

    '''

    def __init__(self, netlist):
        super(Network, self).__init__(netlist)

class GUI(Qcircuit):
    r'''Opens a graphical user interface to constructs a circuit.

    Parameters
    ----------
    filename:       string
                    Path to a file which will store all the information
                    about the graphically constructed circuit.
    edit:           Boolean
                    If True (default), the graphical user interface will be opened.
                    One can set this argument to False to import the circuit without opening
                    the graphical user interface
    plot:           Boolean
                    If True (default), the circuit will be plotted using matplotlib.
    print_network:  Boolean
                    If True (default), a text description of the constructed
                    network will be printed.
            
    Returns
    -------
    qucat.Qcircuit
        A Qcircuit object, see qucat.Qcircuit

    Notes
    -----

    All the necessary information about the circuit generated by the graphical user interface application
    is stored in a human-readable format at the specified path.
    
    Each line of this text file is in the format:

    ``type`` ; ``x_minus`` , ``y_minus`` ; ``x_plus`` , ``y_plus`` ; ``value`` ; ``label``

    and represents a circuit component, wire or ground element.

    ``type`` can take the values ``L``, ``C``, ``R``, ``J``, ``W`` or ``G`` for 
    inductor, capacitor, resistor, junction, wire or ground respectively.

    ``value`` will be a float representing the value of the component or will be empty
    
    ``label`` will be a string corresponding to the label of the component or will be empty

    ``x/y_minus`` (``x/y_plus``) represents the horizontal/vertical location of the minus (plus) node of the component.
    Negative value are allowed and components have a length of 1 unit.
    
    For example, the circuit below, is described by the following text file

    ::

        L;3,-10;3,-11;1.000000e-09;L
        C;4,-10;4,-11;1.000000e-13;C
        J;5,-10;5,-11;;L_J
        C;5,-12;6,-12;1.000000e-15;
        R;7,-11;7,-12;5.000000e+01;
        G;7,-10;7,-11;;


    .. image:: Network_example_circuit.png
    

    '''

    def __init__(self, filename, edit=True, plot=True, print_network=False,_unittesting=False):

        # Note: this will also give a valid path if filename was specified using 
        # an absolute path
        filename = os.path.join(os.getcwd(),filename)

        try:
            with open(filename, 'r') as f:
                pass
        except FileNotFoundError:
            # if file does not exist force the gui to open
            edit = True
            # and create the folder 
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            # ... and file
            with open(filename, "w") as f:
                pass
        print("绘制等效电路图...")
        if edit:
            run([sys.executable,
                os.path.join(os.path.dirname(__file__),"_gui.py"),
                filename])
        # print("Calculate equivalent circuit component parameters...")
        # netlist = []
        # with open(filename, 'r') as f:
        #     for el in f:
        #         el = el.replace('\n', '')
        #         el = el.split(";")
        #         if el[3] == '':
        #             v = None
        #         else:
        #             v = float(el[3])
        #         if el[4] == '':
        #             l = None
        #         else:
        #             l = el[4]
        #         netlist.append(
        #             string_to_component(el[0], el[1], el[2], v, l))
        
        # super(GUI, self).__init__(netlist)
        # for el in self.netlist:
        #     el._set_plot_coordinates()
        
        # if plot:
        #     self.show()

        # if print_network:
        #     for el in [el for el in self.netlist if not isinstance(el,W)]:
        #         print("%s %d %d %s"%(
        #             el.__class__.__name__,
        #             min(el.node_minus,el.node_plus),
        #             max(el.node_minus,el.node_plus),
        #             el._to_string(use_unicode = False)))
        #     print('\n')

class _Network(object):
    """
    The _Network class parses network arrays generated by the GUI
    or written manually by the user. 
    It allows the computation of the R, L and C matrices, the
    admittance Y of the network between
    two nodes as well as the voltage transfer function of the network
    between two ports (4 nodes).

    Parameters
    ----------
    netlist : list
        list of Component objects
    """

    @timeit
    def __init__(self, netlist):

        self.netlist = netlist
        self.parse_netlist()
        # if len(self.net_dict) == 0:
        #     raise ValueError("There are no components in the circuit")
        # if not self.is_connected():
        #     raise ValueError("There are two sub-circuits which are not connected")
        # if self.has_shorts():
        #     raise ValueError("Your circuit appears to be open or shorted making the analysis impossible")
        # if self.has_opens():
        #     raise ValueError("Your circuit appears to be open or shorted making the analysis impossible")

    @timeit
    def is_connected(self, 
        nodes_encountered = None, 
        start_node = None):
        '''
        Determines if a nework is connected (graph theory term).
        
        Starting at "start_node", 
        the algorithm will go from neighbouring node
        to neighbouring node, adding all encountered
        nodes to the encountered_nodes list. 
        
        At then end we check if
        all the nodes of the network were encountered
        by checking the length of this list with respect
        to the total number of nodes
        '''

        encountered_nodes = []
        start_node = list(self.net_dict)[0] # Starting point of the algo
        

        def add_neighboors_to_encountered_nodes(node):
            if node not in encountered_nodes:
                encountered_nodes.append(node)
                for neighboor in self.net_dict[node]:
                    add_neighboors_to_encountered_nodes(neighboor)

        add_neighboors_to_encountered_nodes(start_node)

        if len(encountered_nodes) != len(self.net_dict):
            return False
        else:
            return True

    def has_shorts(self):
        '''
        Determines if there is an short circuit. 

        For each node, we construct the network where
        that node has been removed. 

        If the removal of that node leads to two distinct, 
        non-connected circuits, then that node was a point 
        at which the circuit was being shorted.
        '''
        for node_to_remove in range(len(self.net_dict)):
            # create a copy of the network
            partial_network = deepcopy(self)

            # remove the node_to_remove from the network
            for other_node in partial_network.net_dict[node_to_remove]:
                del partial_network.net_dict[other_node][node_to_remove]
            del partial_network.net_dict[node_to_remove]
            
            # check if that network is connected
            if not partial_network.is_connected():
                return True

        # No shorts were found
        return False
        
    def has_opens(self):
        '''
        Determines if there is an open connection in the 
        circuit. 

        If there are only two nodes in the circuit, it cannot be open. 
        This is because through another check we are imposing that the circuit has at least
        two types of components, one inductive, one capacitive.
        So a two node circuit will at minimum be an LC or JC circuit.

        If there are more than two nodes, and one of the nodes is connected 
        to only one other, the circuit is open.
        '''
        for _, connections in self.net_dict.items():
            if len(connections) == 1 and len(self.net_dict)>2:
                return True
        return False

    def parse_netlist(self):

        def merge_chains(chains, i, j):
            '''Merges two chains (two arrays)'''
            to_add = chains[j]
            del chains[j]
            chains[i] = chains[i]+to_add
            return chains

        # ``chains``` is a list of node-lists (node-list = a chain)
        # each chain lists nodes which are connected one to another
        # either through wires or through ground
        chains = []

        # We start by grouping all nodes which are connected by wires 
        # into chains of nodes indexed by a integer which is to become 
        # the new node names  for future calculations
        for el in self.netlist:

            # Go through all the wires (note: grounds are instances of wires)
            if isinstance(el,W):
                
                # If this element is a ground, call it's negative node '__ground'
                np = el.node_plus
                if type(el) is G:
                    nm = '__ground'
                else:
                    nm = el.node_minus

                # added tells us if both nodes have already 
                # been added to a same chain
                added = False

                # go through all chains to see if it
                # contains the nodes of this wire
                for i, ch in enumerate(chains):

                    # If both node of the wire have already been 
                    # added to a same chain, don't do anyting
                    if (nm in ch) and (np in ch):
                        added = True

                    # If minus node was added to chain 'ch'...
                    elif (nm in ch):
                        for j, ch2 in enumerate(chains):
                            # ...and plus node to chain 'ch2'
                            if np in ch2:
                                # merge the two chains
                                chains = merge_chains(chains, i, j)
                                added = True
                        if added == False:
                            # otherwise add plus node to chain 'ch'
                            ch.append(np)
                            added = True
                    
                    # same check for the plus node
                    elif (np in ch):
                        for j, ch2 in enumerate(chains):
                            if nm in ch2:
                                chains = merge_chains(chains, i, j)
                                added = True
                        if added == False:
                            ch.append(nm)
                            added = True
                
                # if none of the nodes were present in chains, 
                # create a new chain linking the two nodes of the wire
                if added == False:
                    chains.append([nm, np])

        def plot_node_to_new_node(plot_node):
            '''
            Transforms the node ``plot_node``` to a new node.

            Parameters
            ----------
            plot_node:  typically a string or an integer, but could be any
                        hashable object
                        For GUI generated networks, 
                        this is a string 'x,y' that determines the position
                        of the node when plotting it.

            Returns
            -------
            i:          integer, a unique number corresponding to all nodes
                        connected via a wire or ground.
                        ``i`` is one of [0,..,N-1] where N is the number of 
                        nodes in the circuit stripped of all wires.
        
            '''
            i = 0
            # if plot_node is already in a chain, 
            # return the index of that chain in ``chains``
            for ch in chains:
                if plot_node in ch:
                    return i
                i+=1

            # other wise append ``chains`` and 
            # return the the last index of ``chains``
            chains.append([plot_node])
            return i

        # replace plotting nodes with new nodes
        # for all non-wire elements
        # and make a list of all nodes
        self.nodes = []
        for el in self.netlist:
            el._node_minus_plot = el.node_minus
            el._node_plus_plot = el.node_plus
            if not isinstance(el,W):
                el.node_minus = plot_node_to_new_node(el.node_minus)
                el.node_plus = plot_node_to_new_node(el.node_plus)
                if el.node_minus == el.node_plus:
                    raise ValueError("Your circuit appears to be shorted, making the analysis impossible")
                for n in [el.node_minus, el.node_plus]:
                    if n not in self.nodes:
                        self.nodes.append(n)

        
        # build ``net_dict``, a dictionary such that  
        # ``net_dict[node_A][node_B]`` gives the non-wire circuit 
        # component connecting ``node_A`` and ``node_B``.
        # If ``node_A`` and ``node_B`` are not connected, 
        # calling ``net_dict[node_A][node_B]`` will raise a KeyError
        self.net_dict = {}
        for n in self.nodes:
            self.net_dict[n] = {}
        for el in self.netlist:
            if not isinstance(el,W):
                self.connect(el, el.node_minus, el.node_plus)

    @timeit
    def compute_char_poly_coeffs(self, is_lossy = True):
        
        @timeit
        def determinant(matrix):
            return matrix.berkowitz_det()

        self.is_lossy = is_lossy
        ntr = deepcopy(self) # ntr stands for Network To Reduce

        # compute conductance matrix
        ntr.compute_RLC_matrices()

        if self.is_lossy:
            w = sp.Symbol('w')
            char_poly = determinant((ntr.RLC_matrices['L']+1j*w*ntr.RLC_matrices['R']-w**2*ntr.RLC_matrices['C']))
            char_poly = sp.collect(sp.expand(char_poly), w)
            self.char_poly_order = sp.polys.polytools.degree(
                char_poly, gen=w)  # Order of the polynomial
            # Get polynomial coefficients, index 0 = lowest order term
            self.char_poly_coeffs_analytical =\
                [char_poly.coeff(w, n) for n in range(self.char_poly_order+1)] 
        else:
            w2 = sp.Symbol('w2')
            char_poly = determinant((-ntr.RLC_matrices['L']+w2*ntr.RLC_matrices['C']))
            char_poly = sp.collect(sp.expand(char_poly), w2)
            self.char_poly_order = sp.polys.polytools.degree(char_poly, gen=w2)  # Order of the polynomial
            # Get polynomial coefficients, index 0 = lowest order term
            self.char_poly_coeffs_analytical =\
                [char_poly.coeff(w2, n) for n in range(self.char_poly_order+1)]  
                
        
        # Divide by w if possible
        n=0
        while self.char_poly_coeffs_analytical[n]==0:
            n+=1
        self.char_poly_coeffs_analytical = self.char_poly_coeffs_analytical[n:]

        return self.char_poly_coeffs_analytical

    def compute_RLC_matrices(self):
        N_nodes = len(self.net_dict)
        self.RLC_matrices = {
            'R':sp.zeros(N_nodes),
            'L':sp.zeros(N_nodes),
            'C':sp.zeros(N_nodes)
        }

        for i in range(N_nodes):
            for j, el in self.net_dict[i].items():
                if j>i:
                    RLC_matrix_components = el._get_RLC_matrix_components()
                    for k in self.RLC_matrices:
                        self.RLC_matrices[k][i,j] = -RLC_matrix_components[k]
                        self.RLC_matrices[k][j,i] = -RLC_matrix_components[k]
                        self.RLC_matrices[k][i,i] += RLC_matrix_components[k]
                        self.RLC_matrices[k][j,j] += RLC_matrix_components[k]

        # count the number of coefficients in each row
        number_coefficients = np.zeros((N_nodes))
        for k in self.RLC_matrices:
            for i in range(N_nodes):
                for j in range(N_nodes):
                    if self.RLC_matrices[k][i,j] != 0:
                        number_coefficients[i]+=1


        # set a ground 
        ground_node = np.argmax(number_coefficients)
        for k in self.RLC_matrices:
            self.RLC_matrices[k].row_del(ground_node)
            self.RLC_matrices[k].col_del(ground_node)

    def connect(self, element, node_minus, node_plus):
        '''
        Modifies the ``net_dict`` variable such that ``node_minus``
        and ``node_plus`` are marked as connected in future calculations.
        ``net_dict`` is a dictionary such that  
        ``net_dict[node_A][node_B]`` gives the non-wire circuit 
        component connecting ``node_A`` and ``node_B``.
        If ``node_A`` and ``node_B`` are not connected, 
        calling ``net_dict[node_A][node_B]`` will raise a KeyError

        Parameters
        ----------
        element:    a ``Circuit`` object which is not a Wire or a Ground
        node_minus: integer
                    negative node of the element
        node_plus: integer
                    positive node of the element        
        '''

        # Connect node minus to node plus
        try:
            # If the nodes are already connected, add this element in parallel 
            self.net_dict[node_minus][node_plus] = self.net_dict[node_minus][node_plus] | element
        except KeyError:
            # Case where the nodes are not connected
            self.net_dict[node_minus][node_plus] = element

        # Connect node plus to node minus
        try:
            self.net_dict[node_plus][node_minus] = self.net_dict[node_plus][node_minus] | element
        except KeyError:
            self.net_dict[node_plus][node_minus] = element

    def remove_node(self, node_to_remove):
        '''
        Makes use of the star-mesh transform to remove the ``node_to_remove`` from the network.
        A node N=``node_to_remove`` connected to nodes A,B,C,.. through impedances 
        Z_A,Z_B,... (the star) can be eliminated 
        if we interconnect nodes A,B,C,.. with impedances Z_{AB},Z_{AC},Z_{BC},...
        given by Z_{XY} = Z_XZ_Y\sum_M1/Z_M. 
        The resulting network is called the mesh.

        Parameters
        ----------
        node: integer, node to be removed of the network stored in ``net_dict`` 
        '''

        # List of (connecting_nodes, connecting_components) connecting the 
        # node_to_remove to (nearest neighbour) connecting_nodes
        connections = [x for x in self.net_dict[node_to_remove].items()]

        # Sum of admittances of connecting_components
        sum_Y = sum([elt._admittance() for _, elt in connections])

        # Go through all pairs of connecting nodes
        # and calculate the admittance Y_XY that will connect them 
        # in the mesh
        mesh_to_add = []
        for i, (node_A, elt_A) in enumerate(connections):
            for node_B, elt_B in connections[i+1:]:
                Y = elt_A._admittance()*elt_B._admittance()/sum_Y
                mesh_to_add.append([Admittance(node_A, node_B, Y), node_A, node_B])

        # Remove the node_to_remove from the net_dict, along with all
        # the connecting components
        for other_node in self.net_dict[node_to_remove]:
            del self.net_dict[other_node][node_to_remove]
        del self.net_dict[node_to_remove]

        # Add admittances Y_XY connecting nodes X,Y directly adjascent to 
        # the removed node
        for mesh_branch in mesh_to_add:
            self.connect(*mesh_branch)

    @timeit
    def admittance(self, node_minus, node_plus):
        '''
        Compute the admittance of the network between two nodes 
        ``node_plus`` and ``node_minus`` 
        by removing all other nodes through star-mesh transformations.

        Parameters
        ----------
        node_minus: integer 
        node_plus: integer
        '''
        if node_minus == node_plus:
            raise ValueError('node_minus == node_plus')

        # Create a temporary copy of the network which will be reduced
        ntr = deepcopy(self) # ntr stands for Network To Reduce

        # # order nodes from the node with the least amount of connections
        # # to the one with the most
        nodes = [key for key in ntr.net_dict]
        nodes_order = np.argsort([len(ntr.net_dict[key]) for key in nodes])
        nodes_sorted = [nodes[i] for i in nodes_order]
        
        # Remove all nodes except from node_minus, node_plus
        # through star-mesh transforms with the remove_node function
        for node in nodes_sorted:
            if node not in [node_minus, node_plus]:
                ntr.remove_node(node)

        # Compute the admittance between the two remaining nodes: 
        # node_minus and node_plus
        Y = ntr.net_dict[node_minus][node_plus]._admittance()
        return Y

    def branch_admittance(self, node_1, node_2):
        '''
        Returns the admittance in the branch connecting ``node_1`` and ``node_2``.
        If they are not directly connected through a single Component, this function
        returns 0 (i.e. the admittnce of an open circuit).
        This function is written to avoid calling try/except clauses repetitivly
        to verify if ``self.net_dict[node_1][node_2]`` is an existing key

        Parameters
        ----------
        node_1: integer 
        node_2: integer
        '''
        if node_1 == node_2:
            raise ValueError('node_1 == node_2')

        try:
            return self.net_dict[node_1][node_2]._admittance()
        except KeyError:
            return 0.

    def transfer(self, node_left_minus, node_left_plus, node_right_minus, node_right_plus):
        '''
        Returns the transfer function V_right/V_left relating the voltage on 
        a port 'right' defined by ``node_right_minus`` and ``node_right_plus``
        and a port 'left' defined by ``node_left_minus`` and ``node_left_plus``
        We proceed by constructing an ABCD matrix and returning V_right/V_left = 1/A

        Parameters
        ----------
        node_left_minus: integer 
        node_left_plus: integer
        node_right_minus: integer
        node_right_plus: integer
        '''

        if node_left_minus == node_left_plus:
            raise ValueError('node_left_minus == node_left_plus')
        elif node_right_minus == node_right_plus:
            raise ValueError('node_right_minus == node_right_plus')

        # Case where the left an right port are identical
        if (node_left_minus == node_right_minus)\
            and (node_left_plus == node_right_plus):
            return 1.

        # Case where the left an right port are identical, but inverted
        elif (node_left_plus == node_right_minus)\
            and (node_left_minus == node_right_plus):
            return -1.

        # If the ports are not identical, reduce the network such that only
        # the nodes provided as arguments remain

        # Create a temporary copy of the network which will be reduced        
        ntr = deepcopy(self) # ntr stands for Network To Reduce
        
        # # order nodes from the node with the least amount of connections
        # # to the one with the most
        nodes = [key for key in ntr.net_dict]
        nodes_order = np.argsort([len(ntr.net_dict[key]) for key in nodes])
        nodes_sorted = [nodes[i] for i in nodes_order]

        # Remove nodes using the star-mesh relation
        for node in nodes_sorted:
            if node not in [node_left_minus, node_left_plus, node_right_minus, node_right_plus]:
                ntr.remove_node(node)

        if (node_left_minus in [node_right_plus, node_right_minus]) or\
            (node_left_plus in [node_right_plus, node_right_minus]):

        # Case where there are two of the nodes provided as arguments 
        # are identical. 
        # The circuit has then three distinct nodes connected by
        # three components.
        # For this case, the ABCD matrix can be constructed following 
        # the before last case of Table 4.1 in Microwave Engineering (Pozar)
        # Indeed, all these cases are equivelant to the network below:
        #
        #  p1   --------- Y_3 ---------- p2 
        #           |               |
        #          Y_1             Y_2
        #           |               |
        #  gr   ------------------------ gr
        # Note that the transfer function is independant of Y_1, this in essence 
        # a voltage divider (see https://en.wikipedia.org/wiki/Voltage_divider)
        # where the voltage at p2 is entirely determined by Y_2,Y_3 and the voltage at p1


            if node_left_minus == node_right_minus:
                p1 = node_left_plus
                p2 = node_right_plus
                gr = node_left_minus #= node_right_minus
                # Y_1 = ntr.branch_admittance(p1,gr)
                Y_2 = ntr.branch_admittance(p2,gr)
                Y_3 = ntr.branch_admittance(p1,p2)

                # A component of the ABCD matrix
                A = 1+Y_2/Y_3 # node Y_3 cannot be 0 in theory
                return 1/A

            elif node_left_plus == node_right_plus:
                # Ports 1 and 2 are the wrong way round, minuses cancel out
                p1 = node_left_minus
                p2 = node_right_minus
                gr = node_left_plus #= node_right_plus

                # Y_1 = ntr.branch_admittance(p1,gr)
                Y_2 = ntr.branch_admittance(p2,gr)
                Y_3 = ntr.branch_admittance(p1,p2)

                # A component of the ABCD matrix
                A = 1+Y_2/Y_3 # node Y_3 cannot be 0 in theory
                return 1/A

            elif node_left_minus == node_right_plus:
                # Port 2 is the wrong way round, transfer function gets a minus
                p1 = node_left_plus
                p2 = node_right_minus
                gr = node_left_minus #= node_right_plus
                # Y_1 = ntr.branch_admittance(p1,gr)
                Y_2 = ntr.branch_admittance(p2,gr)
                Y_3 = ntr.branch_admittance(p1,p2)

                # A component of the ABCD matrix
                A = 1+Y_2/Y_3 # node Y_3 cannot be 0 in theory
                return -1/A

            elif node_left_plus == node_right_minus:
                # Port 2 is the wrong way round, transfer function gets a minus
                p1 = node_left_minus
                p2 = node_right_plus
                gr = node_left_plus #= node_right_minus
                # Y_1 = ntr.branch_admittance(p1,gr)
                Y_2 = ntr.branch_admittance(p2,gr)
                Y_3 = ntr.branch_admittance(p1,p2)

                # A component of the ABCD matrix
                A = 1+Y_2/Y_3 # node Y_3 cannot be 0 in theory
                return -1/A

        else:
            # Most complex case (discussed in the paper)
            # First, compute the impence matrix of the lattice network following notations in 
            # https://www.globalspec.com/reference/71734/203279/10-11-lattice-networks
            # excerpt of Network Analysis & Circuit (By M. Arshad) section 10.11: LATTICE NETWORKS
            Ya = ntr.branch_admittance(node_left_plus, node_right_plus)
            Yb = ntr.branch_admittance(node_left_minus, node_right_plus)
            Yc = ntr.branch_admittance(node_left_plus, node_right_minus)
            Yd = ntr.branch_admittance(node_left_minus, node_right_minus)

            # The book provides formulas with impedance:
            # sum_Z = Za + Zb + Zc + Zd
            # Z11 is V1/I1 (with V2=0)
            # Z11 = (Za+Zb)*(Zd+Zc)/sum_Z
            # Z21 is V1/I2 (with V2=0)
            # Z21 = (Zb*Zc-Za*Zd)/sum_Z
            # Z22 is V2/I2 (with V1=0)
            # Z22 = (Za+Zc)*(Zd+Zb)/sum_Z

            # From Pozar, we obtain the A and B components of the ABCD matrix of the lattice
            # The C and D components play no role in determining the transfer function
            # A_lattice = Z11/Z21
            # B_lattice = Z11*Z22/Z21-Z21

            # We will work with admittances, to deal in an easier
            # way with Yx = 0 (otherwise we would have to 
            # distinguish many more cases)

            # Using Mathematica, we compute simplify the expressions for 
            # A_lattice and B_lattice to:
            
            A_lattice = (Ya + Yb)*(Yd + Yc)/(Ya*Yd-Yb*Yc)
            B_lattice = (Ya + Yb + Yc + Yd)/(Ya*Yd-Yb*Yc)

            # The admittance accross the left port plays no role
            # The admittance accross the right port comes into play to yield the A component
            # of the total ABCD matrix:

            A = A_lattice + B_lattice*ntr.branch_admittance(node_right_minus,node_right_plus)

            return  1/A

class Circuit(object):
    """docstring for Circuit"""

    def __init__(self, node_minus, node_plus):
        self.node_minus = node_minus
        self.node_plus = node_plus
        self._circuit = None

    def __or__(self, other_circuit):
        return Parallel(self, other_circuit)

    def _set_plot_coordinates(self):

        self.x_plot_node_minus = float(self._node_minus_plot.split(',')[0])
        self.x_plot_node_plus = float(self._node_plus_plot.split(',')[0])
        self.y_plot_node_minus = -float(self._node_minus_plot.split(',')[1])
        self.y_plot_node_plus = -float(self._node_plus_plot.split(',')[1])
        self.x_plot_center = (self.x_plot_node_minus +
                              self.x_plot_node_plus)/2.
        self.y_plot_center = (self.y_plot_node_minus +
                              self.y_plot_node_plus)/2.
        if self.x_plot_node_minus == self.x_plot_node_plus:
            # increasing y = SOUTH in tkinter
            if self.y_plot_node_minus < self.y_plot_node_plus:
                self.angle = SOUTH
            else:
                self.angle = NORTH
        else:
            if self.x_plot_node_minus < self.x_plot_node_plus:
                self.angle = WEST
            else:
                self.angle = EAST

    def _draw_label(self, ax):
        pp = self._circuit._pp
        if self.angle%180. == 0.:
            x = self.x_plot_center+pp['label']['text_position_horizontal'][0]
            y = self.y_plot_center+pp['label']['text_position_horizontal'][1]
            ha = 'center'
            va = 'top'

        else:
            x = self.x_plot_center+pp['label']['text_position_vertical'][0]
            y = self.y_plot_center+pp['label']['text_position_vertical'][1]
            ha = 'left'
            va = 'center'

        ax.text(x, y,
                to_string(self.unit, self.label, self.value),
                fontsize=pp['label']['fontsize'],
                ha=ha, va=va)

class Parallel(Circuit):

    def __init__(self, left, right):
        super(Parallel, self).__init__(node_minus=None, node_plus=None)

        # sets the two children circuit elements
        self.left = left
        self.right = right

    def _admittance(self):
        return Add(
            self.left._admittance(),
            self.right._admittance())
    
    def _get_RLC_matrix_components(self):
        RLC_matrix_components = {
            'R':0,
            'L':0,
            'C':0
        }
        for el in [self.left,self.right]:
            values_to_add = el._get_RLC_matrix_components()
            for k in RLC_matrix_components:
                RLC_matrix_components[k] += values_to_add[k]
        return RLC_matrix_components

class Component(Circuit):

    def __init__(self, node_minus, node_plus, *args):
        super(Component, self).__init__(node_minus, node_plus)
        self.label = None
        self.value = None
        self.__flux = None

        if len(args)==0:
            raise ValueError("Specify either a value or a label")
        for a in args:
            if a is None:
                pass
            elif type(a) is str:
                self.label = a
            else:
                self.value = a

                # Check its not too big, too small, or negative
                # Note that values above max(min)_float would then
                # be interpreted as infinity (or zero)
                if self.value>max_float:
                    raise ValueError("Maximum allowed value is %.2e"%max_float)
                elif self.value<0:
                    raise ValueError("Value should be a positive float")
                elif 0<=self.value<min_float:
                    raise ValueError("Minimum allowed value is %.2e"%min_float)

    def __hash__(self):
        if self.label is None:
            return hash(str(self.value)+self.unit)
        else:
            if self.value is None:
                return hash(self.label+self.unit)
            else:
                return hash(str(self.value)+self.label+self.unit)

    def _get_value(self, **kwargs):
        if self.value is not None:
            return self.value
        elif self.value is None and kwargs is not None:
            if self.label in [k for k in kwargs]:
                return kwargs[self.label]

        return sp.Symbol(self.label)

    def _set_component_lists(self):
        if self.label not in ['', ' ', 'None', None]:
            self._circuit.components[self.label] = self

        if self.value is None and self.label not in ['', ' ', 'None', None]:
            if self.label in self._circuit._no_value_components:
                # raise ValueError(
                #     "Two components may not have the same name %s" % self.label)
                pass
            else:
                self._circuit._no_value_components.append(self.label)

    def _flux_zpf(self, mode, **kwargs):
        self._circuit._set_zeta(**kwargs)
        w = self._circuit.zeta[mode]
        try:
            tr = self._circuit._flux_transformation_dict[
                                        self._circuit.ref_elt[mode].node_minus,
                                        self._circuit.ref_elt[mode].node_plus,
                                        self.node_minus,
                                        self.node_plus]
        except KeyError:
            tr_analytical = self._circuit._network.transfer(
                self._circuit.ref_elt[mode].node_minus, self._circuit.ref_elt[mode].node_plus, self.node_minus, self.node_plus)
            tr = lambdify(['w']+self._circuit._no_value_components,tr_analytical, "numpy")
            def tr_minus(w,**kwargs):
                return -tr(w,**kwargs)
            
            self._circuit._flux_transformation_dict[
                                        self._circuit.ref_elt[mode].node_minus,
                                        self._circuit.ref_elt[mode].node_plus,
                                        self.node_minus,self.node_plus] = tr
            self._circuit._flux_transformation_dict[
                                        self._circuit.ref_elt[mode].node_minus,
                                        self._circuit.ref_elt[mode].node_plus,
                                        self.node_plus,self.node_minus] = tr_minus

        # Following Black-box quantization, 
        # we assume the losses to be neglegible by 
        # removing the imaginary part of the eigenfrequency
        # w = np.real(w)
        
        # Calculation of phi_zpf of the reference junction/inductor
        #  = sqrt(hbar/w/ImdY[w])
        # The minus is there since 1/Im(Y)  = -Im(1/Y)
        phi_zpf_r = self._circuit.ref_elt[mode]._flux_zpf_r(w,**kwargs)

        # Note that the flux defined here 
        phi = tr(w,**kwargs)*phi_zpf_r
        # is complex.

        return phi


    def _to_string(self, use_unicode=True):
        return to_string(self.unit, self.label, self.value, use_unicode=use_unicode)


    @vectorize_kwargs(exclude = ['quantity','mode'])
    def zpf(self, mode, quantity, **kwargs):
        r'''Returns contribution of a mode to the zero-point fluctuations of a quantity for this component.

        The quantity can be current (in units of Ampere), 
        voltage (in Volts), 
        charge (in electron charge), 
        or flux (in units of the reduced flux quantum, :math:`\hbar/2e`).

        Parameters
        ----------
        mode:           integer
                        Determine what mode to consider, where 0 designates
                        the lowest frequency mode, and the others
                        are arranged in order of increasing frequency
        quantity:       string
                        One of 'current', 'flux', 'charge', 'voltage'
        kwargs:     
                    Values for un-specified circuit components, 
                    ex: ``L=1e-9``.

        Returns
        -------
        float
            contribution of the ``mode`` to the zero-point fluctuations of the ``quantity``

        Notes
        -----
        This quantity is calculated by multiplying the
        voltage transfer function :math:`T_{rc}` (between a reference component :math:`r`
        and the annotated component  :math:`c` ), with
        :math:`X_{zpf,m,r}`, the zero-point fluctuations of :math:`\hat{X}` at the reference component.
        
        Note that resistors make the transfer function :math:`T_{rc}`, and hence this quantity, complex.

        For more detail on the underlying theory, see https://arxiv.org/pdf/1908.10342.pdf.
        '''
        if quantity == 'flux':
            phi_0 = hbar/2./e
            return self._flux_zpf(mode,**kwargs)/phi_0
        if quantity == 'voltage':
            phi_zpf = self._flux_zpf(mode,**kwargs)
            # The above will set the eigenfrequencies
            w=np.real(self._circuit.zeta)[mode]
            
            return phi_zpf*1j*w
        if quantity == 'current':
            Vzpf = self.zpf(mode,'voltage',**kwargs)
            # The above will set the eigenfrequencies

            kwargs_with_w = deepcopy(kwargs)
            kwargs_with_w['w'] = np.real(self._circuit.zeta)[mode]
            Y = self._admittance()
            if isinstance(Y, Number):
                pass
            else:
                Y = Y.evalf(subs=kwargs_with_w)
            return complex(Vzpf*Y)
        if quantity == 'charge':
            Izpf = self.zpf(mode,'current', **kwargs)
            # The above will set the eigenfrequencies

            w = np.real(self._circuit.zeta)[mode]
            return Izpf/1j/w/e

class W(Component):
    """docstring for Wire"""

    def __init__(self, node_minus, node_plus, *args):
        super(W, self).__init__(node_minus, node_plus, '')
        self.unit = None
        self.label = None
        self.value = None

    def _to_string(*args, **kwargs):
        return ' '

    def _set_component_lists(self):
        super(W, self)._set_component_lists()
        self._circuit._wire.append(self)

    def _draw(self):
        pp = self._circuit._pp

        x = [np.array([self.x_plot_node_minus, self.x_plot_node_plus]),
        np.array([self.x_plot_node_minus]),
        np.array([self.x_plot_node_plus])]

        y = [np.array([self.y_plot_node_minus, self.y_plot_node_plus]),
        np.array([self.y_plot_node_minus]),
        np.array([self.y_plot_node_plus])]

        line_type = ['W']
        line_type += ['node']
        line_type += ['node']

        return x, y, line_type

class G(W):
    '''
    From a network perspective, a ground element is a wire that connects
    node_plus to a node called '__ground'
    '''
    def __init__(self, node_minus, node_plus, *args):
        super(G, self).__init__(node_minus, node_plus)

    def _set_component_lists(self):
        super(G, self)._set_component_lists()
        self._circuit._grounds.append(self)

    def _draw(self):
        pp = self._circuit._pp
        # Defined for EAST
        line_type = []
        x = [
            np.array([0.5, 0.3]),
            np.array([0.3, 0.3]),
            np.array([0.23, 0.23]),
            np.array([0.16, 0.16]),
        ]
        y = [
            np.array([0., 0.]),
            np.array([-1., 1.])*5./30.,
            np.array([-1., 1.])*3./30.,
            np.array([-1., 1.])*1./30.,
        ]
        line_type.append('W')
        line_type.append('W')
        line_type.append('W')
        line_type.append('W')

        if self.angle == WEST:
            return shift(x, self.x_plot_center), shift(y, self.y_plot_center), line_type
        elif self.angle == NORTH:
            return shift(y, self.x_plot_center), shift([-xx for xx in x], self.y_plot_center), line_type
        elif self.angle == EAST:
            return shift([-xx for xx in x], self.x_plot_center), shift(y, self.y_plot_center), line_type
        elif self.angle == SOUTH:
            return shift(y, self.x_plot_center), shift(x, self.y_plot_center), line_type

class L(Component):
    """A class representing an inductor
    
    Parameters
    ----------
    node_minus:     integer
                    Index corresponding to one node of inductor
    node_minus:     integer
                    Index corresponding to the other node of the inductor
    args:           <float> or <str> or <float>,<str>
                    Other arguments should be a float corresponding to the
                    inductance, a string corresponding to the 
                    name of that value (ex: `"L"`), or both.
                    If only a label is provided, 
                    a value for should be passed
                    as a keyword argument in subsequent function calls
                    (ex: `L = 1e-9`)   
                    This is the best way to proceed if one wants to sweep the value of this
                    inductor. Indeed, the most computationally expensive part of the 
                    analysis is performed upon initializing the circuit, subsequently
                    changing the value of a component and re-calculating a quantity 
                    such as the frequency or anharmonicity can be performed much faster.
    """
    def __init__(self, node_minus, node_plus, *args):
        super(L, self).__init__(node_minus, node_plus, *args)
        self.unit = 'H'

    def _admittance(self):
        return -sp.I*Mul(1/sp.Symbol('w'), 1/self._get_value())

    def _set_component_lists(self):
        super(L, self)._set_component_lists()
        self._circuit.inductors.append(self)

    def _draw(self):
        pp = self._circuit._pp

        x = np.linspace(0.5, float(
            pp['L']['N_turns']) + 1., pp['L']['N_points'])
        y = -np.sin(2.*np.pi*x)
        x = np.cos(2.*np.pi*x)+2.*x

        line_type = []
        line_type.append('L')

        # reset leftmost point to 0
        x_min = x[0]
        x -= x_min

        # set width inductor width
        x_max = x[-1]
        x *= pp['L']['width']/x_max

        # set leftmost point to the length of
        # the side connection wires
        x += (1.-pp['L']['width'])/2.

        # add side wire connections
        x_min = x[0]
        x_max = x[-1]
        x_list = [x]
        x_list += [np.array([0., x_min])]
        x_list += [np.array([x_max, 1.])]
        line_type.append('W')
        line_type.append('W')

        # center in x
        x_list = shift(x_list, -1./2.)

        # set height of inductor
        y *= pp['L']['height']/2.

        # add side wire connections
        y_list = [y]
        y_list += [np.array([0., 0.])]
        y_list += [np.array([0., 0.])]

        if self.angle%180. == 0.:
            return shift(x_list, self.x_plot_center), shift(y_list, self.y_plot_center), line_type
        if self.angle%180. == 90.:
            return shift(y_list, self.x_plot_center), shift(x_list, self.y_plot_center), line_type

    def _get_RLC_matrix_components(self):
        return {
            'R':0,
            'L':1/self._get_value(),
            'C':0
        }

    @timeit
    def _compute_flux_zpf_r(self):
        '''
        Generate the L._flux_zpf_r function which
        takes as an argument an angular frequency (and keyword arguments 
        if component values need to be specified) and returns the 
        derivative of the admittance evaluated at the nodes of the inductor, 
        which is effective capacitance at that frequency.         
        '''
        # Compute a sympy expression for the admittance 
        # at the nodes of the reference element
        Y = self._circuit._network.admittance(self.node_minus, self.node_plus)

        # Write the expression as a single fraction 
        # with the numerator and denomenator as polynomials
        # (it combines but also "de-nests")      
        Y_together = sp.together(Y)

        # Extract numerator and denominator
        u = sp.numer(Y_together)
        v = sp.denom(Y_together)

        # Symbol representing angular frequency
        w = sp.Symbol('w')

        # Calculate derivatives
        derivatives = []
        for P in [u]:#[u,v]:
            # Write as polynomial in 'w'
            P = sp.collect(sp.expand(P), w)

            # Obtain the order of the polynomial 
            P_order = sp.polys.polytools.degree(P, gen=w) 

            # Compute list of coefficients
            P_coeffs_analytical = [P.coeff(w, n) for n in range(P_order+1)[::-1]]

            # Express the derivative of the polynomial
            dP = sum([(P_order-n)*a*w**(P_order-n-1)
                        for n, a in enumerate(P_coeffs_analytical)])

            derivatives.append(dP)
        
        du = derivatives[0]
        # dv = derivatives[1]
        
        # Convert the sympy expression for v/du to a function
        # Note the function arguments are the angular frequency 
        # and component values that need to be specified
        dY = lambdify(['w']+self._circuit._no_value_components,du/v, "numpy")

        def _flux_zpf_r(z,**kwargs):
            return np.sqrt(hbar/np.real(z)/np.imag(dY(z,**kwargs)))

        self._flux_zpf_r = _flux_zpf_r


class J(L):
    """A class representing a junction
    
    Parameters
    ----------
    node_minus:     integer
                    Index corresponding to one node of junction
    node_minus:     integer
                    Index corresponding to the other node of the junction
    args:           <float> or <str> or <float>,<str>
                    Other arguments should be a float which by default
                    corresponds to the Josephson inductance of the
                    junction, a string corresponding to the 
                    name of that value (ex: `"L_J"`), or both.
                    If only a label is provided, 
                    a value for this junction should be passed
                    as a keyword argument in subsequent function calls
                    (ex: `L_J = 10e-9`).
                    This is the best way to proceed if one wants to sweep the value of this
                    junction. Indeed, the most computationally expensive part of the 
                    analysis is performed upon initializing the circuit, subsequently
                    changing the value of a component and re-calculating a quantity 
                    such as the frequency or anharmonicity can be performed much faster.
    use_E:          Boolean
                    If set to True, the junction will be parametrized by
                    its Josephson energy, given in units of Hertz, rather
                    than its Josephson inductance
    use_I:          Boolean
                    If set to True, the junction will be parametrized by
                    its critical current, given in units of Ampere, rather
                    than its Josephson inductance
    """
    def __init__(self, node_minus, node_plus, *args, use_E=False, use_I=False):
        super(J, self).__init__(node_minus, node_plus, *args)

        self.use_E = use_E
        self.use_I = use_I
        if self.use_E:
            self.unit = 'Hz'
        elif self.use_I:
            self.unit = 'A'
        else:
            self.unit = 'H'

    def _get_value(self, **kwargs):
        # Returns the Josephson inductance
        value = super(J, self)._get_value(**kwargs)
        if (self.use_E == False) and (self.use_I == False):
            return value
        elif (self.use_E == True) and (self.use_I == False):
            L = (hbar/2./e)**2/(value*h)  # E is assumed to be provided in Hz
            return L
        elif (use_E == False) and (use_I == True):
            L = (hbar/2./e)/value
            return L
        else:
            raise ValueError("Cannot set both use_E and use_I to True")

    def _get_Ej(self, **kwargs):
        return (hbar/2./e)**2/(self._get_value(**kwargs)*h)

    def _set_component_lists(self):
        super(L, self)._set_component_lists()
        self._circuit.junctions.append(self)
    
    @vectorize_kwargs(exclude = ['mode'])
    def anharmonicity(self, mode, **kwargs):
        r'''Returns the contribution of this junction to the anharmonicity of a given normal mode.

        Returned in units of Hertz, not angular frequency.

        Parameters
        ----------
        kwargs:     
                    Values for un-specified circuit components, 
                    ex: ``L=1e-9``.
        
        mode:           integer
                        where 0 designates
                        the lowest frequency mode, and the others
                        are arranged in order of increasing frequency
        Returns
        -------
        float
            contribution of this junction to the anharmonicity of a given normal mode
        
        Notes
        -----
        The quantity returned is the anharmonicity
        of the mode ``m`` if this junction were the only junction
        present in the circuit (i.e. if all the 
        others were replaced by linear inductors).

        The total anharmonicity of a mode (in first order perturbation theory) is obtained
        by summing these contribution over all modes.

        For more details, see https://arxiv.org/pdf/1908.10342.pdf
        '''
        return self._get_Ej(**kwargs)/2*np.absolute(self.zpf(mode,quantity='flux',**kwargs))**4


    def _draw(self):
        pp = self._circuit._pp

        line_type = []
        x = [
            np.array([0., 1.]),
            np.array([(1.-pp['J']['width'])/2.,
                      (1.+pp['J']['width'])/2.]),
            np.array([(1.-pp['J']['width'])/2.,
                      (1.+pp['J']['width'])/2.])
        ]
        y = [
            np.array([0., 0.]),
            np.array([-1., 1.])*pp['J']['width']/2.,
            np.array([1., -1.])*pp['J']['width']/2.
        ]
        line_type.append('W')
        line_type.append('J')
        line_type.append('J')

        # center in x and y
        x = shift(x, -1./2.)

        if self.angle%180. == 0.:
            return shift(x, self.x_plot_center), shift(y, self.y_plot_center), line_type
        if self.angle%180. == 90.:
            return shift(y, self.x_plot_center), shift(x, self.y_plot_center), line_type

class R(Component):
    """A class representing a resistor
    
    Parameters
    ----------
    node_minus:     integer
                    Index corresponding to one node of resistor
    node_minus:     integer
                    Index corresponding to the other node of the resistor
    args:           <float> or <str> or <float>,<str>
                    Other arguments should be a float corresponding to the
                    resistance, a string corresponding to the 
                    name of that value (ex: `"R"`), or both.
                    If only a label is provided, 
                    a value for should be passed
                    as a keyword argument in subsequent function calls
                    (ex: `R = 1e-9`)   
                    This is the best way to proceed if one wants to sweep the value of this
                    resistor. Indeed, the most computationally expensive part of the 
                    analysis is performed upon initializing the circuit, subsequently
                    changing the value of a component and re-calculating a quantity 
                    such as the dissipation rate can be performed much faster.
    """
    def __init__(self, node_minus, node_plus, *args):
        super(R, self).__init__(node_minus, node_plus, *args)
        self.unit = u"\u03A9"

    def _admittance(self):
        return 1/self._get_value()
    
    def _set_component_lists(self):
        super(R, self)._set_component_lists()
        self._circuit.resistors.append(self)
    
    def _get_RLC_matrix_components(self):
        return {
            'R':1/self._get_value(),
            'L':0,
            'C':0
        }
    
    def _draw(self):
        pp = self._circuit._pp

        x = np.linspace(-0.25, 0.25 +float(pp['R']['N_ridges']), pp['R']['N_points'])
        height = 1.
        period = 1.
        a = height*2.*(-1.+2.*np.mod(np.floor(2.*x/period), 2.))
        b = -height*2.*np.mod(np.floor(2.*x/period), 2.)
        y = (2.*x/period - np.floor(2.*x/period))*a+b+height

        line_type = []
        line_type.append('R')

        # reset leftmost point to 0
        x_min = x[0]
        x -= x_min

        # set width inductor width
        x_max = x[-1]
        x *= pp['R']['width']/x_max

        # set leftmost point to the length of
        # the side connection wires
        x += (1.-pp['R']['width'])/2.

        # add side wire connections
        x_min = x[0]
        x_max = x[-1]
        x_list = [x]
        x_list += [np.array([0., x_min])]
        x_list += [np.array([x_max, 1.])]
        line_type.append('W')
        line_type.append('W')

        # center in x
        x_list = shift(x_list, -1./2.)

        # set height of inductor
        y *= pp['R']['height']/2.

        # add side wire connections
        y_list = [y]
        y_list += [np.array([0., 0.])]
        y_list += [np.array([0., 0.])]

        if self.angle%180. == 0.:
            return shift(x_list, self.x_plot_center), shift(y_list, self.y_plot_center), line_type
        if self.angle%180. == 90.:
            return shift(y_list, self.x_plot_center), shift(x_list, self.y_plot_center), line_type

class C(Component):
    """A class representing a capacitor
    
    Parameters
    ----------
    node_minus:     integer
                    Index corresponding to one node of capacitor
    node_minus:     integer
                    Index corresponding to the other node of the capacitor
    args:           <float> or <str> or <float>,<str>
                    Other arguments should be a float corresponding to the
                    capacitance, a string corresponding to the 
                    name of that value (ex: `"C"`), or both.
                    If only a label is provided, 
                    a value for should be passed
                    as a keyword argument in subsequent function calls
                    (ex: `C = 1e-9`)   
                    This is the best way to proceed if one wants to sweep the value of this
                    capacitor. Indeed, the most computationally expensive part of the 
                    analysis is performed upon initializing the circuit, subsequently
                    changing the value of a component and re-calculating a quantity 
                    such as the anharmonicity can be performed much faster.
    """
    def __init__(self, node_minus, node_plus, *args):
        super(C, self).__init__(node_minus, node_plus, *args)
        self.unit = 'F'

    def _admittance(self):
        return sp.I*Mul(sp.Symbol('w'), self._get_value())

    def _set_component_lists(self):
        super(C, self)._set_component_lists()
        self._circuit.capacitors.append(self)

    def _draw(self):
        pp = self._circuit._pp
        line_type = []
        x = [
            np.array([0., (1.-pp['C']['gap'])/2.]),
            np.array([(1.+pp['C']['gap']) /
                      2., 1.]),
            np.array([(1.-pp['C']['gap'])/2.,
                      (1.-pp['C']['gap'])/2.]),
            np.array([(1.+pp['C']['gap'])/2.,
                      (1.+pp['C']['gap'])/2.]),
        ]
        y = [
            np.array([0., 0.]),
            np.array([0., 0.]),
            np.array([-pp['C']['height']/2., pp['C']['height']/2.]),
            np.array([-pp['C']['height']/2., pp['C']['height']/2.]),
        ]
        line_type.append('W')
        line_type.append('W')
        line_type.append('C')
        line_type.append('C')

        # center in x and y
        x = shift(x, -1./2.)

        if self.angle%180. == 0.:
            return shift(x, self.x_plot_center), shift(y, self.y_plot_center), line_type
        if self.angle%180. == 90.:
            return shift(y, self.x_plot_center), shift(x, self.y_plot_center), line_type

    def _get_RLC_matrix_components(self):
        return {
            'R':0,
            'L':0,
            'C':self._get_value()
        }

class Admittance(Component):
    def __init__(self, node_minus, node_plus, Y):
        self.node_minus = node_minus
        self.node_plus = node_plus
        self.Y = Y

    def _admittance(self):
        return self.Y