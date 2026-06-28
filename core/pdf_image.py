import fitz
import os
import img2pdf
from PIL import Image

from PyQt6.QtCore import QThread

from .logger import logger

def pdf_to_image(file_path, output_dir, dpi=200, fmt="JPG", progress_cb=None):
    from .pdf_ops import validate_pdf
    validate_pdf(file_path)
    with fitz.open(file_path) as doc:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        total_pages = len(doc)
        ext = fmt.lower()
        if ext == "jpg": ext = "jpeg"
        output_files = []
        
        for i in range(total_pages):
            if QThread.currentThread().isInterruptionRequested():
                return None
            if progress_cb: progress_cb(int((i/total_pages)*90), f"Extracting page {i+1}...")
            page = doc[i]
            pix = page.get_pixmap(dpi=dpi)
            out_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.{ext}")
            if ext == "jpeg":
                pix.save(out_path, "jpeg")
            else:
                pix.save(out_path, "png")
            output_files.append(out_path)
    if progress_cb: progress_cb(100, "Extraction complete")
    return output_files

def images_to_pdf(image_paths, output_path, progress_cb=None):
    if progress_cb: progress_cb(10, "Validating images...")
    processed_images = []
    temp_files = []
    
    total = len(image_paths)
    for i, path in enumerate(image_paths):
        if QThread.currentThread().isInterruptionRequested():
            return None
        if progress_cb: progress_cb(10 + int((i/total)*40), f"Processing image {i+1}...")
        if path.lower().endswith('.png'):
            try:
                with Image.open(path) as img:
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        rgb_img = img.convert('RGB')
                        import tempfile
                        fd, temp_path = tempfile.mkstemp(suffix=".jpg")
                        os.close(fd)
                        rgb_img.save(temp_path, "JPEG")
                        processed_images.append(temp_path)
                        temp_files.append(temp_path)
                    else:
                        processed_images.append(path)
            except Exception as e:
                logger.warning(f"Failed to process image {path}: {e}")
                processed_images.append(path)
        else:
            processed_images.append(path)
            
    if progress_cb: progress_cb(60, "Building PDF...")
    try:
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(processed_images))
    finally:
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {temp_file}: {e}")
                
    if progress_cb: progress_cb(100, "Done")
    return output_path