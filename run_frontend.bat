@echo off
echo ========================================================
echo Starting FedHealth React Frontend (Port 3000)...
echo ========================================================
cd /d "%~dp0\frontend"
if not exist node_modules (
    echo Installing node dependencies...
    call npm install
)
call npm start
pause
