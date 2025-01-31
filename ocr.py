import os
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path

# Set path to Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Function to process images for OCR
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # # Adaptive Thresholding
    # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # # Denoising
    # denoised = cv2.fastNlMeansDenoising(thresh, None, 30, 7, 21)

    # # Deskewing
    # coords = cv2.findNonZero(thresh)
    # angle = cv2.minAreaRect(coords)[-1]
    # if angle < -45:
    #     angle = -(90 + angle)
    # else:
    #     angle = -angle
    # (h, w) = gray.shape[:2]
    # center = (w // 2, h // 2)
    # M = cv2.getRotationMatrix2D(center, angle, 1.0)
    # deskewed = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # # Sharpening
    # kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    # sharpened = cv2.filter2D(denoised, -1, kernel)

    return gray

# Function to extract text from an image
def extract_text_from_image(image_path):
    processed_img = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_img)
    return text

# Main function to process PDF
def pdf_to_text(pdf_path, output_text_file="output.txt"):
    poppler_path = r"C:/Program Files/poppler-24.08.0/Library/bin"  # Adjust based on your Poppler path
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
    
    # Ensure output directory exists
    output_dir = "pdf_pages"
    os.makedirs(output_dir, exist_ok=True)

    extracted_text = ""

    # Process each page
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"page_{i+1}.jpg")
        image.save(image_path, "JPEG")

        print(f"Processing Page {i+1}...")

        # Extract text from image
        page_text = extract_text_from_image(image_path)
        extracted_text += f"\n\n--- Page {i+1} ---\n\n{page_text}"

    # Save extracted text to a file
    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    print(f"Text extracted and saved to {output_text_file}")

# Example usage
pdf_to_text("Unit_1.pdf")  # Replace with your PDF filename
