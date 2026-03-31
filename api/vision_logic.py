import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Enable JSON mode for the model
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    generation_config=genai.types.GenerationConfig(
        response_mime_type="application/json"
    )
)

async def analyze_image(file):
    """
    Analyzes an image of a clothing item using Gemini and returns a structured
    JSON description.
    """
    image_bytes = await file.read()

    prompt = (
        "Look at this clothing item and describe it. "
        "Return a JSON object with the following keys: "
        "type, color, style, and material."
    )

    try:
        response = await model.generate_content_async([prompt, image_bytes])
        # The model is now configured to return JSON directly
        return json.loads(response.text)
    except Exception as e:
        print(f"Error analyzing image with Gemini: {e}")
        # In a real app, you'd have more robust logging and error handling
        return None
