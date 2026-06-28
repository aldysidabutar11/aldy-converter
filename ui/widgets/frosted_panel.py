from PyQt6.QtWidgets import QWidget
from ui.theme import Colors, Radius

class FrostedPanel(QWidget):
    def __init__(self, parent=None, radius=Radius.LARGE, border_dashed=False):
        super().__init__(parent)
        border_style = "dashed" if border_dashed else "solid"
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.MAIN_PANEL_BG};
                border: 1px {border_style} {Colors.BORDER_MAIN};
                border-radius: {radius};
            }}
        """)
