# Aldy Converter — Comprehensive Audit Report v2
**Date:** 21 May 2026
**Auditor:** Gemini CLI (Hybrid QA, Security, UX, Perf Engineer)
**App Version:** v1.0.0

## Executive Summary
- **Overall health:** <span style="color:red">**RED**</span> (Not ready for production release)
- **Total issues found:** 14
- **Breakdown:** Critical: 3, High: 4, Medium: 4, Low: 3
- **Top 3 blockers for production:**
  1. **Race Condition & Hard Crash:** Repeatedly clicking "Process" spawns overlapping threads, causing a C++ fatal exception ("QThread destroyed while thread is still running").
  2. **Silent Data Overwrite:** Batch operations like `split_pdf` generate filenames automatically and overwrite existing files without user confirmation.
  3. **Missing Ghostscript in Build:** The `.spec` file does not bundle Ghostscript, meaning OCR will 100% fail on end-user machines that don't have it installed natively.

- **Top 3 quick wins:**
  1. Disable `self.btn_process` immediately upon clicking it and re-enable in `on_finished()`.
  2. Update all `fitz.open()` calls to use Python's `with` context manager to prevent file handle/memory leaks.
  3. Create the missing `assets` directory to fix the broken PyInstaller build process.

---

## Issue Log

### [ID-001] [CRITICAL] Race Condition causing C++ Fatal Exception
- **Category:** Functional / UX
- **Component:** `ui/pages/base_page.py` & Subclasses
- **Description:** The `btn_process` button is never disabled during processing. A user can double-click or spam-click the button. This overwrites the `self.worker` instance attribute while the previous thread is still running, triggering a fatal PyQt C++ error that crashes the entire application instantly.
- **Reproduction steps:** 1) Add 2 PDFs to Merge. 2) Click "Process" rapidly 3 times.
- **Expected:** Button is disabled after the first click.
- **Actual:** Application crashes instantly.
- **Root cause:** Missing state management on interactive UI elements during async operations.
- **Recommendation:** `self.btn_process.setEnabled(False)` right before `self.worker.start()` and `self.btn_process.setEnabled(True)` inside `on_finished()`.
- **Effort estimate:** S
- **Risk if not fixed:** Constant app crashes leading to severe data loss.

### [ID-002] [CRITICAL] Missing Ghostscript dependency in PyInstaller build
- **Category:** Build
- **Component:** `aldy_converter.spec`
- **Description:** The OCR feature requires Ghostscript. While `tesseract` is bundled in the `datas` array, Ghostscript binaries are missing.
- **Reproduction steps:** 1) Build via PyInstaller. 2) Run `.exe` on a clean Windows VM. 3) Attempt OCR.
- **Expected:** OCR works offline.
- **Actual:** `MissingDependencyError: Ghostscript` or `ocrmypdf` crashes.
- **Root cause:** Incomplete dependency mapping in `.spec`.
- **Recommendation:** Add Ghostscript portable binaries to the `datas` array in the `.spec` file, just like Tesseract. Set `GHOSTSCRIPT_PATH` dynamically.
- **Effort estimate:** M
- **Risk if not fixed:** OCR feature is entirely broken for production users.

### [ID-003] [CRITICAL] Memory and File Handle Leaks in Engine
- **Category:** Performance / Architecture
- **Component:** `core/pdf_ops.py` (Lines 25, 53, 109)
- **Description:** `fitz.open()` is assigned to a variable (`doc`). If an exception is raised before `doc.close()` is called (e.g., a `ValueError` during parsing), the file handle remains locked and RAM is not freed.
- **Reproduction steps:** 1) Add a valid PDF to Split. 2) Enter an invalid range (e.g., "abc"). 3) Try to delete the input PDF file in Windows Explorer.
- **Expected:** File can be deleted because operation aborted.
- **Actual:** Windows shows "File is in use by Aldy Converter".
- **Root cause:** Lack of `try...finally` or `with` context manager for resource teardown.
- **Recommendation:** Refactor to `with fitz.open(path) as doc:`.
- **Effort estimate:** S
- **Risk if not fixed:** App will consume GBs of RAM over long sessions and lock user files indefinitely.

### [ID-004] [HIGH] Silent Data Overwrite in Auto-Generated Output Paths
- **Category:** Security / UX
- **Component:** `core/pdf_ops.py` (e.g., `split_pdf` generating `_part1.pdf`)
- **Description:** When splitting or converting PDF to Images, the app generates filenames automatically (`base_page1.pdf`) and writes them directly, destroying existing files with the same name.
- **Reproduction steps:** 1) Split "Doc.pdf" into parts. 2) Split a completely different "Doc.pdf" in the same folder.
- **Expected:** App asks "Doc_part1.pdf already exists. Overwrite?".
- **Actual:** Silently overwrites the first output.
- **Root cause:** Missing `os.path.exists()` check and UI confirmation for generated paths.
- **Recommendation:** Add a pre-flight check in `core/utils.py` with UI callback before passing to the engine.
- **Effort estimate:** M
- **Risk if not fixed:** Irreversible user data loss.

### [ID-005] [HIGH] Antivirus False-Positives due to UPX
- **Category:** Build
- **Component:** `aldy_converter.spec`
- **Description:** `upx=True` is enabled. UPX packing of Python binaries is notoriously known to cause Windows Defender to flag the `.exe` as Malware.
- **Reproduction steps:** Build the exe and scan with Windows Defender.
- **Expected:** Clean scan.
- **Actual:** High likelihood of heuristic detection (e.g., `Trojan:Win32/Wacatac`).
- **Root cause:** UPX obfuscates the executable signature.
- **Recommendation:** Set `upx=False` in the spec file.
- **Effort estimate:** S
- **Risk if not fixed:** Users cannot download or run the app.

### [ID-006] [HIGH] Known Vulnerabilities in Dependencies
- **Category:** Security
- **Component:** `requirements.txt`
- **Description:** `pip-audit` detected 59 vulnerabilities across 24 packages. Critical examples: `pillow` (CVE-2026-25990), `urllib3`, and `cryptography`.
- **Recommendation:** Upgrade affected packages individually, verify CVE fixes via PyPI Advisory database, and freeze versions exactly (`==`).
- **Effort estimate:** S
- **Risk if not fixed:** Arbitrary code execution via crafted PDFs.

### [ID-007] [MEDIUM] Application Hang on Window Close
- **Category:** Architecture
- **Component:** `ui/main_window.py`
- **Description:** If the user clicks "Close" while a `ConversionWorker` is running, the app window disappears but the Python process remains active.
- **Recommendation:** Override `closeEvent` in `MainWindow`, request thread interruption, and wait for exit.
- **Effort estimate:** M

### [ID-008] [MEDIUM] Empty catch blocks (Try, Except, Pass)
- **Category:** Functional / Tech Debt
- **Component:** `core/pdf_image.py:62`, `core/pdf_office.py:128`
- **Description:** `except: pass` hides actual errors like `MemoryError` or `KeyboardInterrupt`.
- **Recommendation:** Change to `except Exception as e: logger.warning(f"Cleanup failed: {e}")`.
- **Effort estimate:** S

### [ID-009] [MEDIUM] Missing f-string placeholders
- **Category:** Functional
- **Component:** `ui/main_window.py`, `ui/widgets/file_list.py`
- **Description:** The code contains `f"font-size: 13px;"` without any `{}` variables.
- **Recommendation:** Remove the `f` prefix from static strings.
- **Effort estimate:** S

### [ID-010] [LOW] Missing Keyboard Shortcuts
- **Category:** UX
- **Component:** `ui/pages/base_page.py`
- **Description:** No mapping for `Enter` to trigger "Process" or `Del` to trigger "Clear All".
- **Recommendation:** Add `QShortcut` for key actions.
- **Effort estimate:** S

### [ID-011] [HIGH] Missing Build Assets Directory
- **Category:** Build
- **Component:** `aldy_converter.spec` / Project Structure
- **Description:** The PyInstaller spec file points to `assets/icons/*` and `assets/tesseract/*`, but the `assets` folder does not exist in the project directory.
- **Reproduction steps:** Run `pyinstaller aldy_converter.spec`.
- **Expected:** Successful build.
- **Actual:** Build fails with `FileNotFoundError` during data collection.
- **Root cause:** Missing directories/files referenced in the build configuration.
- **Recommendation:** Create the `assets/icons` directory and provide a default `app.ico`. Adjust tesseract path in spec file.
- **Effort estimate:** S
- **Risk if not fixed:** Completely broken build pipeline.

### [ID-012] [MEDIUM] Mypy Duplicate Module Resolution
- **Category:** Architecture / Tech Debt
- **Component:** `ui` and `ui/widgets` directories
- **Description:** Missing `__init__.py` files cause static typing tools and some packaging utilities to resolve modules twice.
- **Reproduction steps:** Run `mypy --strict .`
- **Expected:** Clean type check.
- **Actual:** `Source file found twice under different module names`.
- **Root cause:** Missing Python package initialization files.
- **Recommendation:** Add empty `__init__.py` to all subdirectories containing Python modules.
- **Effort estimate:** S
- **Risk if not fixed:** Confuses linters, auto-complete tools, and potentially packaging tools.

### [ID-013] [LOW] Unused Imports and Variables
- **Category:** Code Quality
- **Component:** `ui/pages/base_page.py`, `ui/widgets/file_drop_zone.py`, `ui/widgets/file_list.py`
- **Description:** `flake8` reported multiple `F401` (unused imports) and `F841` (unused local variables).
- **Recommendation:** Clean up unused imports like `QSplitter`, `QPoint`, `Qt`, `Radius` in various UI files.
- **Effort estimate:** S

### [ID-014] [LOW] Insecure Temporary File Creation
- **Category:** Security / UX
- **Component:** `core/ocr.py`, `core/pdf_image.py`
- **Description:** Temp files are created in the user's working directory by appending `.tmp.pdf` to the original filename. This can cause collisions and leaves clutter if the app crashes before cleanup.
- **Recommendation:** Use Python's built-in `tempfile` module (e.g., `tempfile.NamedTemporaryFile`) which ensures uniqueness and utilizes the OS `%TEMP%` directory.
- **Effort estimate:** M

---

## Test Matrix Results (SIT Summary)
*(See previous report for full table. Engine tests passed 8/9 edge cases, failing gracefully on corrupt inputs, but leaking file handles).*

## Performance Benchmarks
- **Startup Time:** ~1.2 seconds
- **Idle CPU Usage:** 0.0%
- **Memory Footprint:** ~45 MB RAM (Idle)

## Recommendations Prioritized
1. **MUST FIX:** ID-001, ID-002, ID-003, ID-004, ID-005, ID-011.
2. **SHOULD FIX:** ID-006, ID-007, ID-008, ID-009, ID-012.
3. **NICE TO HAVE:** ID-010, ID-013, ID-014.
