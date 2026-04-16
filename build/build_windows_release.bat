@echo off
setlocal enabledelayedexpansion

REM Build script for Windows 7 / Python 3.8
REM Creates a portable folder build + optional Inno Setup installer.

cd /d %~dp0\..

if "%PYTHON%"=="" (
  set PYTHON=python
)

echo [1/6] Cleaning old artifacts...
if exist build\tmp rmdir /s /q build\tmp
if exist dist rmdir /s /q dist
if exist build\pyinstaller rmdir /s /q build\pyinstaller
if exist release rmdir /s /q release
mkdir release

echo [2/6] Creating virtual environment...
%PYTHON% -m venv .venv
if errorlevel 1 goto :fail

call .venv\Scripts\activate
if errorlevel 1 goto :fail

echo [3/6] Installing dependencies...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :fail

pip install -r requirements-build.txt
if errorlevel 1 goto :fail

echo [4/6] Building executable with PyInstaller...
pyinstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name PictureConverter ^
  --collect-all fitz ^
  --hidden-import PIL._tkinter_finder ^
  --distpath dist ^
  --workpath build\pyinstaller ^
  main.py
if errorlevel 1 goto :fail

echo [5/6] Preparing release folder...
mkdir release\PictureConverter
xcopy /e /i /y dist\PictureConverter release\PictureConverter >nul
copy README.md release\README.md >nul

set INSTALLER_READY=0
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
  set INSTALLER_READY=1
  echo [6/6] Building installer (.exe) with Inno Setup...
  "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build\installer.iss
) else (
  echo [6/6] Inno Setup not found. Skipping installer build.
  echo        Install Inno Setup 6 and run this script again to get setup.exe.
)

echo.
echo Build completed.
if "%INSTALLER_READY%"=="1" (
  echo Installer: release\PictureConverter-Setup.exe
)
echo Portable app: release\PictureConverter\PictureConverter.exe
exit /b 0

:fail
echo.
echo Build failed.
exit /b 1
