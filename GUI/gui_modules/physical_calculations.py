# physical_calculations.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox,
                             QHBoxLayout, QDoubleSpinBox)
from PyQt5.QtCore import Qt
import numpy as np
from simulation.rdls_tmls import CPW_frequency_4  # Import calculation function
from scipy.constants import c  # Obtain the standard speed of light value


class LambdaQuarterFrequencyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("λ/4 CPW Frequency Calculation")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(300)

        # Create interface elements
        self.length_input = QDoubleSpinBox()
        self.length_input.setRange(0.1, 1000000)
        self.length_input.setSuffix(" μm")
        self.length_input.setDecimals(3)

        self.k_input = QDoubleSpinBox()
        self.k_input.setRange(1.0, 100.0)
        self.k_input.setValue(10.0)
        self.k_input.setSingleStep(0.5)

        self.calculate_btn = QPushButton("Calculate")
        self.result_label = QLabel("Frequency will be shown here")
        self.result_label.setWordWrap(True)

        # Set layout
        layout = QVBoxLayout()

        # Length input line
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("CPW Length:"))
        length_layout.addWidget(self.length_input)
        layout.addLayout(length_layout)

        # Dielectric constant input line
        k_layout = QHBoxLayout()
        k_layout.addWidget(QLabel("Relative Permittivity (ε):"))
        k_layout.addWidget(self.k_input)
        layout.addLayout(k_layout)

        layout.addWidget(self.calculate_btn)
        layout.addSpacing(20)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

        # joining signal
        self.calculate_btn.clicked.connect(self.calculate_frequency)

    def calculate_frequency(self):
        try:
            # Retrieve input values and validate them
            length_um = self.length_input.value()  # unit：micron
            k = self.k_input.value()

            if length_um <= 0:
                raise ValueError("Length must be positive")
            if k < 1:
                raise ValueError("Relative permittivity must be ≥1")

            # conversion units：micron -> rice
            length_m = length_um * 1e-6

            # Call calculation function
            freq_ghz = CPW_frequency_4(length_m, k)

            # Convert to other units
            freq_mhz = freq_ghz * 1000
            wavelength_m = c / (freq_ghz * 1e9)

            # Display results
            result_text = (
                f"λ/4 Frequency: {freq_ghz:.3f} GHz\n"
                f"({freq_mhz:,.0f} MHz)\n\n"
                f"Corresponding wavelength: {wavelength_m:.3f} m\n"
                f"({wavelength_m * 100:.1f} cm)"
            )
            self.result_label.setText(result_text)

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(
                self,
                "Calculation Error",
                f"An error occurred:\n{str(e)}"
            )