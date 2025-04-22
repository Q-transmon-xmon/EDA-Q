from PyQt5.QtWidgets import QMessageBox

from GUI.Widget_2.base_dialog import BaseModifierDialog


class DialogCouplingCapacitance(BaseModifierDialog):
    def __init__(self, design):
        super().__init__(
            design=design,
            title="Coupling Capacitance Modifier",
            defaults=["r21", "c", "125"],  # Default: coupling line, operation type, value
            input_labels=[
                "Coupling Line:",
                "Operation (C/R):",
                "Capacitance Value (fF):"
            ]
        )

    def process_values(self, values):
        try:
            coupling_line_name = values[0].strip()
            op_name = values[1].lower()  # Will be converted to 'c' or 'r'
            op_value = values[2]

            # Validate operation type
            if op_name.lower() not in ['c', 'r']:
                raise ValueError("Operation must be C (Capacitance) or R (Ratio)")

            # Convert to required parameter names
            if op_name.upper() == 'R':
                op_name = 'ratio'  # Assuming the method expects 'ratio' for ratio operations
            else:
                op_name = 'c'  # For capacitance operations

            # Execute the coupling modification
            self.design.equivalent_circuit.change_coupling_options(
                coupling_line_name=coupling_line_name,
                op_name=op_name,
                op_value=op_value
            )

            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Updated coupling {coupling_line_name}\n"
                f"Operation: {op_name.upper()}\n"
                f"New value: {op_value}fF",
                QMessageBox.Ok
            )

            self.designUpdated.emit(self.design)
            return True

        except ValueError as ve:
            raise ValueError(f"Invalid input: {str(ve)}")
        except AttributeError as ae:
            raise RuntimeError(f"Circuit operation failed: {str(ae)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")