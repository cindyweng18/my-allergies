import pytesseract
from PIL import Image
import os

def extract_text_from_image(image_path):
    """Extract text from an image using Tesseract OCR."""
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""
