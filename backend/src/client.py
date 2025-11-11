import os
import google.generativeai as genai
from dotenv import load_dotenv

def initialize_gemini():
    """
    Initializes the Gemini API with the API key from the .env file.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        exit()
    genai.configure(api_key=api_key)

def get_gemini_model(model_name='gemini-2.5-pro'):
    """
    Returns an initialized GenerativeModel instance.
    
    Args:
        model_name (str): The name of the Gemini model to use.
    
    Returns:
        genai.GenerativeModel: An instance of the Gemini model.
    """
    return genai.GenerativeModel(model_name)

def upload_file(file_path):
    """
    Uploads a file to the Gemini API.
    
    Args:
        file_path (str): The path to the file to upload.
        
    Returns:
        The uploaded file object, or None if an error occurs.
    """
    try:
        return genai.upload_file(path=file_path)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred during file upload: {e}")
        return None

def delete_file(file_name):
    """
    Deletes a file from the Gemini API.
    
    Args:
        file_name (str): The name of the file to delete.
    """
    try:
        genai.delete_file(name=file_name)
    except Exception as e:
        print(f"An error occurred during file deletion: {e}")