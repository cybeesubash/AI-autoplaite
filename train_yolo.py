# ============================================================
# train_yolo.py  –  Train YOLO on Vehicle Number Plate Dataset
# ============================================================

import os
import shutil
from ultralytics import YOLO

def train_number_plate_detector():
    """
    Train a YOLOv8 object detection model on the vehicle number plate dataset.
    After training, automatically copy the best weights to backend/model/best.pt.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_yaml = os.path.join(current_dir, "dataset", "data.yaml")
    dest_model_dir = os.path.join(current_dir, "backend", "model")
    dest_weights = os.path.join(dest_model_dir, "best.pt")

    os.makedirs(dest_model_dir, exist_ok=True)

    print("=" * 65)
    print("      VEHICLE NUMBER PLATE YOLOv8 TRAINING PIPELINE")
    print("=" * 65)
    print(f"Dataset config: {data_yaml}")

    if not os.path.exists(data_yaml):
        print(f"[ERROR] Dataset configuration file not found at: {data_yaml}")
        return

    # Load base pretrained model (YOLOv8 Nano for fast training & deployment)
    print("\n[1/3] Initializing base YOLOv8 model (yolov8n.pt)...")
    model = YOLO("yolov8n.pt")

    # Train model
    print("\n[2/3] Starting model fine-tuning...")
    # Parameters can be customized based on your GPU and dataset size
    epochs = 50
    imgsz = 640
    batch = 16

    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name="number_plate_yolo",
        save=True,
        verbose=True
    )

    print("\n[3/3] Training finished. Exporting best weights...")
    # Ultralytics saves runs in runs/detect/number_plate_yolo/weights/best.pt
    run_best_weights = os.path.join(current_dir, "runs", "detect", "number_plate_yolo", "weights", "best.pt")
    
    if os.path.exists(run_best_weights):
        shutil.copy(run_best_weights, dest_weights)
        print(f"[SUCCESS] Copied best trained weights to: {dest_weights}")
    else:
        print(f"[INFO] Training completed. Check your runs directory for weights.")

    print("\n" + "=" * 65)
    print("You can now start the web application by running:")
    print("    python backend/app.py")
    print("=" * 65)

if __name__ == "__main__":
    train_number_plate_detector()
