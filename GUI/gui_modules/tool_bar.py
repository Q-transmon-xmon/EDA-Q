# state_manager.py
import os
import sys

from GUI.Widget_2.EquCir_Capacitance import DialogQubitCapacitance
from GUI.Widget_2.EquCir_CpCapitance import DialogCouplingCapacitance
from GUI.Widget_2.EquCir_CpInductance import DialogCouplingInductance

# Get the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
GUI_PATH = os.path.dirname(current_path)
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add paths
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)

from typing import Optional
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QToolBar, QAction, QMenu, QDialog, QFileDialog
from PyQt5.QtGui import QIcon
from api.design import Design
from PyQt5.QtWidgets import QMessageBox  # Import QMessageBox for pop-up windows  
from GUI.gui_modules.global_state import global_state  # Import global state management singleton

# Import all dialog classes (keep original)
from GUI.Widget_2.Widget_chiplayer import Dialog_ChipLayer
from GUI.Widget_2.Widget_RAlgorithm import Dialog_RAlgorithm
from GUI.Widget_2.Widget_RCavity import Dialog_RCavity
from GUI.Widget_2.Widget_Gds import Dialog_NestedDictViewer
from GUI.Widget_2.Widget_Pin import Dialog_pins
from GUI.Widget_2.Widget_Others import Dialog_Others
from GUI.Widget_2.Topo_Node import Dialog_Node
from GUI.Widget_2.Topo_RandomEdge import Dialog_RandomEdge
from GUI.Widget_2.Topo_CustomEdge import Dialog_CustomEdge
from GUI.Widget_2.Qubit_type import Dialog_Selection
from GUI.Widget_2.Qubit_Custom import Dialog_Qubit_Custom
from GUI.Widget_2.Generate_Tmls import Dialog_tmls
from GUI.Widget_2.Generate_Cpls import Dialog_cpls
from GUI.Widget_2.Generate_Ctls import Dialog_ctls
from GUI.Widget_2.Generate_Crosvs import Dialog_crosvs
from GUI.Widget_2.Sim_Xmon import Dialog_Xmon
from GUI.Widget_2.Sim_Trans import Dialog_Transmon
from GUI.Widget_2.Sim_Readout import Dialog_s21

class ToolBarManager(QToolBar):
    def __init__(self, parent=None):
        super(ToolBarManager, self).__init__(parent)
        self.parent = parent
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(32, 28))
        self.setStyleSheet("QToolButton { min-width: 120px; }")

        # Icon path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(os.path.dirname(current_dir), "icons", "toolbar", "icon_white")
        # Add icon path error checking  
        self.check_icon_path(self.icon_path)  

        self.init_toolbar()

    def init_toolbar(self):
        """Initialize the toolbar (completely retain the original menu structure)"""
        buttons = [
            ("Import topology", "Algorithm"),
            ("Custom Topology", "Topology"),
            ("Equivalent Circuit", "Circuit"),
            ("Generate Qubits", "Qubit"),
            ("Generate ChipLayer", "ChipLayer"),
            ("Readout Resonator", "ReadoutResonator"),
            ("Generate Pin", "GeneratePin"),
            ("Generate Lines", "GenerateLine"),
            ("Routing Algorithm", "RoutingAlgorithm"),
            ("Modify GDS", "GDS"),
            ("Simulation", "Simulation"),
            ("Others", "Others"),
            ("Clear", "Clear"),
        ]

        for index, (button_text, object_name) in enumerate(buttons, start=1):
            action = QAction(QIcon(os.path.join(self.icon_path, f"{index}.png")), button_text, self)
            action.setObjectName(object_name)

            if object_name == "Topology":
                menu = QMenu(self)
                topology_options = ["Generate Topo Node", "Random-Generate Topo Edge", "Custom-Generate Topo Edge"]
                for option_name in topology_options:
                    menu_action = menu.addAction(option_name)
                    menu_action.triggered.connect(lambda checked, name=option_name: self.handle_topology_option(name))
                action.setMenu(menu)
                self.addAction(action)
            elif object_name == "Qubit":
                menu = QMenu(self)
                qubit_options = ["Based on the existing topology", "Custom-generate qubits"]
                for option_name in qubit_options:
                    menu_action = menu.addAction(option_name)
                    menu_action.triggered.connect(lambda checked, name=option_name: self.handle_qubit_option(name))
                action.setMenu(menu)
                self.addAction(action)
            elif object_name == "GenerateLine":
                menu = QMenu(self)
                line_options = ["Coupling_line", "Control_line", "Crossover_line", "Transmission_line"]
                for option_name in line_options:
                    menu_action = menu.addAction(option_name)
                    menu_action.triggered.connect(lambda checked, name=option_name: self.handle_line_option(name))
                action.setMenu(menu)
                self.addAction(action)
            elif object_name == "Simulation":
                menu = QMenu(self)
                simulation_options = ["Xmon", "Transmon", "Readout"]
                for option_name in simulation_options:
                    menu_action = menu.addAction(option_name)
                    menu_action.triggered.connect(lambda checked, name=option_name: self.handle_simulation_option(name))
                action.setMenu(menu)
                self.addAction(action)
            elif object_name == "Circuit":
                menu = QMenu(self)
                circuit_options = ["Generate Equivalent Circuit", "Modify Qubit Capacitance",
                                   "Modify Coupling Inductance", "Modify Coupling Capacitance"]
                for option_name in circuit_options:
                    menu_action = menu.addAction(option_name)
                    menu_action.triggered.connect(lambda checked, name=option_name: self.handle_circuit_option(name))
                action.setMenu(menu)
                self.addAction(action)
            else:
                action.triggered.connect(lambda checked, name=object_name: self.handle_action(name))
                self.addAction(action)

            # Add a function for handling equivalent circuit options

    def get_current_design(self) -> Optional[Design]:
        current_name = global_state.get_current_design_name()
        return global_state.get_design(current_name) if current_name else None

    def handle_action(self, action_name):
        """Handle main button clicks (retain original if-elif structure)"""
        current_design = self.get_current_design()
        if not current_design:
            print("Error: No design loaded!")
            return

        try:
            if action_name == 'Algorithm':
                self.select_file()
            elif action_name == 'Circuit':
                print("Performing equivalent circuit construction operation")
                if not current_design.topology.positions:
                    QMessageBox.warning(self, "Warning", "Topology positions are empty. Cannot generate equivalent circuit.")
                else:
                    current_design.generate_equivalent_circuit()
                    current_design.equivalent_circuit.show()
            elif action_name == 'ChipLayer':
                print("Generating chip layer operation")
                self.parent.chip_layer = Dialog_ChipLayer(design=current_design)
                self.parent.chip_layer.designUpdated.connect(
                    lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                )
                self.parent.chip_layer.show()
            elif action_name == 'ReadoutResonator':
                print("Generating readout cavity operation")
                self.parent.RCavity = Dialog_RCavity(design=current_design)
                self.parent.RCavity.designUpdated.connect(
                    lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                )
                self.parent.RCavity.show()
            elif action_name == 'GeneratePin':
                print("Generating pin operation")
                self.parent.gener_pin = Dialog_pins(design=current_design)
                self.parent.gener_pin.designUpdated.connect(
                    lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                )
                self.parent.gener_pin.show()
            elif action_name == 'RoutingAlgorithm':
                print("Executing routing algorithm operation")
                self.parent.ralgorithm_dialog = Dialog_RAlgorithm(design=current_design)
                self.parent.ralgorithm_dialog.designUpdated.connect(
                    lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                )
                self.parent.ralgorithm_dialog.show()
            elif action_name == 'GDS':
                print("Modifying GDS layout operation")
                self.parent.gds_dialog = Dialog_NestedDictViewer(design=current_design)
                self.parent.gds_dialog.window_gds.designUpdated.connect(
                    lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                )
                self.parent.gds_dialog.show()
            elif action_name == 'Others':
                print("Other operations")
                self.parent.other_dialog = Dialog_Others(design=current_design)
                self.parent.other_dialog.designUpdated.connect(
                    lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                )
                self.parent.other_dialog.show()
            elif action_name == 'Clear':
                print("Executing clear operation")
                self.clear_action()

        except ValueError as e:
            print(f"Operation failed: {str(e)}")

    # All menu handling functions (retain original structure)
    def handle_topology_option(self, option_name):
        if current_design := self.get_current_design():
            try:
                if option_name == "Generate Topo Node":
                    self.parent.node_dialog = Dialog_Node(design=current_design)
                    self.parent.node_dialog.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.node_dialog.exec_()
                elif option_name == "Random-Generate Topo Edge":
                    self.parent.RandomEdge = Dialog_RandomEdge(design=current_design)
                    self.parent.RandomEdge.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.RandomEdge.exec_()
                elif option_name == "Custom-Generate Topo Edge":
                    self.parent.CustomEdge = Dialog_CustomEdge(design=current_design)
                    self.parent.CustomEdge.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.CustomEdge.exec_()
            except KeyError:
                print(f"Unable to update design '{global_state.get_current_design_name()}'")

    def handle_qubit_option(self, option_name):
        if current_design := self.get_current_design():
            try:
                if option_name == "Based on the existing topology":
                    self.parent.qubit_type = Dialog_Selection(design=current_design)
                    self.parent.qubit_type.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.qubit_type.exec_()
                elif option_name == "Custom-generate qubits":
                    self.parent.custom_qubit = Dialog_Qubit_Custom(design=current_design)
                    self.parent.custom_qubit.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.custom_qubit.exec_()
            except KeyError:
                print(f"Design '{global_state.get_current_design_name()}' does not exist")

    def handle_line_option(self, option_name):
        if current_design := self.get_current_design():
            try:
                if option_name == "Coupling_line":
                    self.parent.cpl_dialog = Dialog_cpls(design=current_design)
                    self.parent.cpl_dialog.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.cpl_dialog.exec_()
                elif option_name == "Control_line":
                    self.parent.ctl_dialog = Dialog_ctls(design=current_design)
                    self.parent.ctl_dialog.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.ctl_dialog.exec_()
                elif option_name == "Crossover_line":
                    self.parent.crosvs_dialog = Dialog_crosvs(design=current_design)
                    self.parent.crosvs_dialog.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.crosvs_dialog.exec_()
                elif option_name == "Transmission_line":
                    self.parent.tml_dialog = Dialog_tmls(design=current_design)
                    self.parent.tml_dialog.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.tml_dialog.exec_()
            except KeyError:
                print("Current design is unavailable")

    def handle_simulation_option(self, option_name):
        if current_design := self.get_current_design():
            try:
                if option_name == "Xmon":
                    self.parent.xmon_dialog = Dialog_Xmon(design=current_design)
                    self.parent.xmon_dialog.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.xmon_dialog.exec_()
                elif option_name == "Transmon":
                    self.parent.transmon_dialog = Dialog_Transmon(design=current_design)
                    self.parent.transmon_dialog.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.transmon_dialog.exec_()
                elif option_name == "Readout":
                    self.parent.readout_dialog = Dialog_s21(design=current_design)
                    self.parent.readout_dialog.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.readout_dialog.exec_()
            except KeyError:
                print("Unable to update design")

    def handle_circuit_option(self, option_name):
        """Process circuit parameter modification operations(Integrated dialog box version)"""
        if current_design := self.get_current_design():
            try:
                if option_name == "Generate Equivalent Circuit":
                    # Generate equivalent circuit(Keep the original logic)
                    current_design.generate_equivalent_circuit()
                    current_design.equivalent_circuit.show()

                elif option_name == "Modify Qubit Capacitance":
                    self.parent.qubit_cap_dialog = DialogQubitCapacitance(design=current_design)
                    self.parent.qubit_cap_dialog.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.qubit_cap_dialog.exec_()

                elif option_name == "Modify Coupling Inductance":
                    self.parent.coupling_ind_dialog = DialogCouplingInductance(design=current_design)
                    self.parent.coupling_ind_dialog.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.coupling_ind_dialog.exec_()

                elif option_name == "Modify Coupling Capacitance":
                    self.parent.coupling_cap_dialog = DialogCouplingCapacitance(design=current_design)
                    self.parent.coupling_cap_dialog.designUpdated.connect(
                        lambda d: global_state.update_design(global_state.get_current_design_name(), d)
                    )
                    self.parent.coupling_cap_dialog.exec_()
            except KeyError:
                QMessageBox.critical(
                    self.parent,
                    "Design Error",
                    f"Unable to update design '{global_state.get_current_design_name()}'\nPlease ensure the design contains the necessary components",
                    QMessageBox.Ok
                )
            except Exception as e:
                QMessageBox.critical(
                    self.parent,
                    "Operation Failed",
                    f"Operation execution failed: {str(e)}",
                    QMessageBox.Ok
                )
    def select_file(self):
        """File selection logic (using GlobalState API)"""
        fileDialog = QFileDialog(self.parent)
        fileDialog.setWindowTitle('Select Topology File')
        fileDialog.setFileMode(QFileDialog.ExistingFiles)
        fileDialog.setNameFilter("QASM Files (*.qasm);;All Files (*)")

        if fileDialog.exec_() == QFileDialog.Accepted:
            if file_paths := fileDialog.selectedFiles():
                file_path = file_paths[0]
                try:
                    design_name = global_state.get_current_design_name()
                    # Use GlobalState to create and switch design
                    Import_design = Design(qasm_path=file_path)
                    global_state.update_design(design_name, Import_design)
                    # self.parent.display_area.show_topo_image('./picture/topology.png')
                except ValueError as e:
                    print(f"Import failed: {str(e)}")
                except Exception as e:
                    print(f"Unknown error: {str(e)}")

    def clear_action(self):
        """Clear operation (reset via GlobalState)"""
        try:
            # Reset to initial design
            global_state.update_current_design_name("Initial Design")
            self.parent.display_area.clear_all()
            # Close all dialogs
            for dialog in self.parent.findChildren(QDialog):
                dialog.close()
            print("Interface has been reset")
        except ValueError as e:
            print(f"Reset failed: {str(e)}")

    def check_icon_path(self, path):
        """Check if the icon path exists and contains the necessary icon files."""
        if not os.path.exists(path):
            raise ValueError(f"The specified path does not exist: {path}")
        # Optional: Check if at least one icon file exists in the directory
        if not any(file.endswith('.png') for file in os.listdir(path)):
            raise ValueError(f"No icon files found in the specified path: {path}")