#######################################################################################################################
#This class manages equivalent circuit operations such as initialization, option injection, and parameter calculations.
#######################################################################################################################

from base.base import Base
from addict import Dict
import equ_circ.equ_circ_old
import func_modules
import copy
import numpy as np
import qucat

class EquivalentCircuit(Base):
    def __init__(self, **init_ops):
        """
        Initialize the EquivalentCircuit class.

        Input:
            init_ops: dict, initialization options for creating an equivalent circuit object.

        Output:
            None
        """
        self.initialization(**init_ops)
        return

    def initialization(self, **init_ops):
        """
        Initialize the parameters and attributes of the equivalent circuit object.

        Input:
            init_ops: dict, initialization options.

        Output:
            None
        """
        self.options_path = None  
        self.qcsv_path = None  
        self.rcsv_path = None  
        self.op_name_list = list(self.__dict__.keys())  

        # Call the module to generate equivalent circuit options
        options = func_modules.equ_circ.generate_equivalent_circuit(**init_ops)
        self.inject_options(options)
        return

    def clear(self):
        """
        Clear all attributes of the current object.

        Input:
            None

        Output:
            None
        """
        for op_name in self.op_name_list:
            setattr(self, op_name, None)
        return

    def inject_options(self, options):
        """
        Inject options into the object.

        Input:
            options: dict, containing the equivalent circuit options to be injected.

        Output:
            None
        """
        options = copy.deepcopy(options)  
        self.clear()  
        for op_name, op_value in options.items():
            setattr(self, op_name, op_value)  
        return

    def generate_equ_circ_from_topo(self, topo_ops):
        """
        Generate an equivalent circuit based on topology parameters.

        Input:
            topo_ops: dict, topology parameters.

        Output:
            None
        """
        # Set the path for generating files
        self.options_path = "./equ_circ_files/equ_circ_options.txt"
        self.qcsv_path = "./equ_circ_files/qubit.csv"
        self.rcsv_path = "./equ_circ_files/readout.csv"

        # Call the module to generate an equivalent circuit
        equ_circ.generate_equ_circ(topo_ops=topo_ops, 
                                   txt_path=self.options_path, 
                                   qcsv_path=self.qcsv_path, 
                                   rcsv_path=self.rcsv_path)
        
        #from equ_circ.qucat import GUI
        from qucat import GUI

        self.qucat_cir = GUI(self.options_path,  # Location of the circuit file
               edit=True,  # Open the GUI to edit the circuit
               plot=True,  # Plot the circuit after editing
               print_network=False  # Do not print the network
               )
        return

    def show(self):
        """
        Display the generated equivalent circuit.

        Input:
            None

        Output:
            None
        """
        path = self.options_path  
        equ_circ.display_equ_circ(txt_path=path)  
        return

    def change_qubit_options(self, qubit_name, value):
        """
        Modify the options for a specified qubit.

        Input:
            qubit_name: str, the name of the qubit.
            value: The specific value to update the qubit options.

        Output:
            None
        """
        options_path = self.options_path  
        qcsv_path = self.qcsv_path  
        equ_circ.change_qubit_options(options_path, qcsv_path, qubit_name, value)
        return

    def change_coupling_options(self, coupling_line_name, op_name, op_value):
        """
        Modify the options for a specified coupling line.

        Input:
            coupling_line_name: str, the name of the coupling line.
            op_name: str, the name of the option.
            op_value: The specific value to update the coupling line options.

        Output:
            None
        """
        options_path = self.options_path  
        rcsv_path = self.rcsv_path  
        equ_circ.change_coupling_options(options_path, rcsv_path, coupling_line_name, op_name, op_value)
        return

    def save_image(self, path):
        """
        Save the image of the equivalent circuit.

        Input:
            path: str, the path to save the image.

        Output:
            None
        """
        options_path = self.options_path  
        equ_circ.save_equ_circ_image(options_path, path)
        return

    def find_qubit_options(self, qubit_name):
        """
        Find the options for a specified qubit.

        Input:
            qubit_name: str, the name of the qubit.

        Output:
            dict, containing the options for the qubit.
        """
        qcsv_path = self.qcsv_path  
        return equ_circ.find_qubit_options(qcsv_path=qcsv_path, qubit_name=qubit_name)

    def find_coupling_options(self, coupling_line_name, op_name):
        """
        Find the options for a specified coupling line.

        Input:
            coupling_line_name: str, the name of the coupling line.
            op_name: str, the name of the option.

        Output:
            dict, containing the value of the coupling line options.
        """
        rcsv_path = self.rcsv_path  
        return equ_circ.find_coupling_options(rcsv_path=rcsv_path, coupling_line_name=coupling_line_name, op_name=op_name)

    def calculate_qubits_parms(self, f_q, Ec):
        """
        Calculate related parameters based on qubit frequency and capacitance energy.

        Input:
            f_q: float, qubit frequency in GHz.
            Ec: float, capacitance energy in GHz.

        Output:
            None (but prints the calculation results to the console).
        """
        # Constants definition
        Ec = Ec * 2 * np.pi * 1e6  
        e = 1.60217657e-19  
        h = 6.62606957e-34  
        hbar = 1.0545718E-34  
        phinot = 2.067 * 1E-15  
        phi0 = phinot / (2 * np.pi)  
        c = 3 * 10**8  

        # Calculate related parameters
        Ej = (f_q * 10**9 + Ec)**2 / (8 * Ec)  
        print("If fq =", f_q, 'GHz')
        print("then, Ej =", round((Ej / 10**9), 2), "GHz")
        
        Ic = Ej * h / phi0  
        print("then, Ic =", round((Ic * 10**9), 2), "nA")
        
        Rn = np.pi * 0.182 * 10**-3 / (2 * Ic)  
        print("then, Rn =", round(Rn, 4), "Ω")
        return
    
    def custom_function(self, options1, options2):
        equ_circ_ops = self.options

        ################################ 
        # update equavalent circuit options (your code)
        ################################

        self.inject_options(equ_circ_ops)
        return
    
    def is_qubit_exist(self, qname):
        qubit_ops = self.find_qubit_options(qname)
        if qubit_ops is None:
            return False
        else:
            return True
        
    def is_coupling_exist(self, coupling_name):
        cl_ops = self.find_coupling_options(coupling_line_name=coupling_name,
                                            op_name="l")
        if cl_ops is None:
            return False
        else:
            return True
        
    def call_eigenfrequencies(self, **kwargs):
        EF = self.qucat_cir.eigenfrequencies(**kwargs)
        return EF
    
    def call_loss_rates(self, **kwargs):
        LR = self.qucat_cir.loss_rates(**kwargs)
        return LR

    def call_anharmonicities(self, **kwargs):
        AH = self.qucat_cir.anharmonicities(**kwargs)
        return AH
    
    def call_kerr(self, **kwargs):
        KR = self.qucat_cir.kerr(**kwargs)
        return KR
    

    