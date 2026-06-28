from ui.pages.base_page import BasePage
from core.pdf_office import pdf_to_word
from core.utils import check_overwrite
from workers.conversion_worker import ConversionWorker
from PyQt6.QtWidgets import QFileDialog, QLabel

class PdfToWordPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("PDF to Word", "Convert PDF to editable DOCX format. Best for text-based PDFs.", parent)
        
        warn = QLabel("Note: Scanned PDFs require OCR first. This tool works best for native digital PDFs.")
        warn.setStyleSheet("color: #ff9800; font-style: italic;")
        self.layout.insertWidget(2, warn)
        
    def start_process(self):
        files = self.file_list.get_files()
        if not files: return self.show_error("Please add a PDF file.")
        if len(files) > 1: return self.show_error("Please select only one file.")
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Word Document", "document.docx", "Word Files (*.docx)")
        if not output_path: return

        # ID-004: Silent overwrite fix
        output_path, proceed = check_overwrite(output_path, self.request_overwrite_permission)
        if not proceed: return
        
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.set_processing_state(True)
        
        self.worker = ConversionWorker(pdf_to_word, files[0], output_path)
        self.worker.progress.connect(lambda p, t: (self.progress_bar.setValue(p), self.status_label.setText(t)))
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    def on_finished(self, success, result):
        if success: self.show_success(result)
        else: self.show_error(result)