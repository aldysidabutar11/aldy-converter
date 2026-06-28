import sys
import logging
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.styles import build_stylesheet
from core.logger import logger

import os

def setup_bundled_dependencies():
    """Setup environment variables for bundled Ghostscript and Tesseract if running as exe."""
    if hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
        
        # Ghostscript setup
        gs_base = os.path.join(bundle_dir, 'ghostscript')
        gs_bin = os.path.join(gs_base, 'bin')
        if os.path.exists(gs_bin):
            if gs_bin not in os.environ['PATH']:
                os.environ['PATH'] = gs_bin + os.pathsep + os.environ['PATH']
            
            # Find gswin64c.exe or gswin32c.exe
            for exe in ['gswin64c.exe', 'gswin32c.exe']:
                if os.path.exists(os.path.join(gs_bin, exe)):
                    os.environ['GSC'] = os.path.join(gs_bin, exe)
                    break
        
        # Tesseract setup handled in core/ocr.py but good to have in PATH
        tess_bin = os.path.join(bundle_dir, 'tesseract')
        if os.path.exists(tess_bin) and tess_bin not in os.environ['PATH']:
            os.environ['PATH'] = tess_bin + os.pathsep + os.environ['PATH']

def main():
    try:
        setup_bundled_dependencies()
        app = QApplication(sys.argv)
        app.setStyleSheet(build_stylesheet())
        
        window = MainWindow()
        window.show()
        
        logger.info("Application started")
        sys.exit(app.exec())
    except Exception as e:
        logger.exception("Critical error during application startup")
        print(f"Critical error: {e}")

if __name__ == "__main__":
    main()