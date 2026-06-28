from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QSplitter, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent
from .sidebar import Sidebar
from ui.theme import Colors, Typography, Radius

from .pages.merge_page import MergePage
from .pages.split_page import SplitPage
from .pages.pdf_to_image_page import PdfToImagePage
from .pages.image_to_pdf_page import ImageToPdfPage
from .pages.pdf_to_word_page import PdfToWordPage
from .pages.word_to_pdf_page import WordToPdfPage
# Updated mapping to match new sidebar items
from .pages.pdf_to_excel_page import PdfToExcelPage
from .pages.excel_to_pdf_page import ExcelToPdfPage
from .pages.compress_page import CompressPage
from .pages.ocr_page import OcrPage

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: transparent;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        # macOS style window buttons
        self.btn_close = QPushButton()
        self.btn_min = QPushButton()
        self.btn_max = QPushButton()
        
        for btn, color in [(self.btn_close, Colors.DANGER), (self.btn_min, Colors.WARNING), (self.btn_max, Colors.SUCCESS)]:
            btn.setFixedSize(12, 12)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 6px;
                    border: none;
                }}
            """)
            layout.addWidget(btn)
            
        self.btn_close.clicked.connect(self.parent.close)
        self.btn_min.clicked.connect(self.parent.showMinimized)
        self.btn_max.clicked.connect(self.toggle_max)
        
        layout.addStretch()
        
        self.title_label = QLabel("Aldy Converter")
        self.title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 500; font-family: {Typography.FAMILY}; font-size: 14px;")
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Spacer for centering
        spacer = QWidget()
        spacer.setFixedWidth(60)
        layout.addWidget(spacer)
        
        self.start_pos = None

    def toggle_max(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.start_pos:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.pos() + delta)
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.start_pos = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aldy Converter")
        self.resize(1100, 700)
        self.setMinimumSize(1000, 650)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        main_container = QWidget()
        main_container.setStyleSheet(f"""
            QWidget#MainContainer {{
                background-color: {Colors.BASE_BG};
                border-radius: {Radius.LARGE};
            }}
        """)
        main_container.setObjectName("MainContainer")
        self.setCentralWidget(main_container)
        
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        self.title_bar = TitleBar(self)
        container_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        self.stacked_widget = QStackedWidget()
        self.setup_pages()
        right_layout.addWidget(self.stacked_widget)
        
        status_bar = QWidget()
        status_bar.setFixedHeight(28)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(24, 0, 24, 0)
        status_bar.setStyleSheet("background-color: transparent;")
        
        ready_label = QLabel("Ready")
        ready_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 11px; font-weight: 500;")
        status_layout.addWidget(ready_label)
        
        status_layout.addStretch()
        
        indicator = QLabel()
        indicator.setFixedSize(8, 8)
        indicator.setStyleSheet(f"background-color: {Colors.SUCCESS}; border-radius: 4px;")
        status_layout.addWidget(indicator)
        
        self.version_label = QLabel("v1.0.0")
        self.version_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 11px; font-weight: 500;")
        status_layout.addWidget(self.version_label)
        
        right_layout.addWidget(status_bar)
        main_layout.addWidget(right_widget)
        
        container_layout.addWidget(content_widget)
        
        self.sidebar.page_selected.connect(self.transition_page)
        self.sidebar.select_first()
        
    def transition_page(self, index):
        if index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)

    def closeEvent(self, event):
        """Handle window close by stopping active workers."""
        active_workers = []
        for i in range(self.stacked_widget.count()):
            page = self.stacked_widget.widget(i)
            if hasattr(page, 'worker') and page.worker and page.worker.isRunning():
                active_workers.append(page.worker)
        
        if active_workers:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                "Conversion is still in progress. Cancel and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                for worker in active_workers:
                    worker.requestInterruption()
                    worker.quit()
                    worker.wait(2000) # Wait up to 2s per worker
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def setup_pages(self):
        # Must match features_set1 + features_set2 in sidebar.py
        self.stacked_widget.addWidget(MergePage())      # 0
        self.stacked_widget.addWidget(SplitPage())      # 1
        self.stacked_widget.addWidget(PdfToImagePage()) # 2
        self.stacked_widget.addWidget(ImageToPdfPage()) # 3
        self.stacked_widget.addWidget(PdfToWordPage())  # 4
        self.stacked_widget.addWidget(WordToPdfPage())  # 5
        self.stacked_widget.addWidget(PdfToExcelPage()) # 6
        self.stacked_widget.addWidget(ExcelToPdfPage()) # 7
        self.stacked_widget.addWidget(CompressPage())   # 8
        self.stacked_widget.addWidget(OcrPage())        # 9
