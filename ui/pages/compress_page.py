from ui.pages.base_page import BasePage
from core.pdf_ops import compress_pdf
from core.utils import check_overwrite
from workers.conversion_worker import ConversionWorker
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QComboBox, QMessageBox

class CompressPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Compress PDF", "Reduce the file size of your PDF.", parent)
        
    def setup_options(self):
        layout = QHBoxLayout()
        self.lvl_label = QLabel("Compression Level:")
        self.lvl_combo = QComboBox()
        self.lvl_combo.addItems(["Low", "Medium", "High", "Extreme"])
        self.lvl_combo.setCurrentText("Medium")
        
        layout.addWidget(self.lvl_label)
        layout.addWidget(self.lvl_combo)
        layout.addStretch()
        
        self.options_layout.addLayout(layout)
        
    def start_process(self):
        files = self.file_list.get_files()
        if not files: return self.show_error("Please add a PDF file.")
        if len(files) > 1: return self.show_error("Please select only one file.")
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "compressed.pdf", "PDF Files (*.pdf)")
        if not output_path: return

        # ID-004: Silent overwrite fix
        output_path, proceed = check_overwrite(output_path, self.request_overwrite_permission)
        if not proceed: return
        
        level = self.lvl_combo.currentText()
        
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.set_processing_state(True)
        
        self.worker = ConversionWorker(compress_pdf, files[0], output_path, level)
        self.worker.progress.connect(lambda p, t: (self.progress_bar.setValue(p), self.status_label.setText(t)))
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    def on_finished(self, success, result):
        if success:
            if isinstance(result, dict):
                orig = result['original_size'] / 1024 / 1024
                new = result['new_size'] / 1024 / 1024
                red = result['reduction']
                QMessageBox.information(self, "Compression Result", 
                    f"Original size: {orig:.2f} MB\n"
                    f"New size: {new:.2f} MB\n"
                    f"Reduction: {red:.2f}%")
                self.show_success(result['output_path'])
            else:
                self.show_success(result)
        else:
            self.show_error(result)