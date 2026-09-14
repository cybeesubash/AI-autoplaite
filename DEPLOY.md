# 🚀 Deployment Guide - AutoPlate AI

## 📋 Pre-Deployment Checklist

- [x] `.gitignore` created
- [x] README.md updated
- [x] Flask backend working on port 5000
- [x] Frontend working on port 3000
- [x] YOLOv8 model trained
- [x] OCR fuzzy recovery implemented
- [x] Web scraping (Google/DDG/Bing) integrated
- [x] Database schema ready

---

## 🔧 Step 1: Push to GitHub

**Open a NEW Windows Terminal or Command Prompt** (not in VS Code):

```powershell
cd "a:\ai trafic"

# Configure Git identity (IMPORTANT: Use your real email!)
git config --global user.email "your-github-email@gmail.com"
git config --global user.name "Abinesh"

# Initialize Git repository
git init

# Stage all files
git add .

# Create first commit
git commit -m "Initial commit: AutoPlate AI - AI-powered vehicle number plate detection system with YOLOv8, OCR, and web search"

# Set main branch
git branch -M main

# Add GitHub remote
git remote add origin https://github.com/abinesh-0/autoplaite.git

# Push to GitHub
git push -u origin main
```

### 🔐 Authentication

When prompted for credentials:
- **Username:** `abinesh-0`
- **Password:** Use a **Personal Access Token** (not your GitHub password)

**Create a token here:** https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Name: "AutoPlate AI"
- Select scope: `repo` (full control)
- Click "Generate token"
- Copy and save the token
- Use it as your password when pushing

---

## 🌐 Step 2: Deploy to Web (Options)

### Option A: GitHub Pages (Static Frontend Only)

GitHub Pages can host your frontend:

1. Go to: https://github.com/abinesh-0/autoplaite/settings/pages
2. Under "Source", select `main` branch
3. Select `/frontend` folder or root
4. Save

**Note:** Backend won't run on GitHub Pages (it only hosts static files)

---

### Option B: Deploy Full Stack (Recommended)

#### **Render.com** (Free tier available)

**Backend Deployment:**

1. Go to https://render.com/
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect your `autoplaite` repository
5. Configure:
   - **Name:** `autoplate-ai-backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python backend/app.py`
   - **Add Environment Variables:**
     - `PORT=5000`
6. Click "Create Web Service"

**Frontend Deployment:**

1. Host frontend separately or serve it through Flask
2. Update API URLs in `frontend/script.js` to point to your Render backend URL

---

#### **Vercel** (Frontend) + **Render** (Backend)

**Frontend on Vercel:**
1. Go to https://vercel.com/
2. Import your GitHub repository
3. Configure root directory: `frontend`
4. Deploy

**Backend on Render:** (Same as above)

---

#### **PythonAnywhere** (All-in-One)

1. Go to https://www.pythonanywhere.com/
2. Create free account
3. Upload your project files
4. Install dependencies in virtual environment
5. Configure WSGI file to point to Flask app
6. Set up static files mapping

---

### Option C: Heroku (Requires Credit Card for Verification)

Create `Procfile` in project root:
```
web: python backend/app.py
```

Deploy:
```powershell
heroku login
heroku create autoplate-ai
git push heroku main
```

---

## 📦 Important Files for Deployment

### 1. requirements.txt
Already exists with all dependencies.

### 2. runtime.txt (for some platforms)
Specify Python version:
```
python-3.11.0
```

### 3. Procfile (for Heroku)
```
web: python backend/app.py
```

### 4. Environment Variables
When deploying, set:
- `PORT` (if required by platform)
- Database connection strings
- Any API keys

---

## ⚠️ Before Deploying

### Update CORS in `backend/app.py`

Change from:
```python
CORS(app)
```

To:
```python
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://your-frontend-domain.vercel.app",
            "http://localhost:3000",
            "http://127.0.0.1:5000"
        ]
    }
})
```

### Update API URLs in Frontend

In `frontend/script.js` and `landing/complete-script.js`, update:
```javascript
const API_URL = 'https://your-backend-url.onrender.com';
```

---

## 🧪 Test Deployment

After deployment:

1. ✅ Test image upload
2. ✅ Test video upload
3. ✅ Test OCR recognition
4. ✅ Test web search functionality
5. ✅ Test database history
6. ✅ Check CORS policies
7. ✅ Verify all API endpoints

---

## 📊 Recommended Deployment Stack

**For Free Hosting:**
- **Frontend:** Vercel or Netlify
- **Backend:** Render.com or Railway.app
- **Database:** SQLite (included) or Railway PostgreSQL

**For Production:**
- **Frontend:** Vercel, Netlify, or Cloudflare Pages
- **Backend:** AWS EC2, DigitalOcean, or Railway
- **Database:** PostgreSQL or MySQL
- **Storage:** AWS S3 for uploaded images
- **CDN:** Cloudflare

---

## 🔗 Useful Links

- GitHub Repo: https://github.com/abinesh-0/autoplaite
- Render: https://render.com/
- Vercel: https://vercel.com/
- Railway: https://railway.app/
- PythonAnywhere: https://www.pythonanywhere.com/

---

## 💡 Quick Deploy Commands Summary

```powershell
# 1. Push to GitHub
cd "a:\ai trafic"
git init
git add .
git commit -m "Initial commit: AutoPlate AI"
git branch -M main
git remote add origin https://github.com/abinesh-0/autoplaite.git
git push -u origin main

# 2. Then deploy via web interface (Render/Vercel)
```

---

**Deployment la help venum na sollungaa!** (If you need help with deployment, let me know!)
