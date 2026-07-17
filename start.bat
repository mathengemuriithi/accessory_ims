@echo off
echo ========================================
echo   Starting Accessory IMS Server
echo ========================================
echo.

cd /d C:\Users\HP\Documents\Audacity\accessory_ims
call venv\Scripts\activate

echo.
echo ✅ Server starting at http://127.0.0.1:8000
echo.
python manage.py runserver

echo.
echo ========================================
echo   Server stopped.
echo ========================================
pause
