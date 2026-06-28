from ui.pages.base_page import BasePage
from core.pdf_image import pdf_to_image
from core.utils import check_overwrite
from workers.conversion_worker import ConversionWorker
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QSpinBox, QComboBox
import os

class PdfToImagePage(BasePage):
    def __init__(self, parent=None):
        super().__init__("PDF to Image", "Extract pages from PDF to JPG or PNG format.", parent)
        
    def setup_options(self):
        layout = QHBoxLayout()
        
        self.dpi_label = QLabel("DPI:")
        self.dpi_spinner = QSpinBox()
        self.dpi_spinner.setRange(72, 600)
        self.dpi_spinner.setValue(200)
        
        self.fmt_label = QLabel("Format:")
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["JPG", "PNG"])
        
        layout.addWidget(self.dpi_label)
        layout.addWidget(self.dpi_spinner)
        layout.addWidget(self.fmt_label)
        layout.addWidget(self.fmt_combo)
        layout.addStretch()
        
        self.options_layout.addLayout(layout)
        
    def start_process(self):
        files = self.file_list.get_files()
        if not files: return self.show_error("Please add a PDF file.")
        if len(files) > 1: return self.show_error("Please select only one file.")
        
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir: return
        
        dpi = self.dpi_spinner.value()
        fmt = self.fmt_combo.currentText()

        # ID-004: Silent overwrite fix
        base_name = os.path.splitext(os.path.basename(files[0]))[0]
        ext = fmt.lower()
        if ext == "jpg": ext = "jpeg"
        first_output = os.path.join(output_dir, f"{base_name}_page_1.{ext}")
        
        _, proceed = check_overwrite(first_output, self.request_overwrite_permission)
        if not proceed: return
        
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.set_processing_state(True)
        
        self.worker = ConversionWorker(pdf_to_image, files[0], output_dir, dpi, fmt)
        self.worker.progress.connect(lambda p, t: (self.progress_bar.setValue(p), self.status_label.setText(t)))
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    def on_finished(self, success, result):
        if success:
            self.show_success(result)
        else:
            self.show_error(result)