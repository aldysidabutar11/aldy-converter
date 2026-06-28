[ID-001] [CRITICAL] Race condition crash — Fixed by disabling UI during processing in base_page.py and all subclasses.
[ID-002] [CRITICAL] Missing Ghostscript in build — Added Ghostscript to assets and configured path in main.py.
[ID-011] [HIGH] Missing Build Assets Directory — Created assets structure and provided fallback icon.
[ID-005] [HIGH] UPX antivirus — Disabled UPX in spec file to prevent false-positives.
[ID-003] [CRITICAL] File handle & memory leak — Refactored all fitz.open() calls to use context managers in core/.
[ID-004] [HIGH] Silent Data Overwrite — Added overwrite protection and auto-rename helper in core/utils.py and implemented across all pages.
[ID-006] [HIGH] Vulnerable dependencies — Upgraded pillow, cryptography, urllib3, etc. and froze versions in requirements.txt.
[ID-007] [MEDIUM] Application hang on window close — Implemented closeEvent confirmation and QThread interruption checks in engine loops.
[ID-008] [MEDIUM] Empty catch blocks — Replaced bare except and empty catches with proper logging in core/.
[ID-009] [MEDIUM] Unused f-string prefix — Cleaned up unnecessary f-prefixes from static strings in UI components.
[ID-014] [LOW] Insecure Temporary File Creation — Refactored core modules to use the tempfile module for secure and unique temporary file handling.
[ID-012] [MEDIUM] Package formalization — Added __init__.py files to all subdirectories to resolve duplicate module resolution issues.
[ID-010] [LOW] Keyboard shortcuts — Added support for Enter (Process), Delete (Clear All), and Ctrl+O (Browse) across all pages.
[ID-013] [LOW] Code cleanup — Removed unused imports and variables from UI modules.
