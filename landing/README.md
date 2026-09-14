# AutoPlate AI Landing Page

## 🚗 Premium Dark Cyber-Tech Landing Page

A stunning, modern landing page for the AutoPlate AI project with glassmorphism design, animated particles, and a professional team section.

---

## 📂 File Structure

```
landing/
├── index.html          # Main landing page
├── styles.css          # All styles with glassmorphism theme
├── script.js           # Interactive animations & effects
├── assets/             # Images and media
│   ├── placeholder-1.svg   # Temporary placeholder for Abinesh
│   ├── placeholder-2.svg   # Temporary placeholder for Vishwa
│   ├── placeholder-3.svg   # Temporary placeholder for Praveen
│   ├── abinesh.jpg         # Add your actual photo here
│   ├── vishwa.jpg          # Add your actual photo here
│   └── praveen.jpg         # Add your actual photo here
└── README.md           # This file
```

---

## 🖼️ How to Add Team Member Photos

### Step 1: Prepare Your Photos

1. Take or choose a **professional-looking photo** (front-facing, good lighting)
2. Crop it to a **square** (1:1 aspect ratio) — e.g., 800x800px or 1000x1000px
3. Save as **JPG** with good quality
4. Recommended file names:
   - `abinesh.jpg`
   - `vishwa.jpg`
   - `praveen.jpg`

### Step 2: Add Photos to the Assets Folder

Place your photos in the `landing/assets/` folder:

```
landing/assets/
├── abinesh.jpg    ← Your photo here
├── vishwa.jpg     ← Your photo here
├── praveen.jpg    ← Your photo here
```

### Step 3: Done!

The page will automatically use your real photos instead of the placeholders. The `onerror` fallback in the HTML ensures placeholders show if photos are missing.

---

## 🎨 Features

### Landing Page
- ✅ Dark cyber-tech theme with glassmorphism
- ✅ Sticky navbar with smooth scroll
- ✅ Animated particle background
- ✅ Hero section with plate scanner animation
- ✅ Feature highlights (4 glass cards)
- ✅ Bottom CTA section
- ✅ Minimal footer

### Team Section
- ✅ 3 professional team member cards
- ✅ Circular photos with glow effect
- ✅ Hover animations (lift + zoom)
- ✅ Glassmorphism card design
- ✅ Fully responsive (desktop/tablet/mobile)

### Animations
- ✅ Scanning laser over number plate
- ✅ Particle network background
- ✅ Smooth scroll animations
- ✅ Hover effects on all interactive elements
- ✅ 3D tilt effect on plate scanner

---

## 🌐 How to View

### Option 1: Open Directly
Simply open `index.html` in your browser:
```
Right-click index.html → Open with → Chrome/Firefox/Edge
```

### Option 2: Local Server (Recommended)
If you're already running the Flask backend:
```
http://127.0.0.1:5000/landing/
```

Or use Python's built-in server:
```bash
cd landing
python -m http.server 8080
```
Then visit: `http://localhost:8080`

---

## 📱 Responsive Design

The landing page is fully responsive:
- **Desktop (1400px+)**: Full 3-column team grid, side-by-side hero
- **Laptop (1024-1399px)**: 2-column team grid, side-by-side hero
- **Tablet (768-1023px)**: 2-column team grid, stacked hero
- **Mobile (< 768px)**: 1-column team grid, stacked hero, hamburger menu

---

## 🎯 Navigation

The landing page links to the main detection app:
- **"Try Detection"** button → `../index.html` (main app)
- **"Start Detection"** CTA → `../index.html` (main app)
- **Detection menu link** → `../index.html` (main app)

---

## 🎨 Color Scheme

| Color | Hex | Usage |
|-------|-----|-------|
| Primary Cyan | `#00f2fe` | Buttons, highlights, gradients |
| Primary Blue | `#0891f7` | Gradients, accents |
| Accent Emerald | `#10d9c4` | Secondary accents |
| Dark BG | `#0a0e1a` | Main background |
| Darker BG | `#050810` | Deep background |
| Text Main | `#e2e8f0` | Primary text |
| Text Muted | `#94a3b8` | Secondary text |

---

## 🛠️ Tech Stack

- **HTML5** — Semantic structure
- **CSS3** — Glassmorphism, animations, gradients
- **Vanilla JavaScript** — Particles, scroll effects, nav
- **Google Fonts** — Inter (sans-serif) + JetBrains Mono (monospace)

---

## 📝 Customization

### Change Team Member Info
Edit `index.html` lines 140-220:
```html
<h3 class="team-name">Your Name</h3>
<p class="team-degree">Your Degree</p>
<p class="team-year">Your Year</p>
<span class="role-badge">Your Role</span>
```

### Change Colors
Edit `styles.css` lines 8-20:
```css
:root {
    --primary-cyan: #00f2fe;
    --primary-blue: #0891f7;
    /* ... */
}
```

### Change Hero Plate Number
Edit `index.html` line 68:
```html
<span class="plate-text">TN 38 AB 1234</span>
```

---

## 🚀 Deployment

### GitHub Pages
1. Push the `landing/` folder to your repo
2. Go to Settings → Pages
3. Select branch and `/landing` folder
4. Your page will be live at `https://yourusername.github.io/repo-name/landing/`

### Netlify / Vercel
1. Drag and drop the `landing/` folder
2. Site will be live instantly with a custom URL

---

## 👥 Team

- **Abinesh** — AI / Full Stack Developer
- **Vishwa** — Team Member
- **Praveen** — Team Member

---

## 📄 License

Built for the AutoPlate AI project — B.Tech AI & Data Science

© 2026 AutoPlate AI
# autoplaite
