import os
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QAbstractItemView, QGridLayout, QScrollArea, QFrame, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import qtawesome as qta
from ui.theme import Colors, Typography, Radius

class FileCard(QFrame):
    remove_requested = pyqtSignal(str)
    
    def __init__(self, filepath, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.setFixedSize(220, 80)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.CARD_BG};
                border: 1px solid {Colors.CARD_BORDER};
                border-radius: {Radius.SMALL};
            }}
            QFrame:hover {{
                border: 1px solid {Colors.SIDEBAR_BG};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Icon logic
        ext = os.path.splitext(filepath)[1].lower()
        icon_name = 'fa5s.file'
        icon_color = "#999999"
        if ext == '.pdf':
            icon_name = 'fa5s.file-pdf'
            icon_color = "#E57373"
        elif ext in ['.docx', '.doc']:
            icon_name = 'fa5s.file-word'
            icon_color = "#64B5F6"
            
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon_name, color=icon_color).pixmap(32, 32))
        icon_label.setStyleSheet("border: none; background: transparent;")
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = QLabel(os.path.basename(filepath))
        name_label.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; border: none; background: transparent;")
        
        size = os.path.getsize(filepath) / (1024 * 1024)
        size_label = QLabel(f"{size:.1f} MB")
        size_label.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_SECONDARY}; border: none; background: transparent;")
        
        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(4)
        self.pbar.setTextVisible(False)
        self.pbar.setStyleSheet(f"""
            QProgressBar {{ background: #EEEEEE; border: none; border-radius: 2px; }}
            QProgressBar::chunk {{ background: #A5D6A7; border-radius: 2px; }}
        """)
        self.pbar.setValue(60) # Default mock progress from image
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(size_label)
        info_layout.addWidget(self.pbar)
        
        btn_layout = QVBoxLayout()
        self.btn_remove = QPushButton()
        self.btn_remove.setIcon(qta.icon('fa5s.trash-alt', color="#BBBBBB"))
        self.btn_remove.setFixedSize(20, 20)
        self.btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove.setStyleSheet("border: none; background: transparent;")
        self.btn_remove.clicked.connect(lambda: self.remove_requested.emit(self.filepath))
        
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addStretch()
        
        layout.addWidget(icon_label)
        layout.addLayout(info_layout)
        layout.addLayout(btn_layout)

class FileList(QScrollArea):
    files_changed = pyqtSignal()
    
    def __init__(self, parent=None, drag_drop=False):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("background: transparent;")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(12)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.setWidget(self.container)
        self.files = []

    def add_file(self, filepath):
        if filepath not in self.files:
            self.files.append(filepath)
            self._refresh_grid()
            self.files_changed.emit()
            
    def add_files(self, filepaths):
        for f in filepaths:
            if f not in self.files:
                self.files.append(f)
        self._refresh_grid()
        self.files_changed.emit()
            
    def remove_file(self, filepath):
        if filepath in self.files:
            self.files.remove(filepath)
            self._refresh_grid()
            self.files_changed.emit()
            
    def clear_files(self):
        self.files = []
        self._refresh_grid()
        self.files_changed.emit()
        
    def get_files(self):
        return self.files

    def _refresh_grid(self):
        # Clear current grid
        for i in reversed(range(self.grid.count())): 
            self.grid.itemAt(i).widget().setParent(None)
            
        cols = 4 # Match image grid
        for i, f in enumerate(self.files):
            card = FileCard(f)
            card.remove_requested.connect(self.remove_file)
            self.grid.addWidget(card, i // cols, i % cols)
