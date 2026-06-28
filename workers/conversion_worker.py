from PyQt6.QtCore import QThread, pyqtSignal

class ConversionWorker(QThread):
    progress = pyqtSignal(int, str)         # percent, status text
    finished = pyqtSignal(bool, object)     # success, result (str path / dict / error)
    
    def __init__(self, job_func, *args, **kwargs):
        super().__init__()
        self.job_func = job_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            # We inject the progress callback directly into the function call
            result = self.job_func(*self.args, progress_cb=self.progress.emit, **self.kwargs)
            # Some functions return a list of files or a single file path
            if isinstance(result, list) and result:
                import os
                self.finished.emit(True, os.path.dirname(result[0]))
            elif isinstance(result, (str, dict)):
                self.finished.emit(True, result)
            else:
                self.finished.emit(True, "Success")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.finished.emit(False, str(e))