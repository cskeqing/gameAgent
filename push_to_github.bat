@echo off
chcp 65001 >nul
title Push to GitHub Helper
echo ========================================================
echo       Game Agent - GitHub Push Helper
echo ========================================================
echo.
echo Please create a new repository on GitHub website first:
echo https://github.com/new
echo.
set /p REPO_URL="Paste your GitHub Repository URL here (e.g., https://github.com/user/repo.git): "

if "%REPO_URL%"=="" (
    echo Error: URL cannot be empty.
    pause
    exit /b
)

echo.
echo Adding remote origin...
git remote add origin %REPO_URL%
if %errorlevel% neq 0 (
    echo Remote 'origin' might already exist. Updating it...
    git remote set-url origin %REPO_URL%
)

echo.
echo Pushing to GitHub (Main branch)...
git branch -M main
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Push failed! 
    echo Possible reasons:
    echo 1. You are not logged in. (Try running 'git credential-manager diagnose')
    echo 2. The repository URL is wrong.
    echo 3. You don't have permission to write to this repository.
) else (
    echo.
    echo [SUCCESS] Successfully pushed to GitHub!
)

pause
