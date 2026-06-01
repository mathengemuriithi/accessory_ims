@echo off
cd /d C:\Users\HP\Documents\Audacity\accessory_ims
call venv\Scripts\activate
cd accessory_ims
python manage.py runserver
pause
