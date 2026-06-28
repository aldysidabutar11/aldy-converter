from ui.pages.base_page import BasePage
from core.pdf_ops import split_pdf
from core.utils import check_overwrite
from workers.conversion_worker import ConversionWorker
from PyQt6.QtWidgets import QFileDialog, QRadioButton, QLineEdit, QHBoxLayout, QButtonGroup
import os

class SplitPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Split PDF", "Split PDF by range, interval, or specific pages.", parent)
        
    def setup_options(self):
        self.mode_group = QButtonGroup()
        
        lay1 = QHBoxLayout()
        self.rb_range = QRadioButton("By Range (e.g., 1-5)")
        self.rb_range.setChecked(True)
        self.txt_range = QLineEdit()
        self.txt_range.setPlaceholderText("e.g. 1-5")
        self.mode_group.addButton(self.rb_range, 1)
        lay1.addWidget(self.rb_range)
        lay1.addWidget(self.txt_range)
        
        lay2 = QHBoxLayout()
        self.rb_every = QRadioButton("Every N Pages")
        self.txt_every = QLineEdit()
        self.txt_every.setPlaceholderText("e.g. 2")
        self.mode_group.addButton(self.rb_every, 2)
        lay2.addWidget(self.rb_every)
        lay2.addWidget(self.txt_every)
        
        lay3 = QHBoxLayout()
        self.rb_specific = QRadioButton("Specific Pages (e.g., 1-3,5)")
        self.txt_specific = QLineEdit()
        self.txt_specific.setPlaceholderText("e.g. 1-3,5,7-9")
        self.mode_group.addButton(self.rb_specific, 3)
        lay3.addWidget(self.rb_specific)
        lay3.addWidget(self.txt_specific)
        
        self.options_layout.addLayout(lay1)
        self.options_layout.addLayout(lay2)
        self.options_layout.addLayout(lay3)
        
    def start_process(self):
        files = self.file_list.get_files()
        if not files: return self.show_error("Please add a PDF file to split.")
        if len(files) > 1: return self.show_error("Please select only one file for splitting.")
        
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir: return
        
        mode_id = self.mode_group.checkedId()
        if mode_id == 1:
            mode = "range"
            value = self.txt_range.text()
        elif mode_id == 2:
            mode = "every"
            value = self.txt_every.text()
        else:
            mode = "specific"
            value = self.txt_specific.text()
            
        if not value: return self.show_error("Please enter a value for the selected split mode.")

        # ID-004: Silent overwrite fix
        base_name = os.path.splitext(os.path.basename(files[0]))[0]
        if mode == "range":
            first_output = os.path.join(output_dir, f"{base_name}_split.pdf")
        elif mode == "every":
            first_output = os.path.join(output_dir, f"{base_name}_part1.pdf")
        else: # specific
            # We don't know the exact first page without parsing, but we can guess or just use a generic check
            # For simplicity, if it's specific, let's just check the first possible page if we can parse it
            from core.pdf_ops import parse_pages
            import fitz
            try:
                with fitz.open(files[0]) as doc:
                    pages = parse_pages(value, len(doc))
                    if pages:
                        first_output = os.path.join(output_dir, f"{base_name}_page{pages[0]}.pdf")
                    else:
                        return self.show_error("Invalid pages")
            except Exception as e:
                return self.show_error(str(e))

        _, proceed = check_overwrite(first_output, self.request_overwrite_permission)
        if not proceed: return
        
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.set_processing_state(True)
        
        self.worker = ConversionWorker(split_pdf, files[0], output_dir, mode, value)
        self.worker.progress.connect(lambda p, t: (self.progress_bar.setValue(p), self.status_label.setText(t)))
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    def on_finished(self, success, result):
        if success:
            self.show_success(result)
        else:
            self.show_error(result)