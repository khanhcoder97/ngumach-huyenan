@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Run_Actor_Library.ps1"
if errorlevel 1 pause
