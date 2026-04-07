from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

def get_llm():
    # Check for API key in environment variables (supports both GOOGLE_API_KEY and GEMINI_API_KEY)
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        raise ValueError(
            "Google API key not found. Please set GOOGLE_API_KEY or GEMINI_API_KEY in your .env file"
        )
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        api_key=api_key
    )