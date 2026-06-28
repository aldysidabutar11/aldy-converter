# Aldy Converter

Aldy Converter adalah aplikasi desktop Windows untuk mengelola dan mengonversi file PDF, dibuat dengan **Python**, **PyQt6**, dan **PyMuPDF**. Aplikasi ini meniru fungsi utama tool online seperti iLovePDF, tetapi berjalan secara lokal (offline) dengan kecepatan native.

## Fitur

- **Merge PDF** — gabungkan beberapa PDF menjadi satu (bisa diurutkan via drag & drop)
- **Split PDF** — pisah berdasarkan rentang, interval, atau halaman tertentu
- **PDF → Image** — ekspor halaman ke JPG/PNG
- **Image → PDF** — gabungkan gambar menjadi PDF
- **PDF ↔ Word** — konversi dua arah
- **PDF ↔ Excel** — ekstraksi tabel / cetak sheet ke PDF
- **Compress PDF** — 4 level kompresi (Low / Medium / High / Extreme)
- **OCR** — kenali teks dari PDF hasil scan (output PDF atau TXT)

## Prasyarat

1. **Python 3.9+** (diuji pada Python 3.11)
2. **MS Word** atau **LibreOffice** — untuk fitur Word → PDF
3. **Tesseract OCR** — untuk fitur OCR
4. **Ghostscript** — untuk OCR & sebagian kompresi (via `ocrmypdf`)

## Instalasi (Mode Pengembangan)

### 1. Clone repository
```bash
git clone <url-repo-anda>
cd aldy_converter
```

### 2. (Disarankan) Buat virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependency Python
```bash
pip install -r requirements.txt
```

### 4. Siapkan binari pihak ketiga

> ⚠️ **Penting:** Folder binari (`assets/ghostscript/`, `assets/tesseract/`, `tessdata/`) **tidak disertakan di repository** karena ukurannya besar (±300 MB) dan memiliki lisensi tersendiri. Anda harus menyiapkannya sendiri setelah clone.

**Tesseract OCR**
- Unduh Tesseract untuk Windows (mis. dari [UB-Mannheim build](https://github.com/UB-Mannheim/tesseract/wiki)).
- Aplikasi akan mendeteksi Tesseract dari salah satu lokasi berikut:
  - Terinstall di sistem (`C:\Program Files\Tesseract-OCR\tesseract.exe`), **atau**
  - Di-bundle ke `assets/tesseract/tesseract.exe` dengan data bahasa di `assets/tesseract/tessdata/`.
- Pastikan tersedia data bahasa `eng.traineddata` dan `ind.traineddata`.

**Ghostscript**
- Unduh & install [Ghostscript untuk Windows](https://ghostscript.com/releases/gsdnld.html).
- Aplikasi otomatis mendeteksinya di `C:\Program Files\gs\...`, atau Anda bisa menaruh binari di `assets/ghostscript/bin/`.

### 5. Jalankan aplikasi
```bash
python main.py
```

## Arsitektur

- **UI**: PyQt6 dengan tema gelap kustom. Setiap fitur = satu halaman di `ui/pages/`.
- **Threading**: Konversi berat berjalan di `QThread` (`ConversionWorker`) agar UI tetap responsif.
- **Modularisasi Engine**: Semua logika konversi berada di folder `core/` tanpa ketergantungan Qt, sehingga mudah diuji & dipakai ulang.

```
aldy_converter/
├── main.py                 # Entry point
├── core/                   # Engine konversi (tanpa Qt)
├── ui/                     # Antarmuka PyQt6
│   ├── pages/              # Satu file per fitur
│   └── widgets/            # Komponen UI reusable
├── workers/                # QThread worker
├── assets/                 # Binari pihak ketiga (TIDAK di-commit)
└── tessdata/               # Data Tesseract (TIDAK di-commit)
```

## Build Executable (.exe)

Gunakan PyInstaller:
```bash
pyinstaller aldy_converter.spec --clean --noconfirm
```
File hasil build berada di folder `dist/`. Pastikan binari Tesseract & Ghostscript sudah ada di `assets/` agar ikut ter-bundle.

## Lisensi

Kode aplikasi ini milik pembuatnya. Binari pihak ketiga (Ghostscript, Tesseract) memiliki lisensinya masing-masing (AGPL / Apache 2.0) dan tidak didistribusikan bersama repository ini.
