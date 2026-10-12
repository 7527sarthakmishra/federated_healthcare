@echo off
echo ========================================================
echo Running FedHealth Full Test Suite (ML + Backend APIs)...
echo ========================================================
cd /d "%~dp0"
echo 1. Testing ML & Federated Engine...
python backend/ml/test_ml_engine.py
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] ML Engine test failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo 2. Testing FastAPI Backend & Database...
python backend/test_api_suite.py
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Backend test suite failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo ALL TESTS PASSED SUCCESSFULLY!
echo ========================================================
pause
