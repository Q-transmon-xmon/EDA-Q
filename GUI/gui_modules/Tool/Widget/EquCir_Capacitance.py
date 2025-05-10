from PyQt5.QtWidgets import QMessageBox

from GUI.gui_modules.Tool.Widget.base_dialog import BaseModifierDialog


class DialogQubitCapacitance(BaseModifierDialog):
    def __init__(self, design):
        super().__init__(
            design=design,
            title="Qubit Capacitance Modifier",
            defaults=["q0", "40"],  # Default qubit name and capacitance value
            input_labels=[
                "Qubit Name:",
                "Capacitance (fF):"
            ]
        )

    def process_values(self, values):
        try:
            qubit_name = values[0].strip()  # Clean whitespace
            capacitance = float(values[1])

            # Validate inputs
            if capacitance <= 0:
                raise ValueError("Capacitance must be positive")

            # Check if qubit exists
            if not self.design.equivalent_circuit.is_qubit_exist(qname=qubit_name):
                raise ValueError(f"Qubit '{qubit_name}' does not exist in the design")

            # Execute modification
            self.design.equivalent_circuit.change_qubit_options(
                qubit_name=qubit_name,
                value=capacitance
            )

            # Send update signal
            self.designUpdated.emit(self.design)

            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Successfully updated {qubit_name}\n"
                f"New capacitance: {capacitance}fF",
                QMessageBox.Ok
            )
            return True

        except ValueError as ve:
            raise ValueError(f"Input validation failed: {str(ve)}")
        except AttributeError as ae:
            raise RuntimeError(f"Circuit operation error: {str(ae)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")