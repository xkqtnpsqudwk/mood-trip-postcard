@echo off
setlocal enabledelayedexpansion

if not exist "%~dp0backend\venv\Scripts\activate.bat" (
    echo.
    echo ============================================================
    echo   Setting up the backend virtual environment for the first time...
    echo ============================================================
    where python >nul 2>&1
    if errorlevel 1 (
        echo.
        echo   Python was not found on PATH. Install Python 3.10+ and
        echo   make sure it's on PATH, then run this script again.
        echo.
        pause
        exit /b 1
    )
    call python -m venv "%~dp0backend\venv"
    if errorlevel 1 (
        echo.
        echo   Failed to create backend\venv. See the error above.
        echo.
        pause
        exit /b 1
    )
    pushd "%~dp0backend"
    call venv\Scripts\activate.bat
    call pip install -r requirements.txt
    set "PIP_RESULT=!ERRORLEVEL!"
    popd
    if not "!PIP_RESULT!"=="0" (
        echo.
        echo   Failed to install backend dependencies. See the error above.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo   Backend environment ready.
)

if not exist "%~dp0frontend\node_modules" (
    echo.
    echo ============================================================
    echo   Installing frontend dependencies for the first time...
    echo ============================================================
    where npm >nul 2>&1
    if errorlevel 1 (
        echo.
        echo   npm was not found on PATH. Install Node.js and make
        echo   sure it's on PATH, then run this script again.
        echo.
        pause
        exit /b 1
    )
    pushd "%~dp0frontend"
    call npm install
    set "NPM_RESULT=!ERRORLEVEL!"
    popd
    if not "!NPM_RESULT!"=="0" (
        echo.
        echo   Failed to install frontend dependencies. See the error above.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo   Frontend dependencies ready.
)

set "ENV_FILE=%~dp0backend\.env"
set "KEY_FOUND="

if exist "%ENV_FILE%" (
    for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
        if /i "%%A"=="OPENAI_API_KEY" if not "%%B"=="" set "KEY_FOUND=1"
    )
)

if not defined KEY_FOUND (
    echo.
    echo ============================================================
    echo   OPENAI_API_KEY is missing from backend\.env
    echo.
    echo   This app needs an OpenAI API key for mood analysis,
    echo   preference extraction, postcard image generation, and
    echo   final trip postcard generation. This part can't be
    echo   automated - you need your own key.
    echo.
    echo   1. Create an OpenAI API key in your OpenAI account
    echo   2. Create/edit backend\.env and add this line:
    echo        OPENAI_API_KEY=sk-...
    echo   3. Optional model overrides:
    echo        OPENAI_TEXT_MODEL=gpt-5.4
    echo        OPENAI_IMAGE_MODEL=gpt-image-1.5
    echo ============================================================
    echo.
    pause
)

echo Starting MoodTrip dev servers...

start "MoodTrip - Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && uvicorn main:app --reload --host 127.0.0.1 --port 8000"

start "MoodTrip - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Backend:  http://127.0.0.1:8000/docs
echo Frontend: http://127.0.0.1:5173
echo.
echo Two new windows were opened. Close them to stop the servers.
