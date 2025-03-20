import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

def extract_allergens(text):
    """Send extracted text to Gemini AI and retrieve allergens."""
    prompt = f"Extract all allergens from the following text: {text}. Return only the allergens as a list."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.split("\n") 
    except Exception as e:
        print("Error processing text with Gemini:", e)
        return []

# def extract_text_from_image(image_path):
#     """Extracts text from an image using Google Gemini AI."""
#     with open(image_path, "rb") as img_file:
#         image_data = img_file.read()

#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content(
#         contents=[{"mime_type": "image/jpeg", "data": image_data}]
#     )

#     return response.text.strip() if response.text else "No text found"