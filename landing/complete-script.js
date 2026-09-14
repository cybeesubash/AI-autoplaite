// ============================================================
// AutoPlate AI - Complete Single Page App
// ============================================================

const API_BASE = 'http://127.0.0.1:5000';

// ── Navbar & Navigation ─────────────────────────────────────
const navbar = document.getElementById('navbar');
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('navMenu');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

hamburger.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    hamburger.classList.toggle('active');
});

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        hamburger.classList.remove('active');
    });
});

// Active nav link on scroll
const sections = document.querySelectorAll('section[id]');
window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        if (window.scrollY >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// ── Particle Background ─────────────────────────────────────
const canvas = document.getElementById('particleCanvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particlesArray = [];
const numberOfParticles = 80;

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 2 + 0.5;
        this.speedX = (Math.random() - 0.5) * 0.5;
        this.speedY = (Math.random() - 0.5) * 0.5;
        this.opacity = Math.random() * 0.5 + 0.2;
    }
    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        if (this.x > canvas.width || this.x < 0) this.speedX = -this.speedX;
        if (this.y > canvas.height || this.y < 0) this.speedY = -this.speedY;
    }
    draw() {
        ctx.fillStyle = `rgba(0, 242, 254, ${this.opacity})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

function initParticles() {
    particlesArray = [];
    for (let i = 0; i < numberOfParticles; i++) {
        particlesArray.push(new Particle());
    }
}

function connectParticles() {
    for (let i = 0; i < particlesArray.length; i++) {
        for (let j = i + 1; j < particlesArray.length; j++) {
            const dx = particlesArray[i].x - particlesArray[j].x;
            const dy = particlesArray[i].y - particlesArray[j].y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < 120) {
                ctx.strokeStyle = `rgba(0, 242, 254, ${0.15 * (1 - distance / 120)})`;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(particlesArray[i].x, particlesArray[i].y);
                ctx.lineTo(particlesArray[j].x, particlesArray[j].y);
                ctx.stroke();
            }
        }
    }
}

function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update();
        particlesArray[i].draw();
    }
    connectParticles();
    requestAnimationFrame(animateParticles);
}

initParticles();
animateParticles();

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    initParticles();
});

// ── Upload Tabs ─────────────────────────────────────────────
document.querySelectorAll('.upload-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.upload-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        tab.classList.add('active');
        const tabName = tab.dataset.tab;
        document.getElementById(tabName + 'Tab').classList.add('active');
    });
});

// ── Detail Tabs ─────────────────────────────────────────────
document.querySelectorAll('.detail-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.detail-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.detail-content').forEach(c => c.classList.remove('active'));
        
        tab.classList.add('active');
        const detailName = tab.dataset.detail;
        document.getElementById(detailName + 'Content').classList.add('active');
    });
});

// ── Image Upload ────────────────────────────────────────────
const imageInput = document.getElementById('imageInput');
const imageUploadZone = document.getElementById('imageUploadZone');

imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleImageUpload(e.target.files[0]);
    }
});

imageUploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    imageUploadZone.classList.add('dragover');
});

imageUploadZone.addEventListener('dragleave', () => {
    imageUploadZone.classList.remove('dragover');
});

imageUploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    imageUploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        handleImageUpload(e.dataTransfer.files[0]);
    }
});

async function handleImageUpload(file) {
    showProcessing('Detecting vehicle number plate...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/detect`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        hideProcessing();
        displayResults(data);
    } catch (error) {
        hideProcessing();
        alert('Detection failed: ' + error.message);
    }
}

// ── Video Upload ────────────────────────────────────────────
const videoInput = document.getElementById('videoInput');
const videoUploadZone = document.getElementById('videoUploadZone');

videoInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleVideoUpload(e.target.files[0]);
    }
});

videoUploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    videoUploadZone.classList.add('dragover');
});

videoUploadZone.addEventListener('dragleave', () => {
    videoUploadZone.classList.remove('dragover');
});

videoUploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    videoUploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        handleVideoUpload(e.dataTransfer.files[0]);
    }
});

async function handleVideoUpload(file) {
    showProcessing('Processing video and detecting plate...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/detect-video`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        hideProcessing();
        displayResults(data);
    } catch (error) {
        hideProcessing();
        alert('Video processing failed: ' + error.message);
    }
}

// ── Plate Search ────────────────────────────────────────────
const plateSearchBtn = document.getElementById('plateSearchBtn');
const plateSearchInput = document.getElementById('plateSearchInput');

plateSearchBtn.addEventListener('click', () => {
    const plate = plateSearchInput.value.trim();
    if (plate.length >= 4) {
        handlePlateSearch(plate);
    } else {
        alert('Please enter a valid plate number');
    }
});

plateSearchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        plateSearchBtn.click();
    }
});

document.querySelectorAll('.example-chip').forEach(chip => {
    chip.addEventListener('click', () => {
        plateSearchInput.value = chip.dataset.plate;
        handlePlateSearch(chip.dataset.plate);
    });
});

async function handlePlateSearch(plate) {
    showProcessing('Searching public information...');
    
    try {
        const response = await fetch(`${API_BASE}/search-plate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ plate: plate })
        });
        
        const data = await response.json();
        hideProcessing();
        displaySearchResults(data);
    } catch (error) {
        hideProcessing();
        alert('Search failed: ' + error.message);
    }
}

// ── Display Functions ───────────────────────────────────────
function showProcessing(message) {
    document.getElementById('statusText').textContent = message;
    document.getElementById('processingStatus').classList.remove('hidden');
    document.getElementById('resultsSection').classList.add('hidden');
}

function hideProcessing() {
    document.getElementById('processingStatus').classList.add('hidden');
}

function displayResults(data) {
    // Show results section
    document.getElementById('resultsSection').classList.remove('hidden');
    
    // Display images
    document.getElementById('originalImage').src = API_BASE + data.original_image_url;
    document.getElementById('detectedPlate').src = API_BASE + data.cropped_plate_url;
    
    // Display plate number
    document.getElementById('plateNumber').textContent = data.vehicle_number;
    document.getElementById('confidence').textContent = Math.round(data.detection_confidence * 100) + '%';
    
    // Display registration info
    const regInfo = document.getElementById('registrationInfo');
    regInfo.innerHTML = `
        <div class="info-item">
            <div class="info-label">Vehicle Number</div>
            <div class="info-value">${data.vehicle_number}</div>
        </div>
        <div class="info-item">
            <div class="info-label">State</div>
            <div class="info-value">${data.state || '—'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">RTO Code</div>
            <div class="info-value">${data.rto_code || '—'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Registration Area</div>
            <div class="info-value">${data.registration_area || '—'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Vehicle Type</div>
            <div class="info-value">${data.vehicle_type || '—'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">OCR Confidence</div>
            <div class="info-value">${Math.round((data.ocr_confidence || 0) * 100)}%</div>
        </div>
    `;
    
    // Display public search results
    const searchResults = document.getElementById('publicSearchResults');
    if (data.public_web_pages && data.public_web_pages.length > 0) {
        searchResults.innerHTML = data.public_web_pages.slice(0, 5).map(page => `
            <div class="search-result-item">
                <div class="search-result-title">${escapeHtml(page.title)}</div>
                <div class="search-result-snippet">${escapeHtml(page.snippet)}</div>
                ${page.url ? `<a href="${escapeHtml(page.url)}" target="_blank" style="color: var(--primary-cyan); font-size: 0.8rem; text-decoration: none;">View Source →</a>` : ''}
            </div>
        `).join('');
    } else {
        searchResults.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No public information found</p>';
    }
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displaySearchResults(data) {
    // Show results section
    document.getElementById('resultsSection').classList.remove('hidden');
    
    // Hide image cards for search-only
    document.querySelector('.results-images').style.display = 'none';
    
    // Display plate number
    document.getElementById('plateNumber').textContent = data.plate;
    document.getElementById('confidence').textContent = 'Search Result';
    
    // Display registration info
    const parsed = data.parsed || {};
    const regCard = data.registration_info_card || {};
    const regInfo = document.getElementById('registrationInfo');
    regInfo.innerHTML = `
        <div class="info-item">
            <div class="info-label">Vehicle Number</div>
            <div class="info-value">${data.plate}</div>
        </div>
        <div class="info-item">
            <div class="info-label">State</div>
            <div class="info-value">${regCard.state || parsed.state || '—'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">RTO Code</div>
            <div class="info-value">${regCard.registration_code || parsed.rto_code || '—'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Registration Area</div>
            <div class="info-value">${regCard.registration_area || parsed.registration_area || '—'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Country</div>
            <div class="info-value">${regCard.country || parsed.country || '—'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Vehicle Category</div>
            <div class="info-value">${regCard.vehicle_category || '—'}</div>
        </div>
    `;
    
    // Display public search results
    const searchResults = document.getElementById('publicSearchResults');
    if (data.public_web_pages && data.public_web_pages.length > 0) {
        searchResults.innerHTML = data.public_web_pages.map(page => `
            <div class="search-result-item">
                <div class="search-result-title">${escapeHtml(page.title)}</div>
                <div class="search-result-snippet">${escapeHtml(page.snippet)}</div>
                ${page.url ? `<a href="${escapeHtml(page.url)}" target="_blank" style="color: var(--primary-cyan); font-size: 0.8rem; text-decoration: none;">View Source →</a>` : ''}
            </div>
        `).join('');
    } else {
        searchResults.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No public information found</p>';
    }
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Clear Results ───────────────────────────────────────────
document.getElementById('clearResultsBtn').addEventListener('click', () => {
    document.getElementById('resultsSection').classList.add('hidden');
    document.querySelector('.results-images').style.display = 'flex';
    imageInput.value = '';
    videoInput.value = '';
    plateSearchInput.value = '';
});

// ── Utility ─────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

// Console message
console.log('%c🚗 AutoPlate AI', 'color: #00f2fe; font-size: 24px; font-weight: bold;');
console.log('%cComplete System - Detection Ready', 'color: #94a3b8; font-size: 14px;');
