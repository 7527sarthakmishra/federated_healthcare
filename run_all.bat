@echo off
echo ========================================================
echo Starting FedHealth Full-Stack Platform...
echo ========================================================
start "FedHealth Backend API (Port 8000)" cmd /k "%~dp0run_backend.bat"
timeout /t 3 /nobreak >nul
start "FedHealth React UI (Port 3000)" cmd /k "%~dp0run_frontend.bat"
echo FedHealth Platform launched!
echo Backend Docs: http://localhost:8000/docs
echo Frontend App: http://localhost:3000
