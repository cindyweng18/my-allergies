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


def check_product_safety(product_name, user_allergies):
    """Uses AI to determine if a product contains allergens and returns a verdict + explanation."""
    try:
        allergies_formatted = ", ".join(user_allergies)
        prompt = f"""
        A user has allergies to: {allergies_formatted}.
        Determine if the product "{product_name}" is safe for them.

        1. First, answer either "Safe" or "Unsafe".
        2. Then, explain why in 1–2 sentences, especially if unsafe (e.g., "Contains soy").

        Format your response exactly like this:
        Verdict: <Safe or Unsafe>
        Explanation: <short explanation>
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw_output = response.text.strip()

        verdict = None
        explanation = None
        for line in raw_output.splitlines():
            if line.lower().startswith("verdict:"):
                verdict = line.split(":", 1)[1].strip()
            elif line.lower().startswith("explanation:"):
                explanation = line.split(":", 1)[1].strip()

        if verdict and explanation:
            return verdict, explanation
        else:
            return "Unknown", raw_output 

    except Exception as e:
        return "Error", f"AI request failed: {str(e)}"

# def extract_text_from_image(image_path):
#     """Extracts text from an image using Google Gemini AI."""
#     with open(image_path, "rb") as img_file:
#         image_data = img_file.read()

#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content(
#         contents=[{"mime_type": "image/jpeg", "data": image_data}]
#     )

#     return response.text.strip() if response.text else "No text found"