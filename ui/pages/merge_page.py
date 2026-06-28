from ui.pages.base_page import BasePage
from core.pdf_ops import merge_pdfs
from core.utils import check_overwrite
from workers.conversion_worker import ConversionWorker
from PyQt6.QtWidgets import QFileDialog

class MergePage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Merge PDF", "Combine multiple PDF files into one in the exact order you want. Drag to reorder.", parent, drag_drop=True)
        
    def start_process(self):
        files = self.file_list.get_files()
        if not files:
            self.show_error("Please add PDF files to merge.")
            return
        if len(files) < 2:
            self.show_error("Please add at least two PDF files to merge.")
            return
            
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "merged.pdf", "PDF Files (*.pdf)")
        if not output_path: return

        # ID-004: Silent overwrite fix (Consistency check)
        output_path, proceed = check_overwrite(output_path, self.request_overwrite_permission)
        if not proceed: return
        
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status_label.setText("Starting...")
        self.set_processing_state(True)
        
        self.worker = ConversionWorker(merge_pdfs, files, output_path)
        self.worker.progress.connect(lambda p, t: (self.progress_bar.setValue(p), self.status_label.setText(t)))
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    def on_finished(self, success, result):
        if success:
            self.show_success(result)
        else:
            self.show_error(result)