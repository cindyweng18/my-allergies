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

def extract_allergens(text):
    lines = text.splitlines()
    allergens = set()

    for line in lines:
        clean_line = line.strip().lower()
        if len(clean_line) < 3 or any(char.isdigit() for char in clean_line):
            continue

        match = re.match(r'(allergy|tested|positive|negative)?[:\-\s]*([a-zA-Z\s]{3,})', clean_line)
        if match:
            possible = match.group(2).strip()
            if len(possible.split()) <= 3: 
                allergens.add(possible)

    return list(allergens)
