from ui.pages.base_page import BasePage
from core.pdf_office import word_to_pdf, check_word_installed, check_libreoffice_installed
from core.utils import check_overwrite
from workers.conversion_worker import ConversionWorker
from PyQt6.QtWidgets import QFileDialog, QLabel

class WordToPdfPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Word to PDF", "Convert Word DOC/DOCX to PDF format.", parent)
        
        has_word = check_word_installed()
        has_lo = check_libreoffice_installed()
        
        if not has_word and not has_lo:
            self.btn_process.setEnabled(False)
            self.btn_process.setToolTip("Requires MS Word or LibreOffice to be installed.")
            warn = QLabel("Warning: Neither MS Word nor LibreOffice found. Feature disabled.")
            warn.setStyleSheet("color: #ff4444; font-weight: bold;")
            self.layout.insertWidget(2, warn)
            
    def start_process(self):
        files = self.file_list.get_files()
        if not files: return self.show_error("Please add a Word file.")
        if len(files) > 1: return self.show_error("Please select only one file.")
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "document.pdf", "PDF Files (*.pdf)")
        if not output_path: return

        # ID-004: Silent overwrite fix
        output_path, proceed = check_overwrite(output_path, self.request_overwrite_permission)
        if not proceed: return
        
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.set_processing_state(True)
        
        self.worker = ConversionWorker(word_to_pdf, files[0], output_path)
        self.worker.progress.connect(lambda p, t: (self.progress_bar.setValue(p), self.status_label.setText(t)))
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    def on_finished(self, success, result):
        if success: self.show_success(result)
        else: self.show_error(result)