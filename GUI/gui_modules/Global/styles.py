def set_stylesheet(app):
    """Set the global stylesheet for the application to reduce visual fatigue."""
    app.setStyleSheet("""
        /* Global styles */
        QWidget {
            font-family: "Segoe UI";
            font-size: 11pt;
            background-color: #A8C8E4;
            color: #2C4A6B;
        }

        QMainWindow {
            background-color: #F9F6F2;
        }

        /* Toolbar styles - Modification point 1 */
        QToolBar {
            background-color: #6B8DAA;
            border: none;
            padding: 5px;
        }
        QToolButton {
            background-color: transparent;
            color: #FFFFFF;
            padding: 5px;
        }
        QToolButton:hover {
            background-color: rgba(0, 180, 216, 0.2);
            border-radius: 4px;
            /* ❌ Removed animation: ripple 0.3s; */
        }
        QToolButton:pressed {
            background-color: #00B4D8;
            color: white;
        }

        /* Button styles */
        QPushButton {
            background-color: #F9F6F2;
            border: 1px solid #00B4D8;
            color: #2C4A6B;
            min-width: 80px;
            padding: 6px 10px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: rgba(0, 180, 216, 0.3);
            color: #00B4D8;
        }
        QPushButton:pressed {
            background-color: #0077B6;
            color: white;
        }
        QPushButton:disabled {
            background-color: rgba(142, 197, 255, 0.5);
            color: rgba(112, 128, 144, 0.5);
        }

        /* Tab styles */
        QTabWidget::pane {
            border: 1px solid #B0C4DE;
        }
        QTabBar::tab {
            background-color: #F9F6F2;
            padding: 5px;
        }
        QTabBar::tab:selected {
            background-color: #00B4D8;
            color: white;
        }

        /* Status bar styles */
        QStatusBar {
            background-color: #00B4D8;
            color: white;
        }

        /* Line edit styles */
        QLineEdit {
            padding: 5px;
            border: 1px solid #B0C4DE;
            border-radius: 5px;
            background-color: #F9F6F2;
            color: #2C4A6B;
        }
        QLineEdit:focus {
            border: 1px solid #00B4D8;
        }

        /* Dynamic gradient background */
        QWidget#canvas {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #A8C8E4, stop:1 #E0F2FE);
            border: none;
        }

        /* ❌ Removed the entire @keyframes ripple block */

        /* Interactive color logic - Modification point 2 */
        .hover {
            background-color: rgba(142, 197, 255, 0.3);
        }
        .clicked {
            background-color: #00B4D8;
            /* ❌ Removed transition: background-color 0.3s; */
        }
        .disabled {
            background-color: rgba(142, 197, 255, 0.5);
            /* ❌ Removed filter: blur(2px); */
        }

        /* Other element styles */
        .highlight {
            background-color: #00B4D8;
            border: 2px solid #C4A484;
        }

        .warning {
            background-color: #FFB74D;
            color: black;
        }

        .progress-indicator {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00CED1, stop:1 #20B2AA);
        }
    """)

    def _setup_style(self):
        """Configure the browser-like stylesheet - Modification point 3"""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #C0C0C0;
                border-top: none;
                border-radius: 4px;
                margin: 0;
                background: white;
            }

            QTabBar {
                background: transparent;
                spacing: 2px;
                border: none;
            }

            /* Modification point 4: Corrected gradient syntax */
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,  /* ✅ Corrected to qlineargradient */
                                          stop:0 #F5F5F5, stop:1 #E5E5E5);
                border: 1px solid #C0C0C0;
                border-bottom-color: #C0C0C0;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 120px;
                height: 28px;
                padding: 4px 12px;
                margin-right: -1px;
                color: #404040;
                font: 13px 'Segoe UI';
            }

            QTabBar::tab:selected {
                background: white;
                border-color: #C0C0C0;
                border-bottom-color: white;
                margin-bottom: -1px;
            }

            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,  /* ✅ Corrected to qlineargradient */
                                          stop:0 #F0F0F0, stop:1 #E0E0E0);
            }

            QTabBar::tab:disabled {
                color: #A0A0A0;
                background: #F0F0F0;
            }
        """)