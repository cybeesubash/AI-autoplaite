# ⚡ Quick Start Guide - AutoPlate AI

## 🚀 Push to GitHub (Choose One Method)

### Method 1: Double-Click Batch File (Easiest)
1. Open File Explorer
2. Navigate to `a:\ai trafic`
3. **Edit `push_to_github.bat`** - Change `your-email@gmail.com` to your real email
4. Double-click `push_to_github.bat`
5. Enter your GitHub credentials when prompted
   - Username: `abinesh-0`
   - Password: Use **Personal Access Token** (get from https://github.com/settings/tokens)

### Method 2: PowerShell Script
1. Right-click on `push_to_github.ps1`
2. **Edit** - Change `your-email@gmail.com` to your real email
3. Save and close
4. Right-click on `push_to_github.ps1` → "Run with PowerShell"

### Method 3: Manual Commands
Open Command Prompt or PowerShell:

```powershell
cd "a:\ai trafic"

# IMPORTANT: Change the email below!
git config --global user.email "your-email@gmail.com"
git config --global user.name "Abinesh"

git init
git add .
git commit -m "Initial commit: AutoPlate AI"
git branch -M main
git remote add origin https://github.com/abinesh-0/autoplaite.git
git push -u origin main
```

---

## 🔐 GitHub Authentication

**You MUST use a Personal Access Token, not your password!**

### Create Token:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `AutoPlate AI`
4. Check: `repo` (full control of private repositories)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when Git asks

---

## ✅ After Pushing

Visit: **https://github.com/abinesh-0/autoplaite**

Your repository should now contain:
- ✅ Backend code (Flask API)
- ✅ Frontend code (HTML/CSS/JS)
- ✅ Landing page
- ✅ README.md
- ✅ requirements.txt
- ✅ Training scripts
- ✅ Documentation

---

## 🌐 Deploy to Web

After pushing to GitHub, deploy using:

### **Render.com** (Recommended - Free)
1. Go to https://render.com/
2. Sign in with GitHub
3. New → Web Service
4. Connect `autoplaite` repo
5. Set:
   - Build: `pip install -r requirements.txt`
   - Start: `python backend/app.py`
6. Deploy!

### **Vercel** (Frontend only)
1. Go to https://vercel.com/
2. Import GitHub repo
3. Set root: `frontend/`
4. Deploy!

---

## 📱 Access Your App

**Local:**
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:5000
- Complete Page: http://localhost:3000/complete.html

**After Deployment:**
- Your Render URL: `https://autoplate-ai.onrender.com`
- Your Vercel URL: `https://autoplaite.vercel.app`

---

## 🆘 Troubleshooting

### "Git is not recognized"
→ Install Git: https://git-scm.com/download/win
→ Restart terminal after installation

### "Remote already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/abinesh-0/autoplaite.git
```

### "Authentication failed"
→ Use Personal Access Token, not password
→ Get token: https://github.com/settings/tokens

### "Nothing to commit"
→ You may have already committed
→ Try: `git push -u origin main`

---

## 📞 Need Help?

Check these files:
- `DEPLOY.md` - Full deployment guide
- `GITHUB_SETUP.md` - Detailed Git setup
- `README.md` - Project documentation

**Ella ok ya?** (Everything okay?)
