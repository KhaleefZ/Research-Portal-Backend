from google import genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def check_supported_models():
    if not api_key:
        print("Error: Please set your GEMINI_API_KEY in the .env file.")
        return

    # Initialize the modern Client
    client = genai.Client(api_key=api_key)

    print(f"{'Model ID':<35} | {'Supported Actions'}")
    print("-" * 75)

    try:
        # List all available models
        for m in client.models.list():
            # Check for 'generateContent' action
            # The attribute is now 'supported_actions'
            if "generateContent" in m.supported_actions:
                print(f"{m.name:<35} | generateContent")
                
    except Exception as e:
        print(f"Failed to retrieve models: {e}")

if __name__ == "__main__":
    check_supported_models()