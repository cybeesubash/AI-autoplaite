@echo off
echo ========================================
echo  Fixing Git Issues and Pushing
echo ========================================
echo.

REM Change to correct directory
cd /d "a:\ai trafic"
echo Current directory: %CD%
echo.

REM Configure Git identity (CHANGE THE EMAIL BELOW!)
echo [Step 1] Configuring Git identity...
git config --global user.email "abinesh@example.com"
git config --global user.name "Abinesh"
echo Git identity configured!
echo.

REM Check if .git exists, if not initialize
if not exist ".git" (
    echo [Step 2] Initializing Git repository...
    git init
) else (
    echo [Step 2] Git repository already exists
)
echo.

REM Add all files
echo [Step 3] Adding all files...
git add .
echo.

REM Create commit
echo [Step 4] Creating commit...
git commit -m "Initial commit: AutoPlate AI - Vehicle Number Plate Detection System"
echo.

REM Set main branch
echo [Step 5] Setting main branch...
git branch -M main
echo.

REM Check if remote exists, remove and re-add
echo [Step 6] Configuring remote...
git remote remove origin 2>nul
git remote add origin https://github.com/abinesh-0/autoplaite.git
echo Remote configured!
echo.

REM Push to GitHub
echo [Step 7] Pushing to GitHub...
echo You will be asked for credentials:
echo Username: abinesh-0
echo Password: Use your Personal Access Token (NOT your GitHub password!)
echo Get token from: https://github.com/settings/tokens
echo.
git push -u origin main
echo.

if errorlevel 1 (
    echo ========================================
    echo  ERROR: Push failed!
    echo ========================================
    echo.
    echo Common issues:
    echo 1. Wrong credentials - Use Personal Access Token as password
    echo 2. Network issue - Check internet connection
    echo 3. Repository doesn't exist - Create it on GitHub first
    echo.
) else (
    echo ========================================
    echo  SUCCESS! Code pushed to GitHub!
    echo ========================================
    echo.
    echo View your repository at:
    echo https://github.com/abinesh-0/autoplaite
    echo.
)

pause
