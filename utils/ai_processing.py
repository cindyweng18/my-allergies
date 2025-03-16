import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

def extract_allergens(text):
    """Send extracted text to Gemini AI and retrieve allergens."""
    prompt = f"Extract all food allergens from the following text: {text}. Return only the allergens as a list."

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text.split("\n") 
    except Exception as e:
        print("Error processing text with Gemini:", e)
        return []
