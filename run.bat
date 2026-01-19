@echo off
title Game Agent Console
echo Starting Game Agent...

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Installing dependencies...
    venv\Scripts\pip install -r requirements.txt
)

echo Launching...
venv\Scripts\python src\main.py
pause
