@echo off
setlocal EnableExtensions
cd /d "%~dp0"
chcp 65001 >nul 2>&1
color 0A
title SQL CRACK v1.0.5 (Beta)
set "PYTHON_CMD="
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" >nul 2>&1
  if not errorlevel 1 set "PYTHON_CMD=py"
)
if not defined PYTHON_CMD (
  where python >nul 2>&1
  if not errorlevel 1 (
    python -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=python"
  )
)
if not defined PYTHON_CMD (
  echo [HATA] Python 3.9+ bulunamadi.
  echo https://www.python.org/downloads/
  echo Kurarken "Add Python to PATH" secenegini isaretleyin.
  pause
  exit /b 1
)
if not exist "Start.py" (
  echo [HATA] Start.py bulunamadi. ZIP dosyasini tamamen cikarin.
  pause
  exit /b 1
)
if "%PYTHON_CMD%"=="py" (
  py -3 -u "Start.py"
) else (
  python -u "Start.py"
)
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" echo [HATA] Uygulama kodu: %RESULT%
echo.
echo Pencereyi kapatmak icin bir tusa basin.
pause >nul
exit /b %RESULT%
