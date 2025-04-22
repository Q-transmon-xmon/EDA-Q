from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics
from PyQt5.QtCore import Qt
import math
import logging


class Ruler(QWidget):
    def __init__(self, orientation="horizontal", parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.min_val = 0.0
        self.max_val = 100.0
        self.scale = 1.0
        self.style = {
            "color": QColor(80, 80, 80),
            "font": QFont("Arial", 8),
            "tick_length": 12,
            "label_margin": 3
        }
        self._setup_initial_size()

    def _setup_initial_size(self):
        if self.orientation == "vertical":
            self.setFixedWidth(40)
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        else:
            self.setFixedHeight(40)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_coordinates(self, min_val, max_val):
        if max_val <= min_val: return
        self.min_val = min_val
        self.max_val = max_val
        self.update()

    def set_scale_factor(self, scale):
        self.scale = scale
        self.update()  # Force redraw the ruler

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setFont(self.style["font"])

            if self.orientation == "horizontal":
                self._draw_horizontal(painter)
            else:
                self._draw_vertical(painter)
        except Exception as e:
            logging.error(f"Ruler paint error: {str(e)}")

    def _draw_horizontal(self, painter):
        w, h = self.width(), self.height()
        painter.setPen(QPen(self.style["color"], 1))

        # Draw baseline
        painter.drawLine(30, h - 5, w, h - 5)

        # Dynamically calculate ticks
        phys_range = self.max_val - self.min_val
        if phys_range <= 0: return

        interval = self._calculate_interval(phys_range)
        start = math.floor(self.min_val / interval) * interval
        end = math.ceil(self.max_val / interval) * interval

        current = start
        while current <= end:
            x = 30 + (current - self.min_val) * self.scale
            x = int(round(x))
            self._draw_tick(painter, x, h - 5, f"{current:.2f}")
            current += interval

    def _draw_vertical(self, painter):
        w, h = self.width(), self.height()
        painter.setPen(QPen(self.style["color"], 1))

        # Draw baseline
        painter.drawLine(w - 5, 30, w - 5, h)

        # Dynamically calculate ticks
        phys_range = self.max_val - self.min_val
        if phys_range <= 0: return

        interval = self._calculate_interval(phys_range)
        start = math.floor(self.min_val / interval) * interval
        end = math.ceil(self.max_val / interval) * interval

        current = start
        while current <= end:
            y = h - 30 - (current - self.min_val) * self.scale
            y = int(round(y))
            self._draw_tick(painter, w - 5, y, f"{current:.2f}", vertical=True)
            current += interval

    def _draw_tick(self, painter, x, y, label, vertical=False):
        x, y = int(x), int(y)
        if vertical:
            # Draw vertical tick line
            painter.drawLine(x, y, x - self.style["tick_length"], y)
            # Rotate to draw label
            painter.save()
            painter.translate(x - self.style["tick_length"] - 2, y)
            painter.rotate(-90)
            painter.drawText(0, 0, label)
            painter.restore()
        else:
            # Draw horizontal tick line
            painter.drawLine(x, y, x, y - self.style["tick_length"])
            # Calculate text position
            text_width = QFontMetrics(self.style["font"]).width(label)
            painter.drawText(x - text_width // 2, y - self.style["tick_length"] - self.style["label_margin"], label)

    def _calculate_interval(self, phys_range):
        decade = 10 ** math.floor(math.log10(phys_range))
        normalized = phys_range / decade
        if normalized < 2:
            return decade * 0.1
        elif normalized < 5:
            return decade * 0.2
        else:
            return decade * 0.5