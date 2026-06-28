from ui.pages.base_page import BasePage
from core.ocr import ocr_pdf, check_tesseract_installed, check_ghostscript_installed
from core.utils import check_overwrite
from workers.conversion_worker import ConversionWorker
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QComboBox

class OcrPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("OCR PDF", "Make scanned PDFs searchable or extract text using OCR.", parent)
        
        tess = check_tesseract_installed()
        gs = check_ghostscript_installed()
        
        if not tess or not gs:
            self.btn_process.setEnabled(False)
            missing = []
            if not tess: missing.append("Tesseract OCR")
            if not gs: missing.append("Ghostscript")
            
            msg = f"Warning: {', '.join(missing)} not found. Feature disabled."
            self.btn_process.setToolTip(msg)
            warn = QLabel(msg)
            warn.setStyleSheet("color: #ff4444; font-weight: bold;")
            self.layout.insertWidget(2, warn)
            
            help_text = QLabel("Please install missing dependencies to use this feature.")
            help_text.setOpenExternalLinks(True)
            self.layout.insertWidget(3, help_text)
            
    def setup_options(self):
        layout = QHBoxLayout()
        
        self.lang_label = QLabel("Language:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["ind+eng", "eng", "ind"])
        
        self.mode_label = QLabel("Output Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Searchable PDF", "Extract to TXT"])
        
        layout.addWidget(self.lang_label)
        layout.addWidget(self.lang_combo)
        layout.addWidget(self.mode_label)
        layout.addWidget(self.mode_combo)
        layout.addStretch()
        
        self.options_layout.addLayout(layout)
        
    def start_process(self):
        files = self.file_list.get_files()
        if not files: return self.show_error("Please add a PDF file.")
        if len(files) > 1: return self.show_error("Please select only one file.")
        
        mode = "txt" if self.mode_combo.currentText() == "Extract to TXT" else "pdf"
        lang = self.lang_combo.currentText()
        
        ext = "txt" if mode == "txt" else "pdf"
        output_path, _ = QFileDialog.getSaveFileName(self, f"Save {ext.upper()}", f"ocr_output.{ext}", f"Files (*.{ext})")
        if not output_path: return

        # ID-004: Silent overwrite fix
        output_path, proceed = check_overwrite(output_path, self.request_overwrite_permission)
        if not proceed: return
        
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.set_processing_state(True)
        
        self.worker = ConversionWorker(ocr_pdf, files[0], output_path, lang, mode)
        self.worker.progress.connect(lambda p, t: (self.progress_bar.setValue(p), self.status_label.setText(t)))
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    def on_finished(self, success, result):
        if success: self.show_success(result)
        else: self.show_error(result)