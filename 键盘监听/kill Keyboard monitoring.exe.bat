@echo off
mode con cols=100 lines=100&color 0a 
title Kill Keyboard monitoring.exe
echo Do you want to kill Keyboard monitoring.exe ?
pause

:kill
TASKKILL /F /IM "Keyboard monitoring.exe"

echo again?
pause
goto kill
