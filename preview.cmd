@echo off
rem Rebuilds both sites, serves them locally and opens the preview in the default browser.
rem Close this window to stop the server.
cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1
py -3.13 build.py
if errorlevel 1 pause & exit /b 1
start "" http://127.0.0.1:8124/
cd dist
py -3.13 -m http.server 8124 --bind 127.0.0.1
