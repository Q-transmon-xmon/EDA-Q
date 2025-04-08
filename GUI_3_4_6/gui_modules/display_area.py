import sys
import os
import logging

# Get the directory where the current script is located
GUI_PATH = os.path.dirname(os.path.abspath(__file__))
PROJ_PATH = os.path.dirname(GUI_PATH)

# Add paths
sys.path.append(GUI_PATH)
sys.path.append(PROJ_PATH)
from PyQt5.QtWidgets import QMessageBox  # Import QMessageBox for pop-up windows
from PyQt5.QtWidgets import (
    QTabWidget, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QSizePolicy, QFrame, QToolButton
)
from PyQt5.QtCore import Qt, QPoint, QEvent
from PyQt5.QtGui import QPixmap, QWheelEvent, QCursor, QIcon
from api.design import Design

from GUI_3_4_6.gui_modules.global_state import global_state
from GUI_3_4_6.gui_modules.ruler import Ruler


class DisplayArea(QTabWidget):
    """Main display area container, fixing drag-and-drop issues"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initial_gds_size = (800, 600)

        # Ruler components
        self.v_ruler = Ruler(orientation="vertical")
        self.h_ruler = Ruler(orientation="horizontal")

        # State management
        self._init_ui()
        self.current_scale = 1.0
        self.min_scale = 0.1
        self.max_scale = 3.0
        self.topo_image_path = ''
        self.gds_image_path = ''
        self.drag_offset = QPoint(0, 0)  # Drag offset
        self.image_pos = QPoint(0, 0)    # Current image position

        # Install event filter
        if hasattr(self, 'gds_image_container'):
            self.gds_image_container.installEventFilter(self)

        # Add zoom button
        self._add_zoom_button()

    def _init_ui(self):
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setElideMode(Qt.ElideRight)

        # Create tabs (optimized layout structure)
        self.topo_tab = self._create_tab("Topology View", is_gds=False)
        self.gds_tab = self._create_tab("GDS View", is_gds=True)
        self.addTab(self.topo_tab, "Topology")
        self.addTab(self.gds_tab, "GDS")

    def _create_tab(self, title, is_gds=True):
        """Create a tab (supporting free drag-and-drop)"""
        tab = QWidget()
        tab.setMouseTracking(True)

        # Main layout
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        if is_gds:
            # GDS tab: rulers + image container
            top_container = QWidget()
            top_container.setLayout(QHBoxLayout())
            top_container.layout().setContentsMargins(0, 0, 0, 0)
            top_container.layout().setSpacing(0)

            # Vertical ruler
            self.v_ruler.setFixedWidth(30)
            top_container.layout().addWidget(self.v_ruler)

            # Image container (key for drag-and-drop)
            self.gds_image_container = QWidget()  # Save as an instance variable
            self.gds_image_container.setLayout(QVBoxLayout())
            self.gds_image_container.layout().setContentsMargins(0, 0, 0, 0)
            self.gds_image_label = QLabel(self.gds_image_container)
            self.gds_image_label.setAlignment(Qt.AlignCenter)
            self.gds_image_label.setMinimumSize(*self.initial_gds_size)
            self.gds_image_label.setScaledContents(False)
            self.gds_image_container.layout().addWidget(self.gds_image_label)

            top_container.layout().addWidget(self.gds_image_container)
            main_layout.addWidget(top_container)

            # Horizontal ruler
            self.h_ruler.setFixedHeight(30)
            main_layout.addWidget(self.h_ruler)
        else:
            # Topology tab: image only
            self.topo_image_label = QLabel(tab)
            self.topo_image_label.setAlignment(Qt.AlignCenter)
            self.topo_image_label.setMinimumSize(800, 600)
            self.topo_image_label.setScaledContents(False)
            main_layout.addWidget(self.topo_image_label)

        return tab

    def eventFilter(self, watched, event):
        """Handle container resize events"""
        if watched == self.gds_image_container and event.type() == QEvent.Resize:
            if self.currentIndex() == 1:  # Current tab is GDS
                self._update_gds_display(self.gds_image_label.pixmap())
            return True
        return super().eventFilter(watched, event)

    def show_topo_image(self, image_path):
        self.topo_image_path = image_path
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = self.scale_pixmap(pixmap)
            self.topo_image_label.setPixmap(scaled_pixmap)
            self.topo_image_label.move(self.image_pos)  # Apply position after reset
            self.topo_image_label.setText("")
        else:
            self.topo_image_label.setText("Failed to load topology")

    def show_gds_image(self, image_path):
        self.gds_image_path = image_path
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = self.scale_pixmap(pixmap)
            self.gds_image_label.setPixmap(scaled_pixmap)
            self.gds_image_label.move(self.image_pos)  # Apply position after reset
            self.gds_image_label.setText("")
            self._update_gds_display(scaled_pixmap)
        else:
            self.gds_image_label.setText("Failed to load GDS")

    def scale_pixmap(self, pixmap):
        """Scale the image while maintaining the aspect ratio"""
        scaled_width = int(pixmap.width() * self.current_scale)
        scaled_height = int(pixmap.height() * self.current_scale)
        return pixmap.scaled(
            scaled_width, scaled_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

    def _update_gds_display(self, pixmap):
        try:
            if not self.parent.design_instance or not hasattr(self.parent.design_instance, 'gds'):
                self.h_ruler.set_coordinates(0, 0)
                self.v_ruler.set_coordinates(0, 0)
                return

            bbox = self.parent.design_instance.gds.get_gds_bounding_box()
            if not bbox or None in bbox:
                raise ValueError("Invalid GDS bounding box")

            # Ensure bbox is numeric (handle possible sequence type errors)
            min_coor = (float(bbox[0][0]), float(bbox[0][1]))  # Force conversion to float tuple
            max_coor = (float(bbox[1][0]), float(bbox[1][1]))
            design_width = max_coor[0] - min_coor[0]
            design_height = max_coor[1] - min_coor[1]

            viewport_width = self.gds_image_container.width()
            viewport_height = self.gds_image_container.height()

            # Calculate scale factors (ensure no division by zero)
            scale_x = self.initial_gds_size[0] / design_width if design_width != 0 else 1.0
            scale_y = self.initial_gds_size[1] / design_height if design_height != 0 else 1.0

            current_scale_x = scale_x * self.current_scale
            current_scale_y = scale_y * self.current_scale
            # Calculate coordinates element-wise (avoid sequence multiplication)
            start_x = min_coor[0] + (self.image_pos.x() / current_scale_x)
            end_x = start_x + (viewport_width / current_scale_x)
            start_y = min_coor[1] + (self.image_pos.y() / current_scale_y)
            end_y = start_y + (viewport_height / current_scale_y)
            # Update rulers
            self.h_ruler.set_coordinates(start_x, end_x)
            self.v_ruler.set_coordinates(start_y, end_y)
            self.h_ruler.set_scale_factor(current_scale_x)
            self.v_ruler.set_scale_factor(current_scale_y)

        except Exception as e:
            logging.warning(f"Ruler update failed: {str(e)}")
            self.h_ruler.set_coordinates(0, 0)
            self.v_ruler.set_coordinates(0, 0)

    def wheelEvent(self, event: QWheelEvent):
        """Zoom using the scroll wheel (centered on the mouse)"""
        delta = event.angleDelta().y()
        scale_factor = 1.1 if delta > 0 else 0.9
        new_scale = self.current_scale * scale_factor
        new_scale = max(min(new_scale, self.max_scale), self.min_scale)

        # Calculate the relative position of the mouse within the image
        if self.currentIndex() == 0:
            label = self.topo_image_label
        else:
            label = self.gds_image_label
        mouse_rel_pos = label.mapFrom(self, event.pos())

        # Adjust the offset to maintain the zoom center
        self.image_pos = QPoint(
            int(self.image_pos.x() + (mouse_rel_pos.x() - mouse_rel_pos.x() * (new_scale / self.current_scale))),
            int(self.image_pos.y() + (mouse_rel_pos.y() - mouse_rel_pos.y() * (new_scale / self.current_scale)))
        )
        self.current_scale = new_scale

        # Refresh the display
        if self.currentIndex() == 0:
            self.show_topo_image(self.topo_image_path)
        else:
            self.show_gds_image(self.gds_image_path)
        event.accept()

    def mousePressEvent(self, event):
        """Mouse press event (record drag start point)"""
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.pos()  # Record the starting position
            self.setCursor(QCursor(Qt.ClosedHandCursor))
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Mouse move event (remove boundary restrictions)"""
        if event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.drag_offset
            self.drag_offset = event.pos()
            self.image_pos += delta  # Directly update the position without constraints

            # Move the image
            if self.currentIndex() == 0:
                self.topo_image_label.move(self.image_pos)
            else:
                self.gds_image_label.move(self.image_pos)
                self._update_gds_display(self.gds_image_label.pixmap())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Mouse release event (restore cursor)"""
        if event.button() == Qt.LeftButton:
            self.setCursor(QCursor(Qt.ArrowCursor))
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Mouse double-click event: reset to initial position and zoom"""
        if event.button() == Qt.LeftButton:
            # Reset position and zoom scale
            self.image_pos = QPoint(0, 0)
            self.current_scale = 1.0

            # Reload the current image (trigger display update)
            if self.currentIndex() == 0 and self.topo_image_path:
                self.show_topo_image(self.topo_image_path)
            elif self.currentIndex() == 1 and self.gds_image_path:
                self.show_gds_image(self.gds_image_path)
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def clear_all(self):
        # Clear design data
        null_design = Design()
        global_state.update_design(
            design_name=global_state.get_current_design_name(),
            updated_design=null_design
        )

        # Update current design reference
        self.parent.design_instance = null_design

        # Reset interface display
        # 1. Clear topology image
        self.topo_image_label.clear()
        self.topo_image_label.setText("No Topology Display")

        # 2. Clear GDS image
        self.gds_image_label.clear()
        self.gds_image_label.setText("No GDS Display")

        # 3. Reset ruler display
        # Modify ruler update call method
        self._update_gds_display(None)  # Now it is safe to pass a null value

        # Also clear ruler scales
        self.h_ruler.set_scale_factor(1.0)
        self.v_ruler.set_scale_factor(1.0)

        # 4. Reset position and zoom state
        self.image_pos = QPoint(0, 0)
        self.current_scale = 1.0

        # 5. Force interface refresh
        if self.currentIndex() == 0:  # Topology tab
            self.topo_image_label.repaint()
        else:  # GDS tab
            self.gds_image_label.repaint()
            self._update_gds_display(None)  # Pass a null value to trigger ruler update

    def _add_zoom_button(self):  
        """Add a zoom button to the display area"""  
        self.zoom_button = QToolButton(self)  
        # Icon path  
        current_dir = os.path.dirname(os.path.abspath(__file__))  
        self.icon_path = os.path.join(os.path.dirname(current_dir), "icons")  
        zoom_icon_path = os.path.join(self.icon_path, "extend.png")

        # Add icon path error detection
        if not os.path.exists(zoom_icon_path):
            raise ValueError(f"Zoom icon file does not exist: {zoom_icon_path}")

        self.zoom_button.setIcon(QIcon(zoom_icon_path))  
        self.zoom_button.setIconSize(self.zoom_button.sizeHint())  # Set icon size  
        self.zoom_button.clicked.connect(self._zoom_in)  # Bind zoom function  
        self.zoom_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Fix button size  
        self.zoom_button.raise_()  # Bring button to the top layer  
        self.zoom_button.move(self.width() - self.zoom_button.width() - 10, 10)  # Place in the top-right corner

    def resizeEvent(self, event):
        """Override resizeEvent to ensure the button stays in the top-right corner"""
        super().resizeEvent(event)
        self.zoom_button.move(self.width() - self.zoom_button.width() - 10, 10)

    def _zoom_in(self):
        # Perform different actions based on the current tab
        if self.currentIndex() == 0:  # Topo tab
            if self.parent.design_instance and hasattr(self.parent.design_instance, 'topology'):
                self.parent.design_instance.topology.show_image()
            else:
                logging.warning("No topology instance available")
        elif self.currentIndex() == 1:  # GDS tab
            if self.parent.design_instance and hasattr(self.parent.design_instance, 'gds'):
                self.parent.design_instance.gds.show_gds()
            else:
                logging.warning("No GDS instance available")
        else:
            logging.warning("Unknown tab index")