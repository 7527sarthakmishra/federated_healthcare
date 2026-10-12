@echo off
echo ========================================================
echo Starting FedHealth FastAPI Backend Server (Port 8000)...
echo ========================================================
cd /d "%~dp0\backend"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
