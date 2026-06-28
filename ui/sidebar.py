from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import qtawesome as qta
from ui.theme import Colors, Typography, Radius

class Sidebar(QWidget):
    page_selected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.SIDEBAR_BG};
                border: none;
            }}
            QListWidget {{
                border: none;
                background-color: transparent;
                outline: 0;
            }}
            QListWidget::item {{
                height: 38px;
                padding-left: 12px;
                border-radius: {Radius.SMALL};
                margin: 1px 12px;
                color: {Colors.TEXT_PRIMARY};
                font-family: {Typography.FAMILY};
                font-size: 13px;
                font-weight: 500;
            }}
            QListWidget::item:hover {{
                background-color: {Colors.SIDEBAR_HOVER_BG};
            }}
            QListWidget::item:selected {{
                background-color: {Colors.SIDEBAR_SELECTED_BG};
                color: {Colors.TEXT_PRIMARY};
                font-weight: 600;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(0)
        
        # Logo
        self.logo = QLabel("Aldy Converter")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.logo.setStyleSheet(f"""
            font-family: {Typography.FAMILY};
            font-size: 22px; 
            font-weight: 700; 
            padding: 20px 16px 15px 24px; 
            color: {Colors.TEXT_PRIMARY};
            border: none;
        """)
        layout.addWidget(self.logo)
        
        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget.currentRowChanged.connect(self.page_selected.emit)
        
        features_set1 = [
            ("Merge PDF", "fa5s.object-group"),
            ("Split PDF", "fa5s.cut"),
            ("PDF to Image", "fa5s.image"),
            ("Image to PDF", "fa5s.file-pdf"),
            ("PDF to Word", "fa5s.file-word"),
            ("Word to Excel", "fa5s.file-excel"),
            ("Excel to Excel", "fa5s.file-excel"),
            ("Excel to PDF", "fa5s.file-pdf")
        ]
        
        features_set2 = [
            ("Compress PDF", "fa5s.compress"),
            ("OCR PDF", "fa5s.search")
        ]
        
        for feature, icon_name in features_set1:
            item = QListWidgetItem(feature)
            item.setIcon(qta.icon(icon_name, color=Colors.TEXT_PRIMARY))
            self.list_widget.addItem(item)
            
        # Adjust height to content
        self.list_widget.setFixedHeight(len(features_set1) * 40 + 10)
        layout.addWidget(self.list_widget)
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setStyleSheet(f"background-color: {Colors.SIDEBAR_BORDER}; margin: 4px 24px; height: 1px; border: none;")
        layout.addWidget(line)
        
        self.list_widget2 = QListWidget()
        self.list_widget2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Offset index for second list
        self.list_widget2.currentRowChanged.connect(lambda r: self.page_selected.emit(r + len(features_set1)))
        
        for feature, icon_name in features_set2:
            item = QListWidgetItem(feature)
            item.setIcon(qta.icon(icon_name, color=Colors.TEXT_PRIMARY))
            self.list_widget2.addItem(item)
            
        self.list_widget2.setFixedHeight(len(features_set2) * 40 + 10)
        layout.addWidget(self.list_widget2)
        layout.addStretch()
        
        # Ensure only one selection across lists
        self.list_widget.itemClicked.connect(lambda: self.list_widget2.clearSelection())
        self.list_widget2.itemClicked.connect(lambda: self.list_widget.clearSelection())
        
        self.setLayout(layout)
        
    def select_first(self):
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
