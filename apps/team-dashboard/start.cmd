@echo off
rem Starts the dashboard server (if it is not running yet) and opens the window.
cd /d "%~dp0"
powershell -NoProfile -Command "try { (New-Object Net.Sockets.TcpClient('127.0.0.1',47821)).Close(); exit 0 } catch { exit 1 }"
if errorlevel 1 start "Team dashboard server" /min cmd /c "node server.js > data\server.log 2>&1"
powershell -NoProfile -Command "Start-Sleep -Milliseconds 900"
start "" msedge --app=http://127.0.0.1:47821/ --window-size=1600,950
