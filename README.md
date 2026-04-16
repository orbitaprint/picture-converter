# Picture Converter (Windows 7, Python 3.8)

Offline desktop utility for:
- Image to JPG conversion (`.png`, `.webp` -> `.jpg`)
- Images to single PDF
- PDF pages to JPG files

## Key goals
- Works locally, no cloud or browser runtime
- Lightweight tkinter + ttk UI
- Python 3.8 compatible code
- Windows 7 friendly setup

## Project structure

```text
picture-converter/
├─ main.py
├─ config.py
├─ requirements.txt
├─ README.md
├─ assets/
├─ logs/
└─ app/
   ├─ __init__.py
   ├─ ui/
   │  ├─ __init__.py
   │  ├─ main_window.py
   │  └─ tabs/
   │     ├─ __init__.py
   │     ├─ image_to_jpg_tab.py
   │     ├─ images_to_pdf_tab.py
   │     └─ pdf_to_jpg_tab.py
   ├─ services/
   │  ├─ __init__.py
   │  ├─ image_converter.py
   │  └─ pdf_converter.py
   └─ utils/
      ├─ __init__.py
      ├─ dnd.py
      ├─ file_utils.py
      └─ logger.py
```

## Dependencies and why

- **Pillow 10.4.0**
  - Stable image processing for PNG/JPG/WebP.
  - Also used for creating PDF from images.
- **PyMuPDF 1.24.10**
  - Practical, fast PDF page rendering to images.
  - Needed for PDF -> JPG.
- **tkinterdnd2 0.4.2 (optional helper)**
  - Enables drag-and-drop.
  - If missing, app still works with file dialogs.

## Windows 7 compatibility notes

1. Python 3.8 itself is compatible with Windows 7 (final CPython line with Win7 support).
2. `tkinter` is included with normal Python installer.
3. `PyMuPDF` wheel support on older Windows can vary by machine/runtime:
   - If install fails, keep using image->JPG and images->PDF features.
   - For PDF->JPG fallback, use a Poppler-based workflow (`pdf2image + poppler`) in a future patch.
4. WebP support depends on Pillow build capabilities. Most wheels include it; if not, WebP files may fail with a clear error.

## Install (Windows 7 + Python 3.8)

1. Install **Python 3.8.x (64-bit recommended)** and check "Add Python to PATH".
2. Open **Command Prompt** in project folder.
3. (Recommended) Create virtual environment:

```bat
python -m venv .venv
.venv\Scripts\activate
```

4. Upgrade pip tools (best effort):

```bat
python -m pip install --upgrade pip setuptools wheel
```

5. Install dependencies:

```bat
pip install -r requirements.txt
```

## Run

```bat
python main.py
```

## Logging

- Log file: `logs/app.log`
- Errors for unsupported/corrupt files are shown in the UI and written to log file.

## MVP behavior summary

### 1) Image to JPG
- Supports `.png` and `.webp` input.
- Batch conversion.
- Drag-and-drop (if helper available) + file dialog.
- Save to same source folder or custom output folder.
- JPG quality setting.
- Safe file collision handling (`name.jpg`, `name_1.jpg`, ...).

### 2) Images to PDF
- Supports `.jpg`, `.jpeg`, `.png`, `.webp`.
- Reorder images (Move Up/Down).
- Export to user-selected PDF path.

### 3) PDF to JPG
- Converts each page to separate JPEG.
- Output naming: `page_001.jpg`, `page_002.jpg`, ...
- Quality setting.
- Collision-safe naming when destination already contains files.

## v2 roadmap (not implemented)
- Merge multiple PDFs
- Split PDF by selected pages
- Compress PDF
- Rotate PDF pages
- Folder watch mode for auto-convert
- Operation history panel
- Theme options (dark mode)
- OCR integration

## Build EXE and installer (Windows)

### Quick local build

Run from project root:

```bat
build\build_windows_release.bat
```

The script will:
1. create `.venv`
2. install build dependencies from `requirements-build.txt`
3. build `PictureConverter.exe` with PyInstaller
4. create a portable release folder in `release\PictureConverter`
5. if Inno Setup 6 is installed, build installer `release\PictureConverter-Setup.exe`

### Prerequisites for installer

Install **Inno Setup 6** (optional, only needed for setup `.exe`).
Default expected path:

`C:\Program Files (x86)\Inno Setup 6\ISCC.exe`

If Inno Setup is missing, you still get portable EXE build.

## GitHub release automation

A workflow is included in `.github/workflows/release.yml`.

- Push a tag like `v1.0.0`.
- GitHub Actions builds the app with Python 3.8 on Windows runner.
- Workflow attaches `PictureConverter-portable.zip` to GitHub Release.

### Create release tag

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Windows 7 release note

For maximum Windows 7 compatibility, build on a real Windows 7 machine (or VM) with Python 3.8.
Artifacts built on newer Windows runners usually work, but this is not guaranteed for all target PCs.

## GitHub Actions troubleshooting

If a release workflow is stuck with message `Waiting for a runner to pick up this job...`:

1. Open repository **Settings -> Actions -> General** and ensure Actions are enabled.
2. Ensure you have available GitHub Actions minutes (for private repositories).
3. Re-run workflow from Actions tab.
4. If the runner label is deprecated, use a newer image (this project uses `windows-2022`).
