@echo off
cd /d "%~dp0"

start cmd /k "cd ids-back && python manage.py runserver"
start cmd /k "cd ids-front && npm start"