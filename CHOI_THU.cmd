@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  py -3 Tools\PlayablePreview\server.py --open
) else (
  python Tools\PlayablePreview\server.py --open
)
if errorlevel 1 (
  echo.
  echo Khong khoi dong duoc. Can Python 3.10 tro len. Cong mac dinh: 8090.
  pause
)
