@echo off
setlocal enabledelayedexpansion

echo Stopping Mood Trip Postcard dev servers...

taskkill /FI "WINDOWTITLE eq Mood Trip Postcard - Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Mood Trip Postcard - Frontend*" /T /F >nul 2>&1

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /PID %%P /F >nul 2>&1
)

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /PID %%P /F >nul 2>&1
)

echo Done. Backend (8000) and frontend (5173) stopped if they were running.
