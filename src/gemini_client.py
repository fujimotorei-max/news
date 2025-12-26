import os
import google.generativeai as genai

def gemini_generate(prompt: str, model_name: str = "gemini-flash-latest") -> str:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(model_name)
    return model.generate_content(prompt).text
