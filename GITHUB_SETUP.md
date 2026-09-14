# 🚀 GitHub Setup Guide

## Quick Push to GitHub

Open a **new Command Prompt or PowerShell** window and run:

```powershell
# Navigate to project
cd "a:\ai trafic"

# Configure Git (use your real email!)
git config --global user.email "your-email@gmail.com"
git config --global user.name "Abinesh"

# Initialize repository
git init

# Stage all files
git add .

# Create first commit
git commit -m "Initial commit: AutoPlate AI - Vehicle Number Plate Detection System"

# Set main branch
git branch -M main

# Add remote (already done if error shows)
git remote add origin https://github.com/abinesh-0/autoplaite.git

# Push to GitHub
git push -u origin main
```

## 📝 If Remote Already Exists

If you get an error saying the remote already exists:

```powershell
git remote remove origin
git remote add origin https://github.com/abinesh-0/autoplaite.git
git push -u origin main
```

## 🔐 Authentication

If prompted for credentials:
1. Use your GitHub username
2. For password, use a **Personal Access Token** (not your account password)
   - Go to: GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with `repo` permissions
   - Copy and paste when prompted

## ✅ Verify Upload

After pushing, visit:
https://github.com/abinesh-0/autoplaite

Your code should be visible!

## 📦 What's Included

The `.gitignore` file ensures these won't be uploaded:
- ✅ Python cache files (`__pycache__`)
- ✅ Large model files (`*.pt`)
- ✅ Uploaded images/videos
- ✅ Generated results
- ✅ Database files

Only your source code and documentation will be pushed.
