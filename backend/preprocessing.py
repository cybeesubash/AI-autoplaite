# ============================================================
# preprocessing.py  –  OpenCV Image Preprocessing Pipeline
# ============================================================

import cv2
import numpy as np


def resize_plate(img, target_width=320):
    """Resize cropped license plate image to standard width maintaining aspect ratio."""
    h, w = img.shape[:2]
    if w == 0 or h == 0:
        return img
    aspect_ratio = h / float(w)
    target_height = int(target_width * aspect_ratio)
    return cv2.resize(img, (target_width, target_height), interpolation=cv2.INTER_CUBIC)


def convert_to_grayscale(img):
    """Convert BGR image to single channel grayscale."""
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def remove_noise(gray_img):
    """Apply bilateral filtering to smooth noise while maintaining sharp character edges."""
    return cv2.bilateralFilter(gray_img, d=11, sigmaColor=17, sigmaSpace=17)


def enhance_contrast(gray_img):
    """Apply Contrast Limited Adaptive Histogram Equalization (CLAHE)."""
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    return clahe.apply(gray_img)


def adaptive_thresholding(gray_img):
    """Apply adaptive Gaussian thresholding combined with Otsu thresholding."""
    adaptive = cv2.adaptiveThreshold(
        gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    _, otsu = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Combine adaptive and Otsu for enhanced character contrast
    combined = cv2.bitwise_and(adaptive, otsu)
    return combined


def sharpen_image(gray_img):
    """Apply unsharp mask kernel to sharpen text character outlines."""
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(gray_img, -1, kernel)


def preprocess_plate_pipeline(cropped_bgr_img):
    """
    Execute full OpenCV preprocessing pipeline on cropped plate region:
    1. Resize
    2. Grayscale
    3. Bilateral Noise Reduction
    4. CLAHE Contrast Enhancement
    5. Sharpening
    6. Adaptive Thresholding

    Returns
    -------
    numpy.ndarray  – High contrast binary/preprocessed plate image for OCR
    """
    if cropped_bgr_img is None or cropped_bgr_img.size == 0:
        return None

    resized = resize_plate(cropped_bgr_img, target_width=360)
    gray = convert_to_grayscale(resized)
    denoised = remove_noise(gray)
    enhanced = enhance_contrast(denoised)
    sharpened = sharpen_image(enhanced)
    binary = adaptive_thresholding(sharpened)

    return binary
