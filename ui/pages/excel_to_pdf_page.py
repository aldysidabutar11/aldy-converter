from ui.pages.base_page import BasePage
from core.pdf_office import excel_to_pdf
from core.utils import check_overwrite
from workers.conversion_worker import ConversionWorker
from PyQt6.QtWidgets import QFileDialog

class ExcelToPdfPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Excel to PDF", "Convert Excel spreadsheets to PDF format.", parent)
        
    def start_process(self):
        files = self.file_list.get_files()
        if not files: return self.show_error("Please add an Excel file.")
        if len(files) > 1: return self.show_error("Please select only one file.")
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "spreadsheet.pdf", "PDF Files (*.pdf)")
        if not output_path: return

        # ID-004: Silent overwrite fix
        output_path, proceed = check_overwrite(output_path, self.request_overwrite_permission)
        if not proceed: return
        
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.set_processing_state(True)
        
        self.worker = ConversionWorker(excel_to_pdf, files[0], output_path)
        self.worker.progress.connect(lambda p, t: (self.progress_bar.setValue(p), self.status_label.setText(t)))
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    def on_finished(self, success, result):
        if success: self.show_success(result)
        else: self.show_error(result)