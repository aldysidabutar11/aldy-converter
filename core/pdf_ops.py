import fitz
import os
import io
from PIL import Image
from .exceptions import PDFCorruptedError
from .logger import logger

from PyQt6.QtCore import QThread

def validate_pdf(path):
    try:
        with fitz.open(path) as doc:
            if doc.needs_pass:
                raise PDFCorruptedError(f"File {os.path.basename(path)} is encrypted.")
    except Exception as e:
        if isinstance(e, PDFCorruptedError):
            raise
        raise PDFCorruptedError(f"Invalid or corrupted PDF: {os.path.basename(path)}")

def merge_pdfs(file_paths, output_path, progress_cb=None):
    with fitz.open() as merged_doc:
        total = len(file_paths)
        for i, path in enumerate(file_paths):
            if QThread.currentThread().isInterruptionRequested():
                return None
            if progress_cb: progress_cb(int((i/total)*90), f"Merging {os.path.basename(path)}...")
            validate_pdf(path)
            with fitz.open(path) as doc:
                merged_doc.insert_pdf(doc)
        if progress_cb: progress_cb(90, "Saving merged file...")
        merged_doc.save(output_path)
    if progress_cb: progress_cb(100, "Done")
    return output_path

def parse_pages(value, max_page):
    pages = set()
    for part in value.split(','):
        part = part.strip()
        if not part: continue
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                pages.update(range(max(1, start), min(max_page, end) + 1))
            except ValueError:
                pass
        elif part.isdigit():
            p = int(part)
            if 1 <= p <= max_page:
                pages.add(p)
    return sorted(list(pages))

def split_pdf(file_path, output_dir, mode, value, progress_cb=None):
    validate_pdf(file_path)
    with fitz.open(file_path) as doc:
        total_pages = len(doc)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_files = []
        
        if mode == "range":
            pages = parse_pages(value, total_pages)
            if not pages:
                raise ValueError("Invalid page range")
            with fitz.open() as new_doc:
                for p in pages:
                    if QThread.currentThread().isInterruptionRequested():
                        return None
                    new_doc.insert_pdf(doc, from_page=p-1, to_page=p-1)
                out_path = os.path.join(output_dir, f"{base_name}_split.pdf")
                if progress_cb: progress_cb(80, "Saving...")
                new_doc.save(out_path)
                output_files.append(out_path)
            
        elif mode == "every":
            try:
                n = int(value)
            except ValueError:
                raise ValueError("Interval must be an integer")
            if n < 1:
                raise ValueError("Interval must be at least 1")
            parts = total_pages // n + (1 if total_pages % n != 0 else 0)
            for i in range(parts):
                if QThread.currentThread().isInterruptionRequested():
                    return None
                start = i * n
                end = min((i + 1) * n - 1, total_pages - 1)
                with fitz.open() as new_doc:
                    new_doc.insert_pdf(doc, from_page=start, to_page=end)
                    out_path = os.path.join(output_dir, f"{base_name}_part{i+1}.pdf")
                    if progress_cb: progress_cb(int((i/parts)*90), f"Saving part {i+1}...")
                    new_doc.save(out_path)
                    output_files.append(out_path)
                
        elif mode == "specific":
            pages = parse_pages(value, total_pages)
            if not pages:
                raise ValueError("Invalid pages")
            for i, p in enumerate(pages):
                if QThread.currentThread().isInterruptionRequested():
                    return None
                with fitz.open() as new_doc:
                    new_doc.insert_pdf(doc, from_page=p-1, to_page=p-1)
                    out_path = os.path.join(output_dir, f"{base_name}_page{p}.pdf")
                    if progress_cb: progress_cb(int((i/len(pages))*90), f"Saving page {p}...")
                    new_doc.save(out_path)
                    output_files.append(out_path)
    
    if progress_cb: progress_cb(100, "Done")
    return output_files

def compress_pdf(file_path, output_path, level, progress_cb=None):
    validate_pdf(file_path)
    with fitz.open(file_path) as doc:
        if progress_cb: progress_cb(10, "Preparing compression...")
        
        if level == "Low":
            doc.save(output_path, garbage=4, deflate=True, clean=True)
        elif level == "Medium":
            doc.save(output_path, garbage=4, deflate=True, clean=True, linear=True)
        elif level == "High":
            for i in range(len(doc)):
                if QThread.currentThread().isInterruptionRequested():
                    return None
                if progress_cb: progress_cb(10 + int((i/len(doc))*70), f"Processing images on page {i+1}...")
                page = doc[i]
                for img in page.get_images():
                    xref = img[0]
                    try:
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        pil_img = Image.open(io.BytesIO(image_bytes))
                        if pil_img.mode in ("RGBA", "P"):
                            pil_img = pil_img.convert("RGB")
                        out_io = io.BytesIO()
                        pil_img.save(out_io, format="JPEG", quality=60)
                        doc.update_stream(xref, out_io.getvalue())
                    except Exception as e:
                        logger.warning(f"Failed to compress image xref {xref} on page {i+1}: {e}")
            doc.save(output_path, garbage=4, deflate=True, clean=True, linear=True)
        elif level == "Extreme":
            with fitz.open() as new_doc:
                for i in range(len(doc)):
                    if QThread.currentThread().isInterruptionRequested():
                        return None
                    if progress_cb: progress_cb(10 + int((i/len(doc))*80), f"Rasterizing page {i+1}...")
                    page = doc[i]
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("jpeg")
                    new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                    new_page.insert_image(page.rect, stream=img_bytes)
                new_doc.save(output_path, garbage=4, deflate=True, clean=True, linear=True)
            
    if progress_cb: progress_cb(100, "Compression complete")
    
    orig_size = os.path.getsize(file_path)
    new_size = os.path.getsize(output_path)
    reduction = (orig_size - new_size) / orig_size * 100 if orig_size > 0 else 0
    return {"output_path": output_path, "original_size": orig_size, "new_size": new_size, "reduction": reduction}
