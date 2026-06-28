import os
import sys
import shutil
import ocrmypdf
from .exceptions import DependencyMissingError

def get_tesseract_path():
    if hasattr(sys, '_MEIPASS'):
        tess_path = os.path.join(sys._MEIPASS, 'tesseract', 'tesseract.exe')
        if os.path.exists(tess_path):
            return tess_path
    
    # Check PATH
    path = shutil.which("tesseract")
    if path:
        return path
        
    # Check common Windows paths
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Tesseract-OCR", "tesseract.exe"),
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p
            
    return None

def check_ghostscript_installed():
    if shutil.which("gs") or shutil.which("gswin64c") or shutil.which("gswin32c"):
        return True
    
    # Check common Windows paths
    gs_base = r"C:\Program Files\gs"
    if os.path.exists(gs_base):
        for root, dirs, files in os.walk(gs_base):
            if "gswin64c.exe" in files or "gswin32c.exe" in files:
                return True
    return False

def check_tesseract_installed():
    return get_tesseract_path() is not None

def ocr_pdf(file_path, output_path, lang='ind+eng', output_mode='pdf', progress_cb=None):
    tess_path = get_tesseract_path()
    if not tess_path:
        raise DependencyMissingError("Tesseract OCR is not installed or bundled.")
        
    if progress_cb: progress_cb(10, "Starting OCR process...")
    
    # Add tesseract directory to PATH so ocrmypdf can find it
    tess_dir = os.path.dirname(tess_path)
    if tess_dir not in os.environ['PATH']:
        os.environ['PATH'] = tess_dir + os.pathsep + os.environ['PATH']

    # For Ghostscript, we also need to ensure it's in PATH
    gs_base = r"C:\Program Files\gs"
    if os.path.exists(gs_base):
        for root, dirs, files in os.walk(gs_base):
            if "gswin64c.exe" in files or "gswin32c.exe" in files:
                if root not in os.environ['PATH']:
                    os.environ['PATH'] = root + os.pathsep + os.environ['PATH']
                break

    # Handle TESSDATA_PREFIX
    tessdata_path = None
    if hasattr(sys, '_MEIPASS'):
        tessdata_path = os.path.join(sys._MEIPASS, 'tesseract', 'tessdata')
    else:
        # Check local tessdata in project root
        local_tessdata = os.path.join(os.getcwd(), 'tessdata')
        if os.path.exists(local_tessdata):
            tessdata_path = local_tessdata
        else:
            # Try to find tessdata relative to tesseract_cmd
            potential_tessdata = os.path.join(os.path.dirname(tess_path), 'tessdata')
            if os.path.exists(potential_tessdata):
                tessdata_path = potential_tessdata

    if tessdata_path:
        os.environ['TESSDATA_PREFIX'] = tessdata_path
    
    kwargs = {
        'language': lang,
        'force_ocr': True,
        'progress_bar': False
    }
    
    try:
        if output_mode == 'txt':
            if progress_cb: progress_cb(40, "Extracting text...")
            import tempfile
            fd, temp_pdf = tempfile.mkstemp(suffix=".pdf")
            os.close(fd)
            try:
                ocrmypdf.ocr(file_path, temp_pdf, sidecar=output_path, **kwargs)
            finally:
                if os.path.exists(temp_pdf):
                    try:
                        os.remove(temp_pdf)
                    except Exception as e:
                        from .logger import logger
                        logger.warning(f"Failed to remove temp OCR file: {e}")
        else:
            if progress_cb: progress_cb(40, "Running OCR on PDF...")
            ocrmypdf.ocr(file_path, output_path, **kwargs)
            
        if progress_cb: progress_cb(100, "OCR complete")
        return output_path
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}")