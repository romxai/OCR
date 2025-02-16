# ocr.py
import cv2
import numpy as np
import pytesseract

# Set path to Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def preprocess_image(image):
    """Convert an image to grayscale."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    return gray

def extract_text_from_image(image):
    """Extract text from an image using OCR."""
    processed_img = preprocess_image(image)
    text = pytesseract.image_to_string(processed_img)
    return text
