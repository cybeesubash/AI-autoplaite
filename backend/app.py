# ============================================================
# app.py  –  Flask REST API Server
# Title: AI-Based Indian Vehicle Number Plate Detection,
#        Recognition & Public Information Search System
# ============================================================

import os
import sys

# Ensure workspace root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import uuid
import cv2
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from backend.detection import detect_vehicles_and_plates, crop_plate, draw_bounding_boxes, process_video_file
from backend.ocr import recognize_plate
from backend.web_search import search_public_info, get_plate_suggestions
from backend.scraping import search_plate_number, extract_public_page_snippet
from backend.utils import parse_indian_plate

# Initialize Flask App
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers="*", methods=["GET", "POST", "OPTIONS"])

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}


def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set


# ── REST API ENDPOINTS ──────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "system": "AI-Based Indian Vehicle Number Plate Detection, Recognition & Public Information Search System",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route('/detect', methods=['POST'])
def detect_image_endpoint():
    """Process uploaded vehicle image and recognize Indian number plate."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({"error": "Unsupported image format. Upload JPG, PNG, WEBP."}), 400

    unique_id = uuid.uuid4().hex[:8]
    ext = file.filename.rsplit('.', 1)[1].lower()
    input_filename = f"upload_{unique_id}.{ext}"
    input_path = os.path.join(UPLOADS_DIR, input_filename)
    file.save(input_path)

    try:
        # 1. Run YOLO Vehicle & License Plate Detection
        det = detect_vehicles_and_plates(input_path)

        # 2. Crop Plate ROI using OpenCV
        cropped_plate_bgr = crop_plate(input_path, det["plate_bbox"])

        # 3. Save Cropped Plate Image
        cropped_filename = f"cropped_{unique_id}.jpg"
        cropped_path = os.path.join(RESULTS_DIR, cropped_filename)
        cv2.imwrite(cropped_path, cropped_plate_bgr)

        # 4. Save Annotated Full Scene Image
        annotated_filename = f"annotated_{unique_id}.jpg"
        annotated_path = os.path.join(RESULTS_DIR, annotated_filename)
        draw_bounding_boxes(input_path, det, annotated_path)

        # 5. Run Preprocessing & Tesseract OCR + Indian RTO Parsing
        ocr_result = recognize_plate(cropped_plate_bgr)

        # 6. Save Preprocessed Binary Plate Image
        preprocessed_filename = f"prep_{unique_id}.jpg"
        preprocessed_path = os.path.join(RESULTS_DIR, preprocessed_filename)
        if ocr_result.get("preprocessed_img") is not None:
            cv2.imwrite(preprocessed_path, ocr_result["preprocessed_img"])
        else:
            cv2.imwrite(preprocessed_path, cv2.cvtColor(cropped_plate_bgr, cv2.COLOR_BGR2GRAY))

        now_str = datetime.now().strftime("%I:%M %p, %b %d %Y")
        cropped_url = f"/results/{cropped_filename}"
        annotated_url = f"/results/{annotated_filename}"

        # 7. Only run web search if OCR produced a real plate number
        ocr_status = ocr_result.get("ocr_status", "ok")
        plate_recognized = (
            ocr_status not in ("ocr_failed", "unrecognized_format")
            and ocr_result.get("vehicle_number", "UNKNOWN") != "UNKNOWN"
            and len(ocr_result.get("vehicle_number", "")) >= 4
        )

        if plate_recognized:
            plate_num = ocr_result["vehicle_number"]

            # Run full public info search (RTO card + DuckDuckGo)
            pub_info_res = search_public_info(
                plate_num,
                vehicle_type=det["vehicle_type"],
                cropped_url=cropped_url,
                annotated_url=annotated_url
            )

            # Also run multi-engine BeautifulSoup scrape (Google + DDG + Bing)
            scraped = search_plate_number(plate_num, max_results=12)

            # Merge scraped results — dedupe by URL
            existing_urls = {r.get("url") for r in pub_info_res.get("public_web_pages", [])}
            for r in scraped:
                if r.get("url") not in existing_urls:
                    pub_info_res["public_web_pages"].append({
                        "title": r["title"],
                        "snippet": r["snippet"],
                        "source": r.get("domain", r.get("source_engine", "Web")),
                        "url": r["url"],
                        "relevance_label": r.get("relevance_label", "Potentially related"),
                        "source_engine": r.get("source_engine", "")
                    })
                    existing_urls.add(r["url"])
                    pub_info_res.setdefault("sources", []).append(r["url"])
        else:
            pub_info_res = {
                "registration_info_card": {},
                "public_web_pages": [],
                "public_vehicle_images": [],
                "related_pages": [],
                "status_fields": {},
                "public_information": [],
                "lens_tags": [],
                "sources": []
            }

        response_data = {
            "vehicle_number": ocr_result["vehicle_number"],
            "ocr_status": ocr_status,
            "ocr_failure_reason": ocr_result.get("ocr_failure_reason", ""),
            "plate_recognized": plate_recognized,
            "vehicle_type": det["vehicle_type"],
            "country": ocr_result.get("country", "—"),
            "country_code": ocr_result.get("country_code", "—"),
            "state": ocr_result.get("state", "—"),
            "state_code": ocr_result.get("state_code", "—"),
            "rto_code": ocr_result.get("rto_code", "—"),
            "registration_area": ocr_result.get("registration_area", "—"),
            "rto_place_location": ocr_result.get("rto_place_location", "—"),
            "series": ocr_result.get("series", "—"),
            "registration_number": ocr_result.get("registration_number", "—"),
            "detection_confidence": det["plate_conf"],
            "ocr_confidence": ocr_result["ocr_confidence"],
            "detection_time": now_str,
            "original_image_url": f"/uploads/{input_filename}",
            "annotated_image_url": annotated_url,
            "cropped_plate_url": cropped_url,
            "preprocessed_plate_url": f"/results/{preprocessed_filename}",
            "registration_info_card": pub_info_res.get("registration_info_card", {}),
            "public_web_pages": pub_info_res.get("public_web_pages", []),
            "public_vehicle_images": pub_info_res.get("public_vehicle_images", []),
            "related_pages": pub_info_res.get("related_pages", []),
            "status_fields": pub_info_res.get("status_fields", {}),
            "public_information": pub_info_res.get("public_information", []),
            "lens_tags": pub_info_res.get("lens_tags", []),
            "sources": pub_info_res.get("sources", [])
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"[Error /detect]: {e}")
        return jsonify({"error": f"Detection failed: {str(e)}"}), 500


@app.route('/detect-video', methods=['POST'])
def detect_video_endpoint():
    """Process uploaded vehicle video, sample keyframes, and recognize number plate."""
    if 'file' not in request.files:
        return jsonify({"error": "No video file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected video file"}), 400

    if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        return jsonify({"error": "Unsupported video format. Upload MP4, AVI, MOV."}), 400

    unique_id = uuid.uuid4().hex[:8]
    ext = file.filename.rsplit('.', 1)[1].lower()
    video_filename = f"video_{unique_id}.{ext}"
    video_path = os.path.join(UPLOADS_DIR, video_filename)
    file.save(video_path)

    try:
        # Extract best frame and detection result
        best_frame, det = process_video_file(video_path)

        # Save frame to disk
        frame_filename = f"frame_{unique_id}.jpg"
        frame_path = os.path.join(UPLOADS_DIR, frame_filename)
        cv2.imwrite(frame_path, best_frame)

        # Crop plate ROI
        cropped_plate_bgr = crop_plate(frame_path, det["plate_bbox"])
        cropped_filename = f"cropped_{unique_id}.jpg"
        cropped_path = os.path.join(RESULTS_DIR, cropped_filename)
        cv2.imwrite(cropped_path, cropped_plate_bgr)

        # Draw annotated frame
        annotated_filename = f"annotated_{unique_id}.jpg"
        annotated_path = os.path.join(RESULTS_DIR, annotated_filename)
        draw_bounding_boxes(frame_path, det, annotated_path)

        # OCR Recognition
        ocr_result = recognize_plate(cropped_plate_bgr)

        preprocessed_filename = f"prep_{unique_id}.jpg"
        preprocessed_path = os.path.join(RESULTS_DIR, preprocessed_filename)
        if ocr_result.get("preprocessed_img") is not None:
            cv2.imwrite(preprocessed_path, ocr_result["preprocessed_img"])
        else:
            cv2.imwrite(preprocessed_path, cv2.cvtColor(cropped_plate_bgr, cv2.COLOR_BGR2GRAY))

        now_str = datetime.now().strftime("%I:%M %p, %b %d %Y")

        cropped_url = f"/results/{cropped_filename}"
        annotated_url = f"/results/{annotated_filename}"

        # Only run web search if OCR produced a real plate number
        ocr_status = ocr_result.get("ocr_status", "ok")
        plate_recognized = (
            ocr_status not in ("ocr_failed", "unrecognized_format")
            and ocr_result.get("vehicle_number", "UNKNOWN") != "UNKNOWN"
            and len(ocr_result.get("vehicle_number", "")) >= 4
        )

        if plate_recognized:
            plate_num = ocr_result["vehicle_number"]

            # Run full public info search (RTO card + DuckDuckGo)
            pub_info_res = search_public_info(
                plate_num,
                vehicle_type=det["vehicle_type"],
                cropped_url=cropped_url,
                annotated_url=annotated_url
            )

            # Also run multi-engine BeautifulSoup scrape (Google + DDG + Bing)
            scraped = search_plate_number(plate_num, max_results=12)

            # Merge scraped results — dedupe by URL
            existing_urls = {r.get("url") for r in pub_info_res.get("public_web_pages", [])}
            for r in scraped:
                if r.get("url") not in existing_urls:
                    pub_info_res["public_web_pages"].append({
                        "title": r["title"],
                        "snippet": r["snippet"],
                        "source": r.get("domain", r.get("source_engine", "Web")),
                        "url": r["url"],
                        "relevance_label": r.get("relevance_label", "Potentially related"),
                        "source_engine": r.get("source_engine", "")
                    })
                    existing_urls.add(r["url"])
                    pub_info_res.setdefault("sources", []).append(r["url"])
        else:
            pub_info_res = {
                "registration_info_card": {},
                "public_web_pages": [],
                "public_vehicle_images": [],
                "related_pages": [],
                "status_fields": {},
                "public_information": [],
                "lens_tags": [],
                "sources": []
            }

        response_data = {
            "vehicle_number": ocr_result["vehicle_number"],
            "ocr_status": ocr_status,
            "ocr_failure_reason": ocr_result.get("ocr_failure_reason", ""),
            "plate_recognized": plate_recognized,
            "vehicle_type": det["vehicle_type"],
            "country": ocr_result.get("country", "—"),
            "country_code": ocr_result.get("country_code", "—"),
            "state": ocr_result.get("state", "—"),
            "state_code": ocr_result.get("state_code", "—"),
            "rto_code": ocr_result.get("rto_code", "—"),
            "registration_area": ocr_result.get("registration_area", "—"),
            "rto_place_location": ocr_result.get("rto_place_location", "—"),
            "series": ocr_result.get("series", "—"),
            "registration_number": ocr_result.get("registration_number", "—"),
            "detection_confidence": det["plate_conf"],
            "ocr_confidence": ocr_result["ocr_confidence"],
            "detection_time": now_str,
            "original_image_url": f"/uploads/{frame_filename}",
            "annotated_image_url": annotated_url,
            "cropped_plate_url": cropped_url,
            "preprocessed_plate_url": f"/results/{preprocessed_filename}",
            "registration_info_card": pub_info_res.get("registration_info_card", {}),
            "public_web_pages": pub_info_res.get("public_web_pages", []),
            "public_vehicle_images": pub_info_res.get("public_vehicle_images", []),
            "related_pages": pub_info_res.get("related_pages", []),
            "status_fields": pub_info_res.get("status_fields", {}),
            "public_information": pub_info_res.get("public_information", []),
            "lens_tags": pub_info_res.get("lens_tags", []),
            "sources": pub_info_res.get("sources", [])
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"[Error /detect-video]: {e}")
        return jsonify({"error": f"Video analysis failed: {str(e)}"}), 500


@app.route('/search-public-info', methods=['POST'])
def search_public_info_endpoint():
    """Perform non-sensitive public web search for recognized vehicle number."""
    data = request.get_json() or {}
    vehicle_number = data.get("vehicle_number", "").strip()
    vehicle_type = data.get("vehicle_type", "Car").strip()

    if not vehicle_number:
        return jsonify({"error": "Vehicle number required"}), 400

    results = search_public_info(vehicle_number, vehicle_type=vehicle_type)
    return jsonify(results), 200


# ── PLATE TEXT SEARCH ENDPOINTS ────────────────────────────

@app.route('/search-plate', methods=['POST'])
def search_plate_endpoint():
    """
    Live public web search for a manually typed vehicle number plate.
    Triggered by frontend on user input (debounced).
    Returns multi-engine scraped results + parsed registration info.
    """
    data = request.get_json(force=True, silent=True) or {}
    plate = data.get("plate", "") or request.form.get("plate", "") or request.args.get("plate", "")
    plate = str(plate).strip().upper()

    if not plate or len(plate) < 2:
        return jsonify({"error": "Plate number too short"}), 400

    try:
        # 1. Parse plate for registration info card
        parsed = parse_indian_plate(plate)

        # 2. Multi-engine BeautifulSoup scrape (Google + DDG + Bing)
        scraped = search_plate_number(plate, max_results=12)

        # 3. Also run the full public info search (web + images + RTO card)
        pub_info = search_public_info(
            plate,
            vehicle_type=parsed.get("vehicle_type", "Car"),
            cropped_url="",
            annotated_url=""
        )

        # 4. Merge scraped results into public_web_pages (dedupe by URL)
        existing_urls = {r.get("url") for r in pub_info.get("public_web_pages", [])}
        for r in scraped:
            if r.get("url") not in existing_urls:
                pub_info["public_web_pages"].append({
                    "title": r["title"],
                    "snippet": r["snippet"],
                    "source": r.get("domain", r.get("source_engine", "Web")),
                    "url": r["url"],
                    "relevance_label": r.get("relevance_label", "Potentially related"),
                    "source_engine": r.get("source_engine", "")
                })
                existing_urls.add(r["url"])

        return jsonify({
            "plate": plate,
            "parsed": parsed,
            "registration_info_card": pub_info.get("registration_info_card", {}),
            "public_web_pages": pub_info.get("public_web_pages", [])[:12],
            "related_pages": pub_info.get("related_pages", []),
            "sources": pub_info.get("sources", []),
            "status_fields": pub_info.get("status_fields", {}),
            "lens_tags": pub_info.get("lens_tags", []),
            "scraped_count": len(scraped),
        }), 200

    except Exception as e:
        print(f"[Error /search-plate]: {e}")
        return jsonify({"error": f"Search failed: {str(e)}"}), 500


@app.route('/autocomplete-plate', methods=['GET'])
def autocomplete_plate_endpoint():
    """
    Fast autocomplete suggestions for plate number prefix (typed in search box).
    Returns lightweight suggestion list for dropdown.
    """
    q = request.args.get("q", "").strip().upper()
    if not q or len(q) < 2:
        return jsonify({"suggestions": []}), 200

    try:
        suggestions = get_plate_suggestions(q, max_suggestions=6)
        return jsonify({"suggestions": suggestions}), 200
    except Exception as e:
        print(f"[Error /autocomplete-plate]: {e}")
        return jsonify({"suggestions": []}), 200


# ── STATIC FILE & FRONTEND ROUTING ──────────────────────────

@app.route('/uploads/<filename>')
def serve_uploads(filename):
    return send_from_directory(UPLOADS_DIR, secure_filename(filename))


@app.route('/results/<filename>')
def serve_results(filename):
    return send_from_directory(RESULTS_DIR, secure_filename(filename))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    PORT = int(os.environ.get("PORT", 5000))
    print("=" * 70)
    print("[*] Starting Flask REST API Backend Server")
    print("Title: AI-Based Indian Vehicle Number Plate Detection, Recognition & Public Information Search System")
    print(f"Server running at: http://127.0.0.1:{PORT}")
    print("=" * 70)
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False, threaded=True)
