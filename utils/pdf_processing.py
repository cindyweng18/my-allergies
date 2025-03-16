import fitz
import re
import os

ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        print("Error reading PDF:", e)
    return text

# def find_allergens(text, allergens_list):
#     """Checks if any allergens from the list appear in the extracted text."""
#     found_allergens = [allergen for allergen in allergens_list if allergen.lower() in text.lower()]
#     return found_allergens
