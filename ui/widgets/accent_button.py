from PyQt6.QtWidgets import QPushButton
from ui.theme import Colors, Typography, Radius

class AccentButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(44)
        self.update_style()
        
    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                color: white;
                font-family: {Typography.FAMILY};
                font-size: 16px;
                font-weight: 600;
                border: none;
                border-radius: {Radius.SMALL};
                padding: 0 48px;
                background-color: {Colors.ACCENT_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.ACCENT_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #FFFFFF;
            }}
        """)
