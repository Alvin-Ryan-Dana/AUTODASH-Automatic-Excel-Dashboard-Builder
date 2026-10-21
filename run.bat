@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Membuat virtual environment AutoDash...
  py -3.11 -m venv .venv
  if errorlevel 1 (
    echo Gagal membuat virtual environment. Pastikan Python 3.11 terpasang.
    pause
    exit /b 1
  )
)
call ".venv\Scripts\activate.bat"
python -m pip show streamlit >nul 2>&1
if errorlevel 1 (
  echo Memasang dependensi...
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Instalasi dependensi gagal. Periksa koneksi internet dan requirements.txt.
    pause
    exit /b 1
  )
)
streamlit run app.py
