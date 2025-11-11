
import os
import json
import pandas as pd
from tqdm import tqdm
from src.client import Gemini

def get_bootstrap_prompt():
    """
    Returns the prompt for the Gemini model to bootstrap the dataset.
    """
    return """
    You are an AI quality assurance inspector for a cleaning service. Your task is to evaluate the cleanliness of a given image.
    
    First, identify the primary cleaning task depicted in the image from the following categories:
    - Clean / clear the table surface
    - Clean / clear the floor
    - Clean / clear the sink
    - Clean / clear the toilet
    - Clean / clear the shower / bathtub
    - Clean / clear the mirror
    - Clean / clear the window
    - Clean / clear the stove / oven
    - Clean / clear the refrigerator
    - Clean / clear the microwave
    - Clean / clear the cabinet / drawer
    - Clean / clear the wall
    - Clean / clear the ceiling
    - Clean / clear the fan
    - Clean / clear the light fixture
    - Clean / clear the trash can
    - Clean / clear the bed
    - Clean / clear the sofa / chair
    - Clean / clear the carpet / rug
    - Clean / clear the curtain / blind
    - Clean / clear the door
    - Clean / clear the handle / knob
    - Clean / clear the switch / outlet
    - Clean / clear the remote control
    - Clean / clear the keyboard
    - Clean / clear the mouse
    - Clean / clear the screen / monitor
    - Clean / clear the phone / tablet
    - Clean / clear the book / magazine
    - Clean / clear the toy
    - Clean / clear the plant
    - Clean / clear the pet area
    - Clean / clear the car interior
    - Clean / clear the car exterior
    - Other (specify)

    Then, evaluate the cleanliness of the image based on a scale of 0 to 2:
    - **0: Dirty** - Significant dirt, dust, stains, or clutter. Requires thorough cleaning.
    - **1: Somewhat Clean** - Minor imperfections, some dust, or slight disorganization. Could use a light touch-up.
    - **2: Clean** - Spotless, organized, and free of any visible dirt or clutter.

    Provide a brief justification for your score.

    Your output should be a JSON object with the following keys:
    - "task": The identified cleaning task.
    - "score": The cleanliness score (0, 1, or 2).
    - "justification": A brief explanation for the score.
    """

def process_directories(model, input_dirs, output_csv_path="data/generated_dataset.csv"):
    """
    Processes images in the specified directories, sends them to the Gemini model,
    and saves the results to a CSV file.
    """
    results = []
    prompt = get_bootstrap_prompt()

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    for input_dir in input_dirs:
        print(f"Processing images in: {input_dir}")
        for root, _, files in os.walk(input_dir):
            for file in tqdm(files, desc=f"Processing {os.path.basename(root)}"):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(root, file)
                    try:
                        # Upload image to Gemini
                        uploaded_file = model.upload_file(image_path)
                        
                        # Generate content with image and prompt
                        response = model.generate_content([prompt, uploaded_file])
                        
                        # Parse the JSON response
                        response_text = response.text.strip()
                        # Clean the response text to ensure it's valid JSON
                        if response_text.startswith("```json"):
                            response_text = response_text[len("```json"):].strip()
                        if response_text.endswith("```"):
                            response_text = response_text[:-len("```")].strip()

                        data = json.loads(response_text)
                        
                        results.append({
                            "image_path": image_path,
                            "task": data.get("task"),
                            "score": data.get("score"),
                            "justification": data.get("justification")
                        })
                        
                        # Delete the uploaded file to free up space
                        model.delete_file(uploaded_file.name)

                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON for {image_path}. Response: {response.text}")
                        results.append({
                            "image_path": image_path,
                            "task": "Error",
                            "score": -1,
                            "justification": f"JSON Decode Error: {response.text}"
                        })
                    except Exception as e:
                        print(f"Error processing {image_path}: {e}")
                        results.append({
                            "image_path": image_path,
                            "task": "Error",
                            "score": -1,
                            "justification": str(e)
                        })

    df = pd.DataFrame(results)
    df.to_csv(output_csv_path, index=False)
    print(f"Dataset generated and saved to {output_csv_path}")

def main():
    # Initialize Gemini client
    gemini_client = Gemini(model="gemini-pro-vision")

    # Define input directories (adjust as needed)
    input_directories = ["data/train", "data/val"]

    # Process images and generate dataset
    process_directories(gemini_client, input_directories)

if __name__ == "__main__":
    main()
