@echo off
echo ========================================
echo  AutoPlate AI - GitHub Push Script
echo ========================================
echo.

cd /d "a:\ai trafic"

echo [1/7] Configuring Git user...
git config --global user.email "your-email@gmail.com"
git config --global user.name "Abinesh"

echo [2/7] Initializing Git repository...
git init

echo [3/7] Adding all files...
git add .

echo [4/7] Creating initial commit...
git commit -m "Initial commit: AutoPlate AI - Vehicle Number Plate Detection System with YOLOv8, OCR, and Web Search"

echo [5/7] Setting main branch...
git branch -M main

echo [6/7] Adding remote origin...
git remote add origin https://github.com/abinesh-0/autoplaite.git 2>nul
if errorlevel 1 (
    echo Remote already exists, updating...
    git remote set-url origin https://github.com/abinesh-0/autoplaite.git
)

echo [7/7] Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo  Done! Check: https://github.com/abinesh-0/autoplaite
echo ========================================
echo.
pause
