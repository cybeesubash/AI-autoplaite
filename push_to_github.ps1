# AutoPlate AI - GitHub Push Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " AutoPlate AI - GitHub Push Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "a:\ai trafic"

Write-Host "[1/7] Configuring Git user..." -ForegroundColor Yellow
git config --global user.email "your-email@gmail.com"
git config --global user.name "Abinesh"

Write-Host "[2/7] Initializing Git repository..." -ForegroundColor Yellow
git init

Write-Host "[3/7] Adding all files..." -ForegroundColor Yellow
git add .

Write-Host "[4/7] Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: AutoPlate AI - Vehicle Number Plate Detection System with YOLOv8, OCR, and Web Search"

Write-Host "[5/7] Setting main branch..." -ForegroundColor Yellow
git branch -M main

Write-Host "[6/7] Adding remote origin..." -ForegroundColor Yellow
$remoteExists = git remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) {
    git remote add origin https://github.com/abinesh-0/autoplaite.git
    Write-Host "Remote added successfully" -ForegroundColor Green
} else {
    git remote set-url origin https://github.com/abinesh-0/autoplaite.git
    Write-Host "Remote URL updated" -ForegroundColor Green
}

Write-Host "[7/7] Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Done! Check: https://github.com/abinesh-0/autoplaite" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
