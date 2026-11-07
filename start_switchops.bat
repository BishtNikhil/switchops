@echo off
title SwitchOps — Autonomous Incident War Room Launcher
color 0A
cls
echo ==============================================================================
echo       SWITCH OPS: AUTONOMOUS INCIDENT WAR ROOM (FLIP THE SWITCH 2026)
echo ==============================================================================
echo.
echo [1/3] Launching Switch Agent Protocol Server (Port 8765)...
start "SwitchOps Protocol Server" cmd /k "python switch_room_server.py"

echo [2/3] Waiting 2 seconds for server initialization...
timeout /t 2 /nobreak > nul

echo [3/3] Launching Web Application in Default Browser...
start "" "http://127.0.0.1:8765/room/events" > nul 2>&1
start "" "%~dp0index.html"

echo.
echo ==============================================================================
echo  ✅ SwitchOps is running!
echo  - Web Application:       %~dp0index.html
echo  - Switch Protocol Server: http://127.0.0.1:8765
echo  - SSE Stream:             http://127.0.0.1:8765/room/events
echo.
echo  To start the standalone Agent Worker:
echo    python switch_agent_worker.py
echo ==============================================================================
echo.
pause
