@echo off
title Git Push - Accessory IMS
echo ========================================
echo   Pushing Accessory IMS to GitHub
echo ========================================
echo.

cd /d C:\Users\HP\Documents\Audacity\accessory_ims

echo [1/5] Checking status...
git status

echo.
echo [2/5] Adding all changes...
git add .

echo.
echo [3/5] Checking what was added...
git status

echo.
echo [4/5] Committing changes...
set /p commit_msg="Enter commit message: "
git commit -m "%commit_msg%"

echo.
echo [5/5] Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo   Push complete!
echo ========================================
pause
