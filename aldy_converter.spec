# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/icons/*', 'assets/icons'),
        ('assets/tesseract/*', 'tesseract'),
        ('assets/tesseract/tessdata/*', 'tesseract/tessdata'),
        ('assets/ghostscript/*', 'ghostscript'),
        ('assets/ghostscript/bin/*', 'ghostscript/bin'),
        ('assets/ghostscript/lib/*', 'ghostscript/lib')
    ],
    hiddenimports=[
        'PyQt6.sip',
        'pdf2docx',
        'docx2pdf',
        'pdfplumber',
        'openpyxl',
        'reportlab',
        'ocrmypdf',
        'filetype',
        'img2pdf',
        'PIL',
        'fitz'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'numpy', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AldyConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False, # [ID-005] Disabled UPX to prevent Antivirus false-positives
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app.ico'
)
