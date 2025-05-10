from GUI.gui_modules.Component.cells.Transmon_Actions import TransmonActions
from GUI.gui_modules.Component.cells.Xmon_Actions import XmonActions
from GUI.gui_modules.Component.cells.AirBridge_Actions import AirBridgeActions
from GUI.gui_modules.Component.cells.AirbriageNb_Actions import AirbriageNbActions
from GUI.gui_modules.Component.cells.ChargeLine_Actions import ChargeLineActions
from GUI.gui_modules.Component.cells.ControlLineCircle_Actions import ControlLineCircleActions
from GUI.gui_modules.Component.cells.ControlLineWidthDiff_Actions import ControlLineWidthDiffActions
from GUI.gui_modules.Component.cells.CouplerBase_Actions import CouplerBaseActions
from GUI.gui_modules.Component.cells.CouplingCavity_Actions import CouplingCavityActions
from GUI.gui_modules.Component.cells.CouplingLineStraight_Actions import CouplingLineStraightActions
from GUI.gui_modules.Component.cells.IndiumBump_Actions import IndiumBumpActions
from GUI.gui_modules.Component.cells.LaunchPad_Actions import LaunchPadActions
from GUI.gui_modules.Component.cells.ReadoutArrow_Actions import ReadoutArrowActions
from GUI.gui_modules.Component.cells.ReadoutArrowPlus_Actions import ReadoutArrowPlusActions
from GUI.gui_modules.Component.cells.ReadoutCavity_Actions import ReadoutCavityActions
from GUI.gui_modules.Component.cells.ReadoutCavityFlipchip_Actions import ReadoutCavityFlipchipActions
from GUI.gui_modules.Component.cells.ReadoutCavityPlus_Actions import ReadoutCavityPlusActions
from GUI.gui_modules.Component.cells.TransmissionPath_Actions import TransmissionPathActions


class ComponentHandlers:
    """Centralized management of all component action handlers"""

    def __init__(self, current_design, parent):
        """Initialize all component action handlers"""
        self.handlers = {
            "transmon": TransmonActions(current_design, parent).transmon,
            "xmon": XmonActions(current_design, parent).xmon,
            "coupling_cavity": CouplingCavityActions(current_design, parent).coupling_cavity,
            "coupling_line_straight": CouplingLineStraightActions(current_design, parent).coupling_line_straight,
            "readout_cavity": ReadoutCavityActions(current_design, parent).readout_cavity,
            "readout_cavity_plus": ReadoutCavityPlusActions(current_design, parent).readout_cavity_plus,
            "readout_cavity_flipchip": ReadoutCavityFlipchipActions(current_design, parent).readout_cavity_flipchip,
            "readout_arrow": ReadoutArrowActions(current_design, parent).readout_arrow,
            "readout_arrow_plus": ReadoutArrowPlusActions(current_design, parent).readout_arrow_plus,
            "launch_pad": LaunchPadActions(current_design, parent).launch_pad,
            "control_line_circle": ControlLineCircleActions(current_design, parent).control_line_circle,
            "control_line_width_diff": ControlLineWidthDiffActions(current_design, parent).control_line_width_diff,
            "transmission_path": TransmissionPathActions(current_design, parent).transmission_path,
            "charge_line": ChargeLineActions(current_design, parent).charge_line,
            "airbridge": AirBridgeActions(current_design, parent).airbridge,
            "airbriage_nb": AirbriageNbActions(current_design, parent).airbriage_nb,
            "indium_bump": IndiumBumpActions(current_design, parent).indium_bump,
            "coupler_base": CouplerBaseActions(current_design, parent).coupler_base
        }

    def get_handler(self, command):
        """Get the handler function for the specified command"""
        return self.handlers.get(command)