import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_content(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            return ""