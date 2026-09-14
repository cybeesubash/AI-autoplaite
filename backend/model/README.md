# YOLO Model Directory

Place your custom trained YOLO weights in this folder as `best.pt`.

## Directory Structure:
```
backend/model/
└── best.pt          <-- Place your trained model weights here
```

## How It Works:
1. **Trained Model (`best.pt`)**: When present, `detection.py` loads `best.pt` for dedicated vehicle number plate detection and localization.
2. **Fallback Mode**: If `best.pt` is not yet placed, the system automatically falls back to `yolov8n.pt` for local development and demonstration.
3. **Training**: Run `python train_yolo.py` in the root folder to train a custom YOLO model using your dataset in `dataset/`. The final weights will automatically be saved to this folder as `best.pt`.
