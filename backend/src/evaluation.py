import json
from PIL import Image
from src import client

def get_evaluation_prompt():
    """
    Returns the prompt for the Gemini model to evaluate the cleanliness of an image.
    """
    return """
    You are an AI quality assurance inspector for a cleaning service. Your task is to evaluate the cleanliness of the given image.
    
    Evaluate the cleanliness of the image on a scale of 0 to 10, where 0 is extremely dirty and 10 is perfectly clean.
    
    Provide a brief justification for your score.
    
    Your output should be a JSON object with the following keys:
    - "overall_rating": A descriptive rating (e.g., "Excellent", "Good", "Fair", "Poor").
    - "score": The cleanliness score (0-10).
    - "justification": A brief explanation for the score.
    """

def perform_evaluation(model, image_path):
    """
    Performs a cleanliness evaluation on a single image using the Gemini model.
    
    Args:
        model: The Gemini model instance.
        image_path (str): The path to the image file.
        
    Returns:
        dict: A dictionary containing the evaluation report (rating, score, justification).
    """
    prompt = get_evaluation_prompt()
    
    # Upload the image
    uploaded_image = client.upload_file(image_path)
    if not uploaded_image:
        return {"error": "Failed to upload image."}
        
    # Generate content with the image and prompt
    response = model.generate_content([prompt, uploaded_image])
    
    # Clean up the uploaded file
    client.delete_file(uploaded_image.name)
    
    try:
        # Assuming the response is a JSON string
        report = json.loads(response.text)
        return report
    except (json.JSONDecodeError, KeyError) as e:
        return {"error": f"Failed to parse response from Gemini: {e}", "raw_response": response.text}

if __name__ == '__main__':
    # This is an example of how to use the perform_evaluation function.
    
    # Initialize Gemini
    client.initialize_gemini()
    
    # Get the model
    gemini_model = get_gemini_model('gemini-2.5-pro') # Use a model that supports image and text
    
    # Path to an example image
    example_image_path = "path/to/your/image.jpg" # IMPORTANT: Replace with a valid image path
    
    # Perform the evaluation
    evaluation_report = perform_evaluation(gemini_model, example_image_path)
    
    # Print the report
    if "error" in evaluation_report:
        print(f"An error occurred: {evaluation_report['error']}")
        if "raw_response" in evaluation_report:
            print(f"Raw response: {evaluation_report['raw_response']}")
    else:
        print("--- Cleanliness Evaluation Report ---")
        print(f"Overall Rating: {evaluation_report.get('overall_rating', 'N/A')}")
        print(f"Score: {evaluation_report.get('score', 'N/A')}/10")
        print(f"Justification: {evaluation_report.get('justification', 'N/A')}")
        print("------------------------------------")