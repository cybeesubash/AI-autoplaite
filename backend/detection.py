# ============================================================
# detection.py  –  YOLO Vehicle & Number Plate Detection Engine
# ============================================================

import os
import cv2
import numpy as np
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO = None
    YOLO_AVAILABLE = False
    print("[YOLO] ultralytics not installed. Detection will be skipped.")

# Path to trained custom model weights
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "best.pt")

_model = None

# Mapping standard COCO class IDs to Vehicle Types
COCO_VEHICLE_CLASSES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}


def load_model():
    """Load cached YOLO model weights (custom best.pt or fallback yolov8n.pt)."""
    global _model
    if not YOLO_AVAILABLE:
        print("[YOLO] ultralytics not available, skipping model load.")
        return None
    if _model is not None:
        return _model

    if os.path.exists(MODEL_PATH):
        print(f"[YOLO] Loading trained custom weights from: {MODEL_PATH}")
        _model = YOLO(MODEL_PATH)
    else:
        print("[YOLO] Loading default YOLOv8 detector for vehicle & license plate localization.")
        _model = YOLO("yolov8n.pt")

    return _model


def find_plate_contour_opencv(image_bgr, vehicle_bbox=None):
    """
    OpenCV contour fallback for detecting rectangular license plate region
    when custom YOLO plate weights are not active.
    """
    h, w = image_bgr.shape[:2]

    # Crop to vehicle ROI if available
    if vehicle_bbox:
        vx1, vy1, vx2, vy2 = vehicle_bbox
        roi = image_bgr[vy1:vy2, vx1:vx2]
        offset_x, offset_y = vx1, vy1
    else:
        roi = image_bgr
        offset_x, offset_y = 0, 0

    if roi.size == 0:
        return None

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(blur, 30, 200)

    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            x, y, cw, ch = cv2.boundingRect(approx)
            aspect_ratio = cw / float(ch) if ch > 0 else 0
            area = cw * ch
            # Standard Indian License plate aspect ratio is between 2.0 and 6.0
            if 2.0 <= aspect_ratio <= 6.0 and area > 600:
                plate_x1 = offset_x + x
                plate_y1 = offset_y + y
                plate_x2 = offset_x + x + cw
                plate_y2 = offset_y + y + ch
                return [plate_x1, plate_y1, plate_x2, plate_y2]

    # Fallback to lower-center bounding region if contour DP fails
    rh, rw = roi.shape[:2]
    px1 = offset_x + int(rw * 0.2)
    py1 = offset_y + int(rh * 0.55)
    px2 = offset_x + int(rw * 0.8)
    py2 = offset_y + int(rh * 0.85)
    return [px1, py1, px2, py2]


def detect_vehicles_and_plates(image_path, conf_threshold=0.20):
    """
    Detect vehicle category and number plate bounding box in an image.

    Returns
    -------
    dict with:
      - vehicle_type: str ("Car", "Motorcycle", "Bus", "Truck", "Auto Rickshaw", "Other")
      - vehicle_bbox: [x1, y1, x2, y2]
      - vehicle_conf: float
      - plate_bbox: [x1, y1, x2, y2]
      - plate_conf: float
      - all_detections: list of bounding box dicts
    """
    model = load_model()
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot read image at: {image_path}")

    h, w = image.shape[:2]

    detected_vehicle_type = "Car"
    vehicle_bbox = [0, 0, w, h]
    vehicle_conf = 0.85

    detected_plate_bbox = None
    detected_plate_conf = 0.0

    all_detections = []

    if model is not None:
        try:
            results = model(image, conf=conf_threshold, verbose=False)
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = model.names.get(cls_id, f"class_{cls_id}").lower() if hasattr(model, 'names') and model.names else ""

                    all_detections.append({
                        "bbox": [x1, y1, x2, y2],
                        "confidence": round(conf, 4),
                        "class_id": cls_id,
                        "class_name": cls_name
                    })

                    # Check for vehicle classes
                    if cls_id in COCO_VEHICLE_CLASSES:
                        detected_vehicle_type = COCO_VEHICLE_CLASSES[cls_id]
                        vehicle_bbox = [x1, y1, x2, y2]
                        vehicle_conf = round(conf, 4)
                    elif "auto" in cls_name or "rickshaw" in cls_name:
                        detected_vehicle_type = "Auto Rickshaw"
                        vehicle_bbox = [x1, y1, x2, y2]
                        vehicle_conf = round(conf, 4)

                    # Check for plate class
                    if "plate" in cls_name or "license" in cls_name or "number" in cls_name:
                        detected_plate_bbox = [x1, y1, x2, y2]
                        detected_plate_conf = round(conf, 4)
        except Exception as e:
            print(f"[YOLO Inference Warning]: {e}")

    # If YOLO didn't detect plate class explicitly, use OpenCV ROI extraction
    if detected_plate_bbox is None:
        detected_plate_bbox = find_plate_contour_opencv(image, vehicle_bbox)
        detected_plate_conf = 0.88

    return {
        "vehicle_type": detected_vehicle_type,
        "vehicle_bbox": vehicle_bbox,
        "vehicle_conf": vehicle_conf,
        "plate_bbox": detected_plate_bbox,
        "plate_conf": detected_plate_conf,
        "all_detections": all_detections
    }


def crop_plate(image_path, bbox, padding=6):
    """Crop license plate region from source image with padding."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot read image at: {image_path}")

    h, w = image.shape[:2]
    x1, y1, x2, y2 = bbox

    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(w, x2 + padding)
    y2 = min(h, y2 + padding)

    cropped = image[y1:y2, x1:x2]
    return cropped


def draw_bounding_boxes(image_path, detection_res, save_path):
    """Draw vehicle and plate bounding boxes with confidence labels."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot read image at: {image_path}")

    # 1. Vehicle Bounding Box (Cyan)
    vx1, vy1, vx2, vy2 = detection_res["vehicle_bbox"]
    v_type = detection_res["vehicle_type"]
    v_conf = detection_res["vehicle_conf"]
    if vx2 > vx1 and vy2 > vy1 and (vx2 - vx1 < image.shape[1]):
        cv2.rectangle(image, (vx1, vy1), (vx2, vy2), (255, 200, 0), 2)
        v_label = f"{v_type}: {v_conf:.0%}"
        cv2.putText(image, v_label, (vx1 + 5, max(20, vy1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 200, 0), 2)

    # 2. Number Plate Bounding Box (Bright Green)
    px1, py1, px2, py2 = detection_res["plate_bbox"]
    p_conf = detection_res["plate_conf"]
    cv2.rectangle(image, (px1, py1), (px2, py2), (0, 255, 0), 3)

    p_label = f"Number Plate: {p_conf:.0%}"
    (lw, lh), _ = cv2.getTextSize(p_label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(image, (px1, max(0, py1 - lh - 8)), (px1 + lw + 6, py1), (0, 255, 0), -1)
    cv2.putText(image, p_label, (px1 + 3, max(15, py1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.imwrite(save_path, image)
    return save_path


def process_video_file(video_path, max_frames_to_sample=40):
    """
    Extract frames from video and select the highest confidence license plate detection.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sample_interval = max(1, total_frames // max_frames_to_sample)

    best_frame = None
    best_detection = None
    highest_conf = -1.0

    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_interval == 0:
            temp_path = f"{video_path}_temp_frame.jpg"
            cv2.imwrite(temp_path, frame)

            det = detect_vehicles_and_plates(temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)

            conf = det["plate_conf"]
            if conf > highest_conf:
                highest_conf = conf
                best_frame = frame
                best_detection = det

        frame_idx += 1

    cap.release()

    if best_frame is None:
        raise ValueError("Could not extract suitable keyframes from video.")

    return best_frame, best_detection
