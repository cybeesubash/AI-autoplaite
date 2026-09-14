# Vehicle Number Plate Dataset Structure

This folder contains the annotated dataset for training the YOLO model for automatic license plate detection.

## Directory Structure:
```
dataset/
│
├── data.yaml            # Dataset YAML configuration (classes, paths)
│
├── images/              # Raw vehicle photos
│   ├── train/           # Training images (e.g., .jpg, .png)
│   ├── val/             # Validation images
│   └── test/            # Test images
│
└── labels/              # YOLO format annotations (.txt)
    ├── train/           # Normalized [class x_center y_center width height]
    ├── val/
    └── test/
```

## Annotation Format (YOLO):
Each `.txt` label file corresponds to an image with the same name and contains bounding boxes:
```
<class-index> <x_center> <y_center> <width> <height>
```
Example (`vehicle_01.txt`):
```
0 0.492188 0.651563 0.221875 0.084375
```
Where `0` corresponds to `number_plate`.
