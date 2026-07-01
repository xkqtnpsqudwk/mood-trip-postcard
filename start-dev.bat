@echo off
setlocal enabledelayedexpansion

set "ENV_FILE=%~dp0backend\.env"
set "KEY_FOUND="

if exist "%ENV_FILE%" (
    for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
        if /i "%%A"=="NVIDIA_NIM_API_KEY" if not "%%B"=="" set "KEY_FOUND=1"
    )
)

if not defined KEY_FOUND (
    echo.
    echo ============================================================
    echo   NVIDIA_NIM_API_KEY is missing from backend\.env
    echo.
    echo   This app needs a free NVIDIA NIM API key to talk to the
    echo   AI (mood analysis, postcard text, and postcard photo^).
    echo.
    echo   1. Go to https://build.nvidia.com/ and sign in ^(free^)
    echo   2. Open any model page and click "Get API Key"
    echo   3. Create/edit backend\.env and add this line:
    echo        NVIDIA_NIM_API_KEY=nvapi-...
    echo ============================================================
    echo.
    pause
)

echo Starting Mood Trip Postcard dev servers...

start "Mood Trip Postcard - Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && uvicorn main:app --reload --host 127.0.0.1 --port 8000"

start "Mood Trip Postcard - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Backend:  http://127.0.0.1:8000/docs
echo Frontend: http://127.0.0.1:5173
echo.
echo Two new windows were opened. Close them to stop the servers.
