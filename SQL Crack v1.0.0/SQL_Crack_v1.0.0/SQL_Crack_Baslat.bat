@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SQL Crack v1.0.0
cls
echo ==================================================
echo           SQL CRACK v1.0.0
echo           TarikPro43391
 echo ==================================================
echo.
if not exist "server.py" (
  echo [HATA] server.py dosyasi bulunamadi.
  echo Zip dosyasini tamamen cikartip tekrar deneyin.
  pause
  exit /b 1
)
set "PYTHON_CMD="
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -c "import sys; assert sys.version_info.major == 3" >nul 2>&1
  if not errorlevel 1 set "PYTHON_CMD=py"
)
if not defined PYTHON_CMD (
  where python >nul 2>&1
  if not errorlevel 1 (
    python -c "import sys; assert sys.version_info.major == 3" >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=python"
  )
)
if not defined PYTHON_CMD (
  echo [HATA] Python 3 bulunamadi.
  echo Python 3 kurup "Add Python to PATH" secenegini isaretleyin.
  echo https://www.python.org/downloads/windows/
  pause
  exit /b 1
)
if "%PYTHON_CMD%"=="py" (
  py -3 server.py
) else (
  python server.py
)
if errorlevel 1 (
  echo.
  echo [HATA] Sunucu baslatilamadi. Yukaridaki mesaji kontrol edin.
)
pause
endlocal
