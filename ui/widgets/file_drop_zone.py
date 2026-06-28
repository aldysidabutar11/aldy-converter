from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from ui.theme import Colors, Typography, Radius
import qtawesome as qta
from .frosted_panel import FrostedPanel

class FileDropZone(FrostedPanel):
    files_dropped = pyqtSignal(list)
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent, radius=Radius.LARGE, border_dashed=True)
        self.setAcceptDrops(True)
        self.setFixedHeight(300) # Larger like image
        self.setObjectName("DropZone")
        self.update_drop_style(False)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title_label = QLabel("Drag & Drop files here")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"background: transparent; border: none; font-size: 28px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        
        self.subtitle_label = QLabel("or click to browse")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet(f"background: transparent; border: none; font-size: 14px; color: {Colors.TEXT_PRIMARY};")
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        self.setLayout(layout)
        self.update_icon(False)

    def update_icon(self, hover):
        # Specific PDF + Cloud look (mocking with stacked icons if possible, or just cloud-upload)
        color = Colors.SIDEBAR_BG if not hover else Colors.TEXT_PRIMARY
        self.icon_label.setPixmap(qta.icon('fa5s.file-pdf', color="#5D6D7E").pixmap(80, 80)) # Large icon like image

    def update_drop_style(self, hover):
        if hover:
            self.setStyleSheet(f"""
                QWidget#DropZone {{
                    background-color: #FFFFFF;
                    border: 1px solid {Colors.TEXT_PRIMARY};
                    border-radius: {Radius.LARGE};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget#DropZone {{
                    background-color: transparent;
                    border: 1px solid #C8B2A6;
                    border-radius: {Radius.LARGE};
                }}
            """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.update_drop_style(True)
            self.update_icon(True)
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        self.update_drop_style(False)
        self.update_icon(False)
        
    def dropEvent(self, event):
        self.update_drop_style(False)
        self.update_icon(False)
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.files_dropped.emit(files)
            
    def enterEvent(self, event):
        self.update_drop_style(True)
        self.update_icon(True)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.update_drop_style(False)
        self.update_icon(False)
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()