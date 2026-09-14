# ============================================================
# ocr.py  –  Hybrid EasyOCR + OpenCV Contour Number Plate Scanner
# Title: AI-Based Global & Indian Vehicle Registration Portal
# ============================================================

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import cv2
import numpy as np
import re
from backend.preprocessing import preprocess_plate_pipeline
from backend.utils import parse_indian_plate

# ── TESSERACT OCR SETUP ───────────────────────────────────
import pytesseract
import shutil

TESSERACT_CMD_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\ABINESH S\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
    r"C:\Users\ABINESH S\anaconda4\Library\bin\tesseract.exe",
    # Linux (Render / Docker) typical locations
    "/usr/bin/tesseract",
    "/usr/local/bin/tesseract",
    "/app/.apt/usr/bin/tesseract",
]

TESSERACT_AVAILABLE = False
_detected_tesseract = shutil.which("tesseract")
if _detected_tesseract:
    pytesseract.pytesseract.tesseract_cmd = _detected_tesseract
    TESSERACT_AVAILABLE = True
else:
    for path in TESSERACT_CMD_PATHS:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            TESSERACT_AVAILABLE = True
            break

# ── EASYOCR SETUP: Lazy init on first use ─────────────────────────────────
EASYOCR_READER = None
EASYOCR_AVAILABLE = False
EASYOCR_TRIED = False

try:
    import easyocr as _easyocr_module
    EASYOCR_AVAILABLE = True  # module importable
    print("[OCR] EasyOCR package found. Will initialize on first plate scan.")
except ImportError:
    print("[OCR] EasyOCR not installed. Run: pip install easyocr")


def _get_easyocr_reader():
    """Lazy-init EasyOCR reader — loads model on first call, cached after."""
    global EASYOCR_READER, EASYOCR_TRIED, EASYOCR_AVAILABLE
    if EASYOCR_TRIED:
        return EASYOCR_READER
    EASYOCR_TRIED = True
    if not EASYOCR_AVAILABLE:
        return None
    try:
        print("[OCR] Initializing EasyOCR reader (first run, downloading models if needed)...")
        EASYOCR_READER = _easyocr_module.Reader(['en'], gpu=False, verbose=False)
        print("[OCR] EasyOCR reader ready.")
    except Exception as e:
        print(f"[OCR] EasyOCR init failed: {e}. Will use OpenCV fallback.")
        EASYOCR_AVAILABLE = False
        EASYOCR_READER = None
    return EASYOCR_READER


def run_easyocr(bgr_img):
    """Run EasyOCR on the image and return best alphanumeric text.
    Tries multiple scales, sorts segments left-to-right, picks best valid result."""
    reader = _get_easyocr_reader()
    if reader is None:
        return ""

    def _read_single(img):
        try:
            results = reader.readtext(
                img,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                detail=1,
                paragraph=False,
                width_ths=0.7,
                ycenter_ths=0.5
            )
            if not results:
                return ""
            # Sort strictly left-to-right by leftmost x of bounding box
            results_sorted = sorted(results, key=lambda r: r[0][0][0])
            text = "".join([r[1].upper() for r in results_sorted])
            return re.sub(r'[^A-Z0-9]', '', text)
        except Exception as e:
            print(f"[EasyOCR] Note: {e}")
            return ""

    candidates = []

    # Original size
    t = _read_single(bgr_img)
    if t:
        candidates.append(t)

    # Upscaled 2x — helps with small plates
    h, w = bgr_img.shape[:2]
    upscaled = cv2.resize(bgr_img, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
    t2 = _read_single(upscaled)
    if t2:
        candidates.append(t2)

    # Upscaled 3x with sharpening
    upscaled3 = cv2.resize(bgr_img, (w * 3, h * 3), interpolation=cv2.INTER_LANCZOS4)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(upscaled3, -1, kernel)
    t3 = _read_single(sharpened)
    if t3:
        candidates.append(t3)

    if not candidates:
        return ""

    # Pick the candidate that best matches Indian plate pattern after correction
    from backend.utils import fix_ocr_confusion, INDIAN_STATES
    for cand in candidates:
        corrected = fix_ocr_confusion(cand)
        if re.match(r'^[A-Z]{2}\d{2}[A-Z]{1,3}\d{1,4}$', corrected):
            if corrected[:2] in INDIAN_STATES:
                print(f"[EasyOCR] Best candidate: {cand} → {corrected}")
                return corrected

    # Return longest candidate as fallback
    return max(candidates, key=len)


def run_tesseract(preprocessed_img):
    """Run Tesseract OCR on preprocessed plate image."""
    if not TESSERACT_AVAILABLE:
        return "", 0.0

    raw_text = ""
    avg_conf = 0.0

    configs = [
        r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        r'--oem 3 --psm 11 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    ]

    for config in configs:
        try:
            data = pytesseract.image_to_data(preprocessed_img, config=config, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data.get('conf', []) if isinstance(c, (int, str)) and str(c).isdigit() and int(c) > 0]
            text = pytesseract.image_to_string(preprocessed_img, config=config).strip()
            clean = re.sub(r'[^A-Z0-9]', '', text.upper())
            if len(clean) >= 4:
                avg_conf = round(float(np.mean(confidences)) / 100.0, 2) if confidences else 0.85
                raw_text = clean
                break
        except Exception as e:
            print(f"[Tesseract] Config {config}: {e}")

    return raw_text, avg_conf


def run_opencv_contour_scanner(preprocessed_img):
    """
    Emergency fallback OCR: Contour character segmentation + morphological analysis.
    Extracts characters from binary plate ROI without Tesseract or EasyOCR.
    """
    if preprocessed_img is None or preprocessed_img.size == 0:
        return ""

    h, w = preprocessed_img.shape[:2]

    # Apply morphological closing to join character fragments
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(preprocessed_img, cv2.MORPH_CLOSE, kernel)

    # Try both binary and inverted binary
    candidates = []
    for binary in [closed, cv2.bitwise_not(closed)]:
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue

        char_boxes = []
        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            aspect = ch / float(cw) if cw > 0 else 0
            height_ratio = ch / float(h)
            area = (cw * ch) / float(w * h)

            if 0.8 <= aspect <= 5.5 and 0.2 <= height_ratio <= 0.95 and 0.004 <= area <= 0.3:
                if x > 1 and (x + cw) < (w - 1):
                    char_boxes.append((x, y, cw, ch))

        char_boxes = sorted(char_boxes, key=lambda b: b[0])

        # De-overlap
        filtered = []
        for box in char_boxes:
            if not filtered:
                filtered.append(box)
            else:
                prev_x, _, prev_w, _ = filtered[-1]
                if (box[0] - prev_x) > (prev_w * 0.3):
                    filtered.append(box)

        if 4 <= len(filtered) <= 12:
            candidates.append((len(filtered), filtered, binary))

    if not candidates:
        return ""

    # Use the candidate with the most sensible character count (6-12)
    candidates.sort(key=lambda x: abs(x[0] - 10))
    _, best_boxes, best_binary = candidates[0]

    # OCR each character ROI using EasyOCR if available
    _reader = _get_easyocr_reader()
    if _reader is not None:
        all_chars = []
        for x, y, cw, ch in best_boxes:
            roi = best_binary[max(0, y-2):min(h, y+ch+2), max(0, x-2):min(w, x+cw+2)]
            if roi.size == 0:
                continue
            roi_bgr = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
            roi_big = cv2.resize(roi_bgr, (cw*3, ch*3), interpolation=cv2.INTER_CUBIC)
            try:
                results = _reader.readtext(roi_big, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', detail=0)
                if results:
                    char = re.sub(r'[^A-Z0-9]', '', results[0].upper())
                    if char:
                        all_chars.append(char[0])
            except Exception:
                pass
        if len(all_chars) >= 4:
            return "".join(all_chars)

    return ""


def recognize_plate(cropped_bgr_img):
    """
    Full Hybrid OCR Pipeline:
    1. EasyOCR with multi-scale + sharpening (best accuracy)
    2. Tesseract OCR with multiple PSM configs
    3. OpenCV Contour Scanner (emergency fallback)
    Picks the best result by checking Indian plate format validity.
    """
    if cropped_bgr_img is None or cropped_bgr_img.size == 0:
        parsed = parse_indian_plate("")
        parsed["ocr_confidence"] = 0.0
        parsed["preprocessed_img"] = None
        parsed["ocr_status"] = "ocr_failed"
        parsed["ocr_failure_reason"] = "No plate region could be cropped from the image."
        return parsed

    # ── Preprocessing Pipeline ──────────────────────────
    preprocessed_img = preprocess_plate_pipeline(cropped_bgr_img)
    if preprocessed_img is None:
        preprocessed_img = cv2.cvtColor(cropped_bgr_img, cv2.COLOR_BGR2GRAY)

    # Helper: score a candidate — higher = more Indian-plate-like
    def score_candidate(text):
        if not text or len(text) < 6:
            return 0
        from backend.utils import fix_ocr_confusion, INDIAN_STATES
        corrected = fix_ocr_confusion(text)
        if re.match(r'^[A-Z]{2}\d{2}[A-Z]{1,3}\d{1,4}$', corrected) and corrected[:2] in INDIAN_STATES:
            return 3  # perfect Indian match
        if re.match(r'^[A-Z]{2}\d{2}', corrected) and corrected[:2] in INDIAN_STATES:
            return 2  # partial Indian match
        if len(corrected) >= 6:
            return 1  # something was read
        return 0

    all_candidates = []  # list of (text, conf, source)

    # ── Stage 1: EasyOCR (multi-scale, sorted L→R) ───────
    easyocr_text = run_easyocr(cropped_bgr_img)
    if easyocr_text:
        all_candidates.append((easyocr_text, 0.94, "EasyOCR"))
        print(f"[OCR-EasyOCR] Extracted: {easyocr_text}")

    # ── Stage 2: Tesseract OCR ─────────────────────────────
    tess_text, tess_conf = run_tesseract(preprocessed_img)
    if tess_text:
        all_candidates.append((tess_text, tess_conf, "Tesseract"))
        print(f"[OCR-Tesseract] Extracted: {tess_text}")

    # Also try Tesseract on original gray (not binarized)
    gray_orig = cv2.cvtColor(cropped_bgr_img, cv2.COLOR_BGR2GRAY)
    gray_resized = cv2.resize(gray_orig, (gray_orig.shape[1]*2, gray_orig.shape[0]*2), interpolation=cv2.INTER_CUBIC)
    tess_text2, tess_conf2 = run_tesseract(gray_resized)
    if tess_text2 and tess_text2 != tess_text:
        all_candidates.append((tess_text2, tess_conf2, "Tesseract-Gray"))
        print(f"[OCR-Tesseract-Gray] Extracted: {tess_text2}")

    # ── Stage 3: OpenCV Contour Scanner ──────────────────
    contour_text = run_opencv_contour_scanner(preprocessed_img)
    if contour_text:
        all_candidates.append((contour_text, 0.78, "Contour"))
        print(f"[OCR-Contour] Extracted: {contour_text}")

    # ── Pick best candidate ───────────────────────────────
    raw_text = ""
    avg_conf = 0.0

    if all_candidates:
        # Sort by score descending, then confidence descending
        scored = sorted(all_candidates, key=lambda x: (score_candidate(x[0]), x[1]), reverse=True)
        raw_text, avg_conf, source = scored[0]
        print(f"[OCR] Best result from {source}: '{raw_text}' (score={score_candidate(raw_text)})")

    print(f"[OCR] Final OCR result: '{raw_text}'")

    # Parse and validate registration number format
    parsed = parse_indian_plate(raw_text)
    parsed["ocr_confidence"] = avg_conf if raw_text else 0.0
    parsed["preprocessed_img"] = preprocessed_img

    # Tag OCR failure clearly so the app layer can handle it honestly
    if not raw_text:
        parsed["ocr_status"] = "ocr_failed"
        parsed["ocr_failure_reason"] = (
            "No readable text found in plate region. "
            "Possible causes: image blur, low resolution, bad angle, or plate obstruction."
        )
    elif parsed.get("ocr_status") == "unrecognized_format":
        parsed["ocr_failure_reason"] = (
            f"OCR read '{raw_text}' but it does not match any known plate format."
        )

    return parsed
