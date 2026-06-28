from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QMessageBox, QFileDialog, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QShortcut, QKeySequence
from ui.widgets.file_drop_zone import FileDropZone
from ui.widgets.file_list import FileList
from ui.widgets.accent_button import AccentButton
from ui.theme import Colors, Typography, Radius
import os
import qtawesome as qta

class BasePage(QWidget):
    def __init__(self, title, description, parent=None, drag_drop=False):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(40, 40, 40, 24)
        self.layout.setSpacing(12)
        
        self.header = QLabel(title)
        self.header.setStyleSheet(f"""
            font-size: {Typography.H1_SIZE}; 
            font-weight: {Typography.H1_WEIGHT}; 
            color: {Colors.TEXT_PRIMARY};
            border: none;
            background: transparent;
        """)
        
        self.desc = QLabel(description)
        self.desc.setStyleSheet(f"""
            font-size: {Typography.BODY_SIZE}; 
            color: {Colors.TEXT_PRIMARY}; 
            margin-bottom: 24px;
            border: none;
            background: transparent;
        """)
        
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.desc)
        
        self.drop_zone = FileDropZone()
        self.drop_zone.setToolTip("Click to browse or drag files here (Ctrl+O)")
        self.drop_zone.files_dropped.connect(self.on_files_dropped)
        self.drop_zone.clicked.connect(self.browse_files)
        self.layout.addWidget(self.drop_zone)
        
        self.file_list = FileList(drag_drop=drag_drop)
        self.layout.addWidget(self.file_list, stretch=1)
        
        self.options_frame = QFrame()
        self.options_layout = QVBoxLayout()
        self.options_layout.setContentsMargins(0, 8, 0, 8)
        self.options_frame.setLayout(self.options_layout)
        self.layout.addWidget(self.options_frame)
        self.setup_options()
        
        action_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Clear All")
        self.btn_clear.setToolTip("Remove all files from list (Delete)")
        self.btn_clear.setFixedHeight(40)
        self.btn_clear.clicked.connect(self.file_list.clear_files)
        
        self.btn_process = AccentButton("Process")
        self.btn_process.setToolTip("Start conversion (Enter)")
        self.btn_process.clicked.connect(self.start_process)
        
        action_layout.addWidget(self.btn_clear)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_process)
        self.layout.addLayout(action_layout)
        
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(8)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.CAPTION_SIZE};")
        self.status_label.hide()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        self.layout.addLayout(progress_layout)
        
        self.setLayout(self.layout)

        # Keyboard Shortcuts [ID-010]
        QShortcut(QKeySequence("Return"), self, self.start_process)
        QShortcut(QKeySequence("Enter"), self, self.start_process)
        QShortcut(QKeySequence("Delete"), self, self.file_list.clear_files)
        QShortcut(QKeySequence("Ctrl+O"), self, self.browse_files)
        
    def setup_options(self):
        pass
        
    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*.*)")
        if files:
            self.on_files_dropped(files)
            
    def on_files_dropped(self, files):
        self.file_list.add_files(files)
        
    def start_process(self):
        pass
        
    def set_processing_state(self, is_processing):
        """Enable or disable UI elements during processing to prevent race conditions."""
        self.btn_process.setEnabled(not is_processing)
        self.btn_clear.setEnabled(not is_processing)
        self.drop_zone.setEnabled(not is_processing)
        # Options frame might contain interactive widgets
        self.options_frame.setEnabled(not is_processing)
        
    def request_overwrite_permission(self, path):
        """Show a dialog asking the user how to handle existing files."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("File Exists")
        msg.setText(f"The file '{os.path.basename(path)}' already exists.")
        msg.setInformativeText("What would you like to do?")
        
        btn_overwrite = msg.addButton("Overwrite", QMessageBox.ButtonRole.DestructiveRole)
        btn_rename = msg.addButton("Auto-rename", QMessageBox.ButtonRole.AcceptRole)
        btn_cancel = msg.addButton(QMessageBox.StandardButton.Cancel)
        
        msg.exec()
        
        if msg.clickedButton() == btn_overwrite:
            return 'overwrite'
        elif msg.clickedButton() == btn_rename:
            return 'rename'
        else:
            return 'cancel'

    def show_success(self, output_path):
        self.set_processing_state(False)
        self.progress_bar.setValue(100)
        self.status_label.setText("Complete!")
        self.animate_message_box(output_path)
        
    def animate_message_box(self, output_path):
        msg = QMessageBox(self)
        msg.setIconPixmap(qta.icon('fa5s.check-circle', color=Colors.SUCCESS).pixmap(48, 48))
        msg.setWindowTitle("Success")
        msg.setText("Operation completed successfully!")

        btn_open = AccentButton("Open Folder")
        msg.addButton(btn_open, QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Ok)

        msg.exec()
        if msg.clickedButton() == btn_open:
            if os.path.isfile(output_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(output_path)))
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

        self.progress_bar.hide()
        self.status_label.hide()
        self.status_label.setText("")

    def show_error(self, error_msg):
        self.set_processing_state(False)
        self.progress_bar.hide()
        self.status_label.hide()
        msg = QMessageBox(self)
        msg.setIconPixmap(qta.icon('fa5s.times-circle', color=Colors.DANGER).pixmap(48, 48))
        msg.setWindowTitle("Error")
        msg.setText(str(error_msg))
        msg.exec()
