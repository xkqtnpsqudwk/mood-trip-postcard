@echo off
setlocal enabledelayedexpansion

echo Stopping MoodTrip dev servers...

taskkill /FI "WINDOWTITLE eq MoodTrip - Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq MoodTrip - Frontend*" /T /F >nul 2>&1

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /PID %%P /F >nul 2>&1
)

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /PID %%P /F >nul 2>&1
)

echo Done. Backend (8000) and frontend (5173) stopped if they were running.
