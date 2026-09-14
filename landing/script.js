// ============================================================
// script.js  –  Frontend App Logic & REST API Integration
// Title: AI-Based Indian & Global Vehicle Number Plate Detection,
//        Recognition & Public Information Search System
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    // ── DYNAMIC API BASE URL & MULTI-ENDPOINT FALLBACK ───────
    function getCandidateApiUrls() {
        const list = [];
        if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
            if (window.location.port === '5000') {
                list.push(window.location.origin);
            } else if (window.location.hostname) {
                list.push(`${window.location.protocol}//${window.location.hostname}:5000`);
            }
        }
        list.push('http://127.0.0.1:5000');
        list.push('http://localhost:5000');
        return [...new Set(list)];
    }

    let ACTIVE_API_BASE_URL = getCandidateApiUrls()[0];

    async function smartFetch(endpoint, options = {}) {
        const candidateUrls = getCandidateApiUrls();
        let lastError = null;

        for (const baseUrl of candidateUrls) {
            try {
                const url = `${baseUrl}${endpoint}`;
                const res = await fetch(url, options);
                if (res) {
                    ACTIVE_API_BASE_URL = baseUrl;
                    return res;
                }
            } catch (err) {
                lastError = err;
            }
        }
        throw lastError || new TypeError('Failed to connect to backend server');
    }

    // ── DOM ELEMENTS ─────────────────────────────────────────
    const serverStatusBadge = document.getElementById('serverStatusBadge');
    const serverStatusText = document.getElementById('serverStatusText');

    const tabImage = document.getElementById('tabImage');
    const tabVideo = document.getElementById('tabVideo');

    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const dropIdle = document.getElementById('dropIdle');
    const dropPreview = document.getElementById('dropPreview');

    const imagePreview = document.getElementById('imagePreview');
    const videoPreview = document.getElementById('videoPreview');
    const fileNameSpan = document.getElementById('fileName');
    const fileSizeSpan = document.getElementById('fileSize');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const formatHint = document.getElementById('formatHint');

    const detectBtn = document.getElementById('detectBtn');
    const resetBtn = document.getElementById('resetBtn');

    const progressContainer = document.getElementById('progressContainer');
    const progressMsg = document.getElementById('progressMsg');
    const progressPercent = document.getElementById('progressPercent');
    const progressBarFill = document.getElementById('progressBarFill');

    const errorAlert = document.getElementById('errorAlert');
    const errorMsg = document.getElementById('errorMsg');

    const resultsEmptyState = document.getElementById('resultsEmptyState');
    const resultsPopulatedState = document.getElementById('resultsPopulatedState');
    const resultStatusPill = document.getElementById('resultStatusPill');

    const plateNumberDisplay = document.getElementById('plateNumberDisplay');
    const plateConfidenceBadge = document.getElementById('plateConfidenceBadge');

    // 4-Image Grid Elements
    const originalImage = document.getElementById('originalImage');
    const annotatedImage = document.getElementById('annotatedImage');
    const croppedPlateImage = document.getElementById('croppedPlateImage');
    const preprocessedPlateImage = document.getElementById('preprocessedPlateImage');

    // Result Card Details
    const resVehicleNumber = document.getElementById('resVehicleNumber');
    const resSeries = document.getElementById('resSeries');
    const resRegNum = document.getElementById('resRegNum');
    const resDetectConf = document.getElementById('resDetectConf');
    const resOcrConf = document.getElementById('resOcrConf');

    // Modal Elements
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    const modalCloseBtn = document.getElementById('modalCloseBtn');

    const infoBtn = document.getElementById('infoBtn');
    const infoModal = document.getElementById('infoModal');
    const infoModalCloseBtn = document.getElementById('infoModalCloseBtn');

    // ── APP STATE ────────────────────────────────────────────
    let currentMode = 'image'; // 'image' or 'video'
    let selectedFile = null;
    let currentVehicleNumber = '';
    let currentVehicleType = 'Car';

    // ── INITIAL HEALTH CHECK ─────────────────────────────────
    checkBackendHealth();

    function checkBackendHealth() {
        smartFetch('/api/health')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'ok') {
                    serverStatusText.textContent = 'Flask REST API Active';
                    serverStatusBadge.classList.add('active');
                }
            })
            .catch(() => {
                serverStatusText.textContent = 'Backend Connecting...';
            });
    }

    // ── TAB SWITCHING IN RESULTS ──────────────────────────────
    document.querySelectorAll('.rtab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.rtab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.rtab-content').forEach(c => c.classList.add('hidden'));

            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            const targetEl = document.getElementById(targetId);
            if (targetEl) targetEl.classList.remove('hidden');
        });
    });

    // ── MODE SWITCHING ───────────────────────────────────────
    tabImage.addEventListener('click', () => setMode('image'));
    tabVideo.addEventListener('click', () => setMode('video'));

    function setMode(mode) {
        currentMode = mode;
        tabImage.classList.toggle('active', mode === 'image');
        tabVideo.classList.toggle('active', mode === 'video');

        if (mode === 'image') {
            fileInput.accept = 'image/png, image/jpeg, image/jpg, image/webp';
            formatHint.textContent = 'Supports: JPG, PNG, WEBP (Max 50MB)';
        } else {
            fileInput.accept = 'video/mp4, video/avi, video/mov, video/webm';
            formatHint.textContent = 'Supports: MP4, AVI, MOV (Max 100MB)';
        }
        resetFileSelection();
    }

    // ── DRAG & DROP FILE SELECTION ───────────────────────────
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFileSelect(e.target.files[0]);
        }
    });

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetFileSelection();
    });

    function handleFileSelect(file) {
        selectedFile = file;
        fileNameSpan.textContent = file.name;
        fileSizeSpan.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';

        const fileURL = URL.createObjectURL(file);

        if (file.type.startsWith('image/')) {
            imagePreview.src = fileURL;
            imagePreview.classList.remove('hidden');
            videoPreview.classList.add('hidden');
        } else if (file.type.startsWith('video/')) {
            videoPreview.src = fileURL;
            videoPreview.classList.remove('hidden');
            imagePreview.classList.add('hidden');
        }

        dropIdle.classList.add('hidden');
        dropPreview.classList.remove('hidden');
        detectBtn.disabled = false;
        hideError();
    }

    function resetFileSelection() {
        selectedFile = null;
        fileInput.value = '';
        imagePreview.src = '';
        videoPreview.src = '';
        imagePreview.classList.add('hidden');
        videoPreview.classList.add('hidden');
        dropPreview.classList.add('hidden');
        dropIdle.classList.remove('hidden');
        detectBtn.disabled = true;
        hideError();
    }

    resetBtn.addEventListener('click', () => {
        resetFileSelection();
        resetResultsDisplay();
    });

    function resetResultsDisplay() {
        resultsPopulatedState.classList.add('hidden');
        resultsEmptyState.classList.remove('hidden');
        resultStatusPill.textContent = 'Awaiting Input';
        resultStatusPill.className = 'status-pill idle';
        progressContainer.classList.add('hidden');
        currentVehicleNumber = '';
    }

    // ── DETECTION & AUTOMATED MULTI-QUERY SEARCH ───────────────
    detectBtn.addEventListener('click', () => {
        if (!selectedFile) return;

        showProgress();
        hideError();
        detectBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', selectedFile);

        const endpoint = currentMode === 'image' ? '/detect' : '/detect-video';

        // Animate Timeline Steps
        simulateProgressTimeline();

        smartFetch(endpoint, {
            method: 'POST',
            body: formData
        })
        .then(res => {
            if (!res.ok) {
                return res.json().then(data => { throw new Error(data.error || 'Server error'); });
            }
            return res.json();
        })
        .then(data => {
            updateProgressBar(100, 'Public Search Complete ✓');
            setTimeout(() => {
                progressContainer.classList.add('hidden');
                displayDetectionResults(data);
                detectBtn.disabled = false;
            }, 400);
        })
        .catch(err => {
            progressContainer.classList.add('hidden');
            showError(err.message || 'Detection failed. Please ensure the Flask server is running at http://127.0.0.1:5000.');
            detectBtn.disabled = false;
        });
    });

    function simulateProgressTimeline() {
        setTimelineStep('tstep1', 'active');
        updateProgressBar(15, 'Number Plate Detected ✓');

        setTimeout(() => {
            setTimelineStep('tstep1', 'done');
            setTimelineStep('tstep2', 'active');
            updateProgressBar(35, 'OCR Completed ✓');
        }, 500);

        setTimeout(() => {
            setTimelineStep('tstep2', 'done');
            setTimelineStep('tstep3', 'active');
            updateProgressBar(55, 'Registration Format Analyzed ✓');
        }, 1000);

        setTimeout(() => {
            setTimelineStep('tstep3', 'done');
            setTimelineStep('tstep4', 'active');
            updateProgressBar(75, 'Searching Public Web...');
        }, 1500);

        setTimeout(() => {
            setTimelineStep('tstep4', 'done');
            setTimelineStep('tstep5', 'active');
            updateProgressBar(90, 'Searching Public Images...');
        }, 2000);

        setTimeout(() => {
            setTimelineStep('tstep5', 'done');
            setTimelineStep('tstep6', 'active');
            updateProgressBar(98, 'Analyzing Public Results...');
        }, 2500);
    }

    function setTimelineStep(stepId, state) {
        const target = document.getElementById(stepId);
        if (target) {
            target.className = `t-step ${state}`;
        }
    }

    function updateProgressBar(percent, msg) {
        progressBarFill.style.width = percent + '%';
        progressPercent.textContent = percent + '%';
        progressMsg.textContent = msg;
    }

    function showProgress() {
        progressContainer.classList.remove('hidden');
        updateProgressBar(0, 'Initializing pipeline...');
    }

    function resolveMediaUrl(url) {
        if (!url) return '';
        if (url.startsWith('http://') || url.startsWith('https://')) return url;
        return `${ACTIVE_API_BASE_URL}${url}`;
    }

    // ── DISPLAY DETECTION & AUTOMATIC SEARCH RESULTS ────────────
    function displayDetectionResults(data) {
        currentVehicleNumber = data.vehicle_number;
        currentVehicleType = data.vehicle_type || 'Car';

        // ── OCR FAILURE BANNER ───────────────────────────────────
        // Remove any existing banner first
        const existingBanner = document.getElementById('ocrFailureBanner');
        if (existingBanner) existingBanner.remove();

        const plateNotRecognized = !data.plate_recognized ||
            data.vehicle_number === 'UNKNOWN' ||
            data.ocr_status === 'ocr_failed' ||
            data.ocr_status === 'unrecognized_format';

        if (plateNotRecognized) {
            // Build a clear, honest failure banner
            const banner = document.createElement('div');
            banner.id = 'ocrFailureBanner';
            banner.style.cssText = `
                background: rgba(239,68,68,0.12);
                border: 1px solid rgba(239,68,68,0.4);
                border-radius: 12px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
                display: flex;
                flex-direction: column;
                gap: 0.4rem;
            `;

            const statusLabel = data.ocr_status === 'ocr_failed'
                ? 'OCR could not read any text from the plate region'
                : `OCR read "${escapeHtml(data.vehicle_number)}" — unrecognized plate format`;

            banner.innerHTML = `
                <div style="display:flex;align-items:center;gap:0.6rem;font-weight:700;color:#f87171;font-size:0.95rem;">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    Plate Not Recognized
                </div>
                <div style="font-size:0.84rem;color:#fca5a5;">${statusLabel}</div>
                ${data.ocr_failure_reason ? `<div style="font-size:0.78rem;color:#94a3b8;margin-top:0.2rem;">${escapeHtml(data.ocr_failure_reason)}</div>` : ''}
                <div style="font-size:0.78rem;color:#94a3b8;margin-top:0.3rem;">
                    <b>Tips:</b> Use a clear, front-on photo with good lighting. Ensure the plate is fully visible and not blurred.
                </div>
            `;

            // Insert banner at the top of the populated results
            const populatedState = document.getElementById('resultsPopulatedState');
            populatedState.insertBefore(banner, populatedState.firstChild);

            // Override plate badge to show failure state
            plateNumberDisplay.textContent = data.ocr_status === 'ocr_failed' ? 'NOT READABLE' : (data.vehicle_number || 'UNKNOWN');
            plateNumberDisplay.style.color = '#f87171';
            const validBadge = document.getElementById('plateValidationBadge');
            if (validBadge) {
                validBadge.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Plate Not Recognized';
                validBadge.className = 'badge-tag';
                validBadge.style.cssText = 'background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.3);';
            }
        } else {
            // Successful read — reset plate badge to normal
            plateNumberDisplay.style.color = '';
            const validBadge = document.getElementById('plateValidationBadge');
            if (validBadge) {
                validBadge.innerHTML = '<i class="fa-solid fa-circle-check"></i> Valid Registration Format';
                validBadge.className = 'badge-tag valid';
                validBadge.style.cssText = '';
            }
        }

        // Badge & Header
        plateNumberDisplay.textContent = data.vehicle_number;
        plateConfidenceBadge.innerHTML = `<i class="fa-solid fa-gauge-high"></i> ${(data.detection_confidence * 100).toFixed(0)}% Confidence`;

        const badgeFlag = document.getElementById('badgeFlag');
        const badgeCountryCode = document.getElementById('badgeCountryCode');
        if (badgeFlag) {
            if (!plateNotRecognized && data.country && data.country.includes('India')) {
                badgeFlag.textContent = '🇮🇳'; badgeCountryCode.textContent = 'IND';
            } else if (!plateNotRecognized && data.country && (data.country.includes('United Kingdom') || data.country.includes('UK'))) {
                badgeFlag.textContent = '🇬🇧'; badgeCountryCode.textContent = 'GBR';
            } else if (!plateNotRecognized && data.country && (data.country.includes('Germany') || data.country.includes('EU'))) {
                badgeFlag.textContent = '🇩🇪'; badgeCountryCode.textContent = 'DEU';
            } else if (!plateNotRecognized && data.country && (data.country.includes('United States') || data.country.includes('USA'))) {
                badgeFlag.textContent = '🇺🇸'; badgeCountryCode.textContent = 'USA';
            } else if (!plateNotRecognized && data.country && (data.country.includes('United Arab') || data.country.includes('UAE'))) {
                badgeFlag.textContent = '🇦🇪'; badgeCountryCode.textContent = 'UAE';
            } else if (plateNotRecognized) {
                badgeFlag.textContent = '❓'; badgeCountryCode.textContent = '???';
            } else {
                badgeFlag.textContent = '🌐'; badgeCountryCode.textContent = 'INT';
            }
        }

        // 4-Image Grid
        originalImage.src = resolveMediaUrl(data.original_image_url);
        annotatedImage.src = resolveMediaUrl(data.annotated_image_url);
        croppedPlateImage.src = resolveMediaUrl(data.cropped_plate_url);
        preprocessedPlateImage.src = resolveMediaUrl(data.preprocessed_plate_url);

        // OCR Tab Card
        resVehicleNumber.textContent = plateNotRecognized ? '— Not Readable —' : data.vehicle_number;
        resVehicleNumber.style.color = plateNotRecognized ? '#f87171' : '';
        resSeries.textContent  = plateNotRecognized ? '—' : (data.series || '—');
        resRegNum.textContent  = plateNotRecognized ? '—' : (data.registration_number || '—');
        resDetectConf.textContent = Math.round((data.detection_confidence || 0) * 100) + '%';
        resOcrConf.textContent    = plateNotRecognized ? 'N/A' : Math.round((data.ocr_confidence || 0) * 100) + '%';

        // Populate VAHAN-inspired original registration info portal
        const regCard = data.registration_info_card || {};
        const dash = '—';
        document.getElementById('vahanRegNum').textContent  = plateNotRecognized ? dash : (regCard.registration_number || data.vehicle_number || dash);
        document.getElementById('vahanCountry').textContent = plateNotRecognized ? dash : (regCard.country || data.country || dash);
        document.getElementById('vahanState').textContent   = plateNotRecognized ? dash : (regCard.state || data.state || dash);
        document.getElementById('vahanRtoCode').textContent = plateNotRecognized ? dash : (regCard.registration_code || data.rto_code || dash);
        document.getElementById('vahanArea').textContent    = plateNotRecognized ? dash : (regCard.registration_area || data.registration_area || dash);
        document.getElementById('vahanPlace').textContent   = plateNotRecognized ? dash : (regCard.rto_place_location || data.rto_place_location || dash);
        document.getElementById('vahanVehicleType').textContent = regCard.vehicle_category || data.vehicle_type || dash;
        document.getElementById('vahanDetectConf').textContent  = Math.round((data.detection_confidence || 0) * 100) + '%';
        document.getElementById('vahanOcrConf').textContent     = plateNotRecognized ? '0%' : Math.round((data.ocr_confidence || 0) * 100) + '%';
        document.getElementById('vahanSource').textContent      = plateNotRecognized ? 'N/A — plate not recognized' : (regCard.information_source || 'Public Web Sources');

        // Populate Lens tags
        const lensTagsContainer = document.getElementById('lensTagsContainer');
        if (lensTagsContainer) {
            if (data.lens_tags && data.lens_tags.length > 0) {
                lensTagsContainer.innerHTML = data.lens_tags.map(tag => `<span class="lens-tag-pill">${escapeHtml(tag)}</span>`).join('');
            } else {
                lensTagsContainer.innerHTML = '';
            }
        }

        // Render Public Web Pages
        renderPublicWebPages(data.public_web_pages || data.public_information || []);

        // Render Public Vehicle Images
        renderPublicVehicleImages(data.public_vehicle_images || []);

        // Render Related Pages
        renderRelatedPages(data.related_pages || []);

        // Render Sources List
        renderSourcesList(data.sources || []);

        // Reveal Populated State
        resultsEmptyState.classList.add('hidden');
        resultsPopulatedState.classList.remove('hidden');
        resultStatusPill.textContent = 'Automatic Search Complete';
        resultStatusPill.className = 'status-pill success';
    }

    function renderPublicWebPages(webList) {
        const container = document.getElementById('publicWebContainer');
        if (!container) return;

        if (!webList || webList.length === 0) {
            container.innerHTML = `<div class="public-empty-notice"><i class="fa-solid fa-circle-info"></i> No public web results found.</div>`;
            return;
        }

        let html = '';
        webList.forEach(item => {
            const relBadgeClass = item.relevance_label === 'Exact text match' ? 'exact' : 'potential';
            html += `
                <div class="public-info-item">
                    <span class="public-item-domain">${escapeHtml(item.source)}</span>
                    <span class="relevance-badge ${relBadgeClass}"><i class="fa-solid fa-tag"></i> ${escapeHtml(item.relevance_label || 'Public Reference')}</span>
                    <h4 class="public-item-title">${escapeHtml(item.title)}</h4>
                    <p class="public-item-desc">${escapeHtml(item.snippet)}</p>
                    ${item.url && item.url !== '#' ? `
                        <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer" class="btn-view-source">
                            View Source <i class="fa-solid fa-arrow-up-right-from-square"></i>
                        </a>
                    ` : ''}
                </div>
            `;
        });
        container.innerHTML = html;
    }

    function renderPublicVehicleImages(imgList) {
        const grid = document.getElementById('publicImagesGrid');
        if (!grid) return;

        if (!imgList || imgList.length === 0) {
            grid.innerHTML = `<div class="public-empty-notice"><i class="fa-solid fa-circle-info"></i> No public vehicle images found.</div>`;
            return;
        }

        let html = '';
        imgList.forEach(img => {
            html += `
                <div class="public-image-card">
                    <div class="img-card-preview">
                        <img src="${escapeHtml(img.image_url)}" alt="Public vehicle preview" loading="lazy" />
                    </div>
                    <div class="img-card-body">
                        <span class="img-card-source">${escapeHtml(img.source_name)}</span>
                        <h5 class="img-card-title">${escapeHtml(img.page_title)}</h5>
                        <p class="img-card-desc">${escapeHtml(img.description)}</p>
                        <div class="img-card-footer">
                            <span class="match-label-badge"><i class="fa-solid fa-camera"></i> ${escapeHtml(img.match_label || 'Potentially Related')}</span>
                            ${img.view_source_url && img.view_source_url !== '#' ? `
                                <a href="${escapeHtml(img.view_source_url)}" target="_blank" rel="noopener noreferrer" class="btn-view-source">
                                    View Source <i class="fa-solid fa-arrow-up-right-from-square"></i>
                                </a>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        grid.innerHTML = html;
    }

    function renderRelatedPages(pagesList) {
        const container = document.getElementById('relatedPagesContainer');
        if (!container) return;

        if (!pagesList || pagesList.length === 0) {
            container.innerHTML = `<div class="public-empty-notice"><i class="fa-solid fa-circle-info"></i> No related reference pages found.</div>`;
            return;
        }

        let html = '';
        pagesList.forEach(p => {
            html += `
                <div class="public-info-item">
                    <span class="public-item-domain">${escapeHtml(p.source)}</span>
                    <h4 class="public-item-title">${escapeHtml(p.title)}</h4>
                    <p class="public-item-desc">${escapeHtml(p.snippet)}</p>
                    ${p.url && p.url !== '#' ? `
                        <a href="${escapeHtml(p.url)}" target="_blank" rel="noopener noreferrer" class="btn-view-source">
                            View Source <i class="fa-solid fa-arrow-up-right-from-square"></i>
                        </a>
                    ` : ''}
                </div>
            `;
        });
        container.innerHTML = html;
    }

    function renderSourcesList(sources) {
        const container = document.getElementById('sourcesListContainer');
        if (!container) return;

        if (!sources || sources.length === 0) {
            container.innerHTML = `<div class="public-empty-notice"><i class="fa-solid fa-circle-info"></i> No public source links available.</div>`;
            return;
        }

        let html = '<ul class="sources-url-list" style="display:flex; flex-direction:column; gap:0.5rem; list-style:none;">';
        sources.forEach(url => {
            html += `
                <li style="background:rgba(255,255,255,0.03); padding:0.6rem 0.8rem; border-radius:6px; border:1px solid rgba(255,255,255,0.08);">
                    <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" style="color:var(--primary-cyan); text-decoration:none; word-break:break-all; font-size:0.85rem;">
                        <i class="fa-solid fa-link"></i> ${escapeHtml(url)}
                    </a>
                </li>
            `;
        });
        html += '</ul>';
        container.innerHTML = html;
    }

    // ── EXPAND / MODAL EVENT HANDLERS ───────────────────────
    document.getElementById('expandAnnotatedBtn').addEventListener('click', () => {
        openImageModal('YOLO Bounding Box Detection', annotatedImage.src);
    });

    document.getElementById('expandCropBtn').addEventListener('click', () => {
        openImageModal('OpenCV Cropped Plate ROI', croppedPlateImage.src);
    });

    document.getElementById('expandPrepBtn').addEventListener('click', () => {
        openImageModal('OpenCV Preprocessed Binary Plate', preprocessedPlateImage.src);
    });

    function openImageModal(title, src) {
        if (!src) return;
        modalTitle.textContent = title;
        modalImage.src = src;
        imageModal.classList.remove('hidden');
    }

    modalCloseBtn.addEventListener('click', () => imageModal.classList.add('hidden'));
    imageModal.addEventListener('click', (e) => {
        if (e.target === imageModal) imageModal.classList.add('hidden');
    });

    infoBtn.addEventListener('click', (e) => {
        e.preventDefault();
        infoModal.classList.remove('hidden');
    });
    infoModalCloseBtn.addEventListener('click', () => infoModal.classList.add('hidden'));

    // ── UTILITY FUNCTIONS ───────────────────────────────────
    function showError(msg) {
        errorMsg.textContent = msg;
        errorAlert.classList.remove('hidden');
    }

    function hideError() {
        errorAlert.classList.add('hidden');
    }

    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});

// ============================================================
// PLATE SEARCH SECTION — Live typing search with BeautifulSoup
// multi-engine backend (Google + DuckDuckGo + Bing)
// ============================================================

(function initPlateSearch() {

    // ── DOM refs ────────────────────────────────────────────
    const input          = document.getElementById('plateSearchInput');
    const mirrorEl       = document.getElementById('plateInputMirror');
    const searchBtn      = document.getElementById('plateSearchBtn');
    const clearBtn       = document.getElementById('plateSearchClearBtn');
    const acDropdown     = document.getElementById('plateAutocomplete');
    const acList         = document.getElementById('plateAcList');
    const quickChips     = document.querySelectorAll('.ps-chip');

    const stateIdle      = document.getElementById('psStateIdle');
    const stateLoading   = document.getElementById('psStateLoading');
    const stateError     = document.getElementById('psStateError');
    const errorMsg       = document.getElementById('psErrorMsg');
    const retryBtn       = document.getElementById('psRetryBtn');
    const loadingMsg     = document.getElementById('psLoadingMsg');

    const resultsPanel   = document.getElementById('psResultsPanel');

    // Registration card
    const psRegFlag      = document.getElementById('psRegFlag');
    const psRegPlateText = document.getElementById('psRegPlateText');
    const psRegState     = document.getElementById('psRegState');
    const psRegArea      = document.getElementById('psRegArea');
    const psRegRto       = document.getElementById('psRegRto');
    const psRegTags      = document.getElementById('psRegTags');

    const psWebCount     = document.getElementById('psWebCount');
    const psWebList      = document.getElementById('psWebResultsList');
    const psVahanGrid    = document.getElementById('psVahanGrid');
    const psRelatedList  = document.getElementById('psRelatedList');

    // Engine pills (loading state)
    const psEngGoogle    = document.getElementById('psEngGoogle');
    const psEngDDG       = document.getElementById('psEngDDG');
    const psEngBing      = document.getElementById('psEngBing');

    // ── State ───────────────────────────────────────────────
    let debounceTimer   = null;
    let acDebounce      = null;
    let lastQuery       = '';
    let searchAbortCtrl = null;
    const MIN_CHARS     = 3;     // start auto-search at 3 chars
    const DEBOUNCE_MS   = 600;   // wait 600ms after last keystroke
    const AC_DEBOUNCE   = 300;

    // ── Helpers ─────────────────────────────────────────────
    function esc(t) {
        if (!t) return '';
        return String(t)
            .replace(/&/g,'&amp;').replace(/</g,'&lt;')
            .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    function setState(name) {
        stateIdle.classList.add('hidden');
        stateLoading.classList.add('hidden');
        stateError.classList.add('hidden');
        resultsPanel.classList.add('hidden');
        if (name === 'idle')    stateIdle.classList.remove('hidden');
        if (name === 'loading') stateLoading.classList.remove('hidden');
        if (name === 'error')   stateError.classList.remove('hidden');
        if (name === 'results') resultsPanel.classList.remove('hidden');
    }

    function normalizePlate(raw) {
        return raw.toUpperCase().replace(/[^A-Z0-9]/g, '');
    }

    function getApiBase() {
        if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
            if (window.location.port === '5000') return window.location.origin;
            return `${window.location.protocol}//${window.location.hostname}:5000`;
        }
        // Opened directly from disk (file://) — use the local Flask backend
        return 'http://127.0.0.1:5000';
    }

    // ── Engine pill animation ───────────────────────────────
    let engineCycle = null;
    function startEngineCycle() {
        const pills = [psEngGoogle, psEngDDG, psEngBing];
        let i = 0;
        pills.forEach(p => p.classList.remove('active'));
        engineCycle = setInterval(() => {
            pills.forEach(p => p.classList.remove('active'));
            pills[i % pills.length].classList.add('active');
            i++;
        }, 600);
    }
    function stopEngineCycle() {
        if (engineCycle) { clearInterval(engineCycle); engineCycle = null; }
        [psEngGoogle, psEngDDG, psEngBing].forEach(p => p.classList.remove('active'));
    }

    // ── Input mirror (styled plate number live display) ─────
    function updateMirror(val) {
        const clean = normalizePlate(val);
        if (!mirrorEl) return;
        if (clean.length === 0) {
            mirrorEl.innerHTML = '';
            return;
        }
        // Color-segment the plate: STATE(2) + DIST(2) + SERIES(2) + NUM(4)
        const parts = clean.match(/^([A-Z]{2})(\d{1,2})?([A-Z]{1,3})?(\d{1,4})?(.*)$/) || [];
        let html = '';
        if (parts[1]) html += `<span class="pm-state">${parts[1]}</span>`;
        if (parts[2]) html += `<span class="pm-dist">${parts[2]}</span>`;
        if (parts[3]) html += `<span class="pm-series">${parts[3]}</span>`;
        if (parts[4]) html += `<span class="pm-num">${parts[4]}</span>`;
        if (parts[5]) html += `<span class="pm-extra">${parts[5]}</span>`;
        mirrorEl.innerHTML = html;
    }

    // ── Tab switching inside results panel ──────────────────
    document.querySelectorAll('.ps-rtab').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.ps-rtab').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.ps-tab-content').forEach(c => c.classList.add('hidden'));
            btn.classList.add('active');
            const target = document.getElementById(btn.dataset.pstab);
            if (target) target.classList.remove('hidden');
        });
    });

    // ── Autocomplete fetch ───────────────────────────────────
    function fetchAutocomplete(q) {
        clearTimeout(acDebounce);
        if (q.length < 2) { closeAutocomplete(); return; }
        acDebounce = setTimeout(async () => {
            try {
                const res = await fetch(`${getApiBase()}/autocomplete-plate?q=${encodeURIComponent(q)}`);
                const data = await res.json();
                renderAutocomplete(data.suggestions || []);
            } catch (_) { closeAutocomplete(); }
        }, AC_DEBOUNCE);
    }

    function renderAutocomplete(suggestions) {
        if (!suggestions.length) { closeAutocomplete(); return; }
        acList.innerHTML = suggestions.map((s, i) =>
            `<div class="ps-ac-item" role="option" tabindex="0" data-idx="${i}" data-url="${esc(s.url || '')}">
                <div class="ps-ac-title">${esc(s.display_text)}</div>
                ${s.snippet ? `<div class="ps-ac-snippet">${esc(s.snippet)}</div>` : ''}
                <span class="ps-ac-domain">${esc(s.domain || '')}</span>
            </div>`
        ).join('');
        acDropdown.classList.remove('hidden');

        acList.querySelectorAll('.ps-ac-item').forEach(item => {
            item.addEventListener('mousedown', (e) => {
                e.preventDefault();
                const url = item.dataset.url;
                if (url) window.open(url, '_blank', 'noopener');
                closeAutocomplete();
            });
        });
    }

    function closeAutocomplete() {
        acDropdown.classList.add('hidden');
        acList.innerHTML = '';
    }

    // ── Main search ──────────────────────────────────────────
    async function runSearch(raw) {
        const plate = normalizePlate(raw);
        if (plate === lastQuery && !resultsPanel.classList.contains('hidden')) return;
        if (plate.length < MIN_CHARS) { setState('idle'); return; }

        lastQuery = plate;

        // Abort any in-flight request
        if (searchAbortCtrl) searchAbortCtrl.abort();
        searchAbortCtrl = new AbortController();

        setState('loading');
        loadingMsg.textContent = `Searching "${plate}" across Google, DuckDuckGo & Bing…`;
        startEngineCycle();
        closeAutocomplete();

        try {
            const res = await fetch(`${getApiBase()}/search-plate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ plate }),
                signal: searchAbortCtrl.signal
            });

            stopEngineCycle();

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.error || `Server error ${res.status}`);
            }

            const data = await res.json();
            renderResults(data);
            setState('results');

        } catch (err) {
            stopEngineCycle();
            if (err.name === 'AbortError') return; // user typed again
            errorMsg.textContent = err.message || 'Search failed. Is the Flask backend running?';
            setState('error');
        }
    }

    // ── Render results ───────────────────────────────────────
    function renderResults(data) {
        const plate  = data.plate || lastQuery;
        const parsed = data.parsed || {};
        const card   = data.registration_info_card || {};
        const pages  = data.public_web_pages || [];
        const related = data.related_pages || [];
        const tags   = data.lens_tags || [];

        // Registration card header
        psRegPlateText.textContent = plate;
        psRegFlag.textContent = (card.country || '').includes('India') ? '🇮🇳' : '🌐';
        psRegState.textContent = card.state || parsed.state || '—';
        psRegArea.textContent  = card.registration_area || parsed.registration_area || '—';
        psRegRto.textContent   = card.registration_code || parsed.rto_code || '—';

        // Tags / lens pills
        psRegTags.innerHTML = tags.length
            ? tags.map(t => `<span class="ps-reg-tag">${esc(t)}</span>`).join('')
            : '';

        // Web results count badge
        psWebCount.textContent = pages.length;

        // ── Web Results Tab ──────────────────────────────────
        if (!pages.length) {
            psWebList.innerHTML = `<div class="ps-empty"><i class="fa-solid fa-circle-info"></i> No public web results found for <b>${esc(plate)}</b>.</div>`;
        } else {
            psWebList.innerHTML = pages.map(item => {
                const engineClass = (item.source_engine || '').toLowerCase() === 'google'     ? 'google'
                                  : (item.source_engine || '').toLowerCase() === 'bing'       ? 'bing'
                                  : (item.source_engine || '').toLowerCase() === 'duckduckgo' ? 'ddg'
                                  : 'other';
                const relClass = (item.relevance_label || '').toLowerCase().includes('exact') ? 'exact' : 'potential';
                return `<div class="ps-web-item">
                    <div class="ps-web-item-top">
                        <span class="ps-web-domain">${esc(item.source || item.domain || '')}</span>
                        ${item.source_engine ? `<span class="ps-engine-tag ${engineClass}">${esc(item.source_engine)}</span>` : ''}
                        <span class="relevance-badge ${relClass}">
                            <i class="fa-solid fa-tag"></i> ${esc(item.relevance_label || 'Public Reference')}
                        </span>
                    </div>
                    <h4 class="ps-web-title">${esc(item.title)}</h4>
                    <p class="ps-web-snippet">${esc(item.snippet)}</p>
                    ${item.url && item.url !== '#'
                        ? `<a href="${esc(item.url)}" target="_blank" rel="noopener noreferrer" class="btn-view-source">
                                View Source <i class="fa-solid fa-arrow-up-right-from-square"></i>
                           </a>`
                        : ''}
                </div>`;
            }).join('');
        }

        // ── Registration Info Tab ────────────────────────────
        const regFields = [
            ['Registration Number', card.registration_number || plate, true],
            ['Country',             card.country || '—',               false],
            ['State / Region',      card.state || parsed.state || '—', false],
            ['RTO Code',            card.registration_code || parsed.rto_code || '—', false],
            ['Registration Area',   card.registration_area || '—',     false],
            ['RTO Office Location', card.rto_place_location || '—',    false],
            ['Vehicle Category',    card.vehicle_category || '—',      false],
            ['Series',              card.series || '—',                false],
            ['Number Digits',       card.number_digits || '—',         false],
            ['Information Source',  card.information_source || 'Public Web Sources', false],
            ['Owner Information',   'Not Available',                   false, 'privacy'],
            ['Phone / Address',     'Not Available',                   false, 'privacy'],
        ];
        psVahanGrid.innerHTML = regFields.map(([label, val, highlight, statusType]) => `
            <div class="vahan-item">
                <span class="vahan-label">${esc(label)}</span>
                <span class="vahan-value${highlight ? ' highlight' : ''}">${esc(val)}</span>
                <span class="vahan-status ${statusType === 'privacy' ? 'privacy' : 'verified'}">
                    <i class="fa-solid ${statusType === 'privacy' ? 'fa-user-shield' : 'fa-circle-check'}"></i>
                    ${statusType === 'privacy' ? 'Strictly Privacy Protected' : 'Verified Public Information'}
                </span>
            </div>
        `).join('');

        // ── Related Pages Tab ─────────────────────────────────
        if (!related.length) {
            psRelatedList.innerHTML = `<div class="ps-empty"><i class="fa-solid fa-circle-info"></i> No related pages found.</div>`;
        } else {
            psRelatedList.innerHTML = related.map(p => `
                <div class="ps-web-item">
                    <span class="ps-web-domain">${esc(p.source || '')}</span>
                    <h4 class="ps-web-title">${esc(p.title)}</h4>
                    <p class="ps-web-snippet">${esc(p.snippet)}</p>
                    ${p.url && p.url !== '#'
                        ? `<a href="${esc(p.url)}" target="_blank" rel="noopener noreferrer" class="btn-view-source">
                                View Source <i class="fa-solid fa-arrow-up-right-from-square"></i>
                           </a>`
                        : ''}
                </div>
            `).join('');
        }

        // Reset to Web tab
        document.querySelectorAll('.ps-rtab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.ps-tab-content').forEach(c => c.classList.add('hidden'));
        const webTabBtn = document.querySelector('.ps-rtab[data-pstab="psTabWeb"]');
        if (webTabBtn) webTabBtn.classList.add('active');
        document.getElementById('psTabWeb').classList.remove('hidden');
    }

    // ── Input events ─────────────────────────────────────────
    input.addEventListener('input', () => {
        const val = input.value.trim();
        const clean = normalizePlate(val);

        // Update mirror
        updateMirror(val);

        // Show/hide clear button
        clearBtn.classList.toggle('hidden', val.length === 0);

        // Autocomplete suggestions
        fetchAutocomplete(clean);

        // Debounced auto-search
        clearTimeout(debounceTimer);
        if (clean.length < MIN_CHARS) {
            if (clean.length === 0) setState('idle');
            return;
        }
        debounceTimer = setTimeout(() => runSearch(val), DEBOUNCE_MS);
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            clearTimeout(debounceTimer);
            closeAutocomplete();
            runSearch(input.value.trim());
        }
        if (e.key === 'Escape') {
            closeAutocomplete();
        }
    });

    // Close autocomplete on outside click
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !acDropdown.contains(e.target)) {
            closeAutocomplete();
        }
    });

    // Search button
    searchBtn.addEventListener('click', () => {
        clearTimeout(debounceTimer);
        closeAutocomplete();
        runSearch(input.value.trim());
    });

    // Clear button
    clearBtn.addEventListener('click', () => {
        input.value = '';
        mirrorEl.innerHTML = '';
        clearBtn.classList.add('hidden');
        lastQuery = '';
        closeAutocomplete();
        setState('idle');
        if (searchAbortCtrl) searchAbortCtrl.abort();
    });

    // Retry button
    retryBtn.addEventListener('click', () => runSearch(input.value.trim()));

    // Quick chip buttons
    quickChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const plate = chip.dataset.plate;
            input.value = plate;
            updateMirror(plate);
            clearBtn.classList.remove('hidden');
            clearTimeout(debounceTimer);
            runSearch(plate);
        });
    });

    // Initial state
    setState('idle');

})();
