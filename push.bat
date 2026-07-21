@echo off
title Git Push - Accessory IMS
echo ========================================
echo   Pushing Accessory IMS to GitHub
echo ========================================
echo.

cd /d C:\Users\HP\Documents\Audacity\accessory_ims

echo [1/6] Creating data backup...
python manage.py dumpdata core > data_backup.json
echo ✅ Backup created: data_backup.json

echo.
echo [2/6] Checking status...
git status

echo.
echo [3/6] Adding all changes...
git add .

echo.
echo [4/6] Checking what was added...
git status

echo.
echo [5/6] Committing changes...
set /p commit_msg="Enter commit message: "
git commit -m "%commit_msg%"

echo.
echo [6/6] Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo   Push complete!
echo ========================================
pause
