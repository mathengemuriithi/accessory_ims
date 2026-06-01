@echo off
title Git Push - Inventory Management System
echo ========================================
echo   Pushing IMS Project to GitHub
echo ========================================
echo.

cd /d C:\Users\HP\Documents\Audacity\accessory_ims

echo [1/4] Checking status...
git status

echo.
echo [2/4] Adding all changes...
git add .

echo.
echo [3/4] Committing changes...
set /p commit_msg="Enter commit message: "
git commit -m "%commit_msg%"

echo.
echo [4/4] Pushing to GitHub...
git push

echo.
echo ========================================
echo   Push complete!
echo ========================================
pause
