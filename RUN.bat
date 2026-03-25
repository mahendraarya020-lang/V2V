@echo off
cls
color 0A
echo ========================================
echo V2V 5G RESEARCH PLATFORM
echo WINDOWS VERSION
echo ========================================
echo.
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan!
    echo Install Python dari: https://www.python.org/downloads/
    pause
    exit /b
)
echo Python: OK
echo.
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    echo Tunggu sebentar...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Gagal install dependencies!
        echo Coba manual: pip install -r requirements.txt
        pause
        exit /b
    )
    echo Dependencies: OK
) else (
    echo Dependencies: OK
)
echo.
echo ========================================
echo STARTING SERVER...
echo ========================================
echo.
echo Server akan jalan di: http://localhost:5000
echo.
echo Login dengan:
echo Username: 1101223157
echo Password: 1101223157
echo.
echo ========================================
echo JANGAN TUTUP WINDOW INI!
echo Tekan Ctrl+C untuk stop server
echo ========================================
echo.
cd backend
python app.py
pause
