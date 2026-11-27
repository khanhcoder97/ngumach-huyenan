@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Run_Playable_Alpha.ps1"
if errorlevel 1 pause
