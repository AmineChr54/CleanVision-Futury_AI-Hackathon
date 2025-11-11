import json
from PIL import Image
import numpy as np
from src import client
from src.maskrcnn_detector import MaskRCNNDetector
from src.segmenter import SAM_Segmenter
from src import config

def get_deep_eval_prompt(class_name):
    """
    Generates a prompt for the Gemini model to evaluate a specific segmented object.
    """
    return f"""
    You are an AI quality assurance inspector. You will be given an image of a segmented object: a '{class_name}'.
    
    Your task is to:
    1. Evaluate the cleanliness of this specific object on a scale of 0 to 10.
    2. Provide a brief justification for your score.
    3. Suggest a specific, actionable to-do item if the object is not perfectly clean (score < 10).

    Your output must be a JSON object with the following keys:
    - "object_name": The name of the object being evaluated.
    - "score": The cleanliness score (0-10).
    - "justification": A brief explanation for the score.
    - "todo_item": A to-do item (string), or null if the score is 10.
    """

def crop_and_save_segment(image_np, mask, box, padding=20):
    """
    Crops the segmented object from the image, applies the mask, and saves it.
    """
    x_min, y_min, x_max, y_max = [int(c) for c in box]
    
    # Add padding
    x_min = max(0, x_min - padding)
    y_min = max(0, y_min - padding)
    x_max = min(image_np.shape[1], x_max + padding)
    y_max = min(image_np.shape[0], y_max + padding)

    # Crop the image and the mask
    cropped_image = image_np[y_min:y_max, x_min:x_max]
    cropped_mask = mask[y_min:y_max, x_min:x_max]
    
    # Ensure the mask is 3-dimensional for broadcasting
    cropped_mask_3d = np.expand_dims(cropped_mask, axis=-1)
    
    # Create a white background
    white_background = np.ones_like(cropped_image) * 255
    
    # Apply the mask: where the mask is True, use the cropped image, otherwise use the white background
    segmented_object_np = np.where(cropped_mask_3d, cropped_image, white_background).astype(np.uint8)
    
    # Save the cropped and segmented object to a temporary file
    temp_path = config.SEGMENTED_OBJECT_PATH
    Image.fromarray(segmented_object_np).save(temp_path)
    
    return temp_path

def perform_deep_evaluation(gemini_model, detector, image_path):
    """
    Performs a deep evaluation of an image by detecting, segmenting, and evaluating each object.
    """
    # 1. Detect objects
    image = Image.open(image_path).convert("RGB")
    image_np = np.array(image)
    
    instances = detector.run_detection(image_np)
    
    # 2. Initialize models
    sam = SAM_Segmenter()
    
    overall_scores = []
    todo_list = []

    # 3. Iterate through detected objects
    for i in range(len(instances)):
        box = instances.pred_boxes.tensor[i].numpy()
        class_id = instances.pred_classes[i].item()
        class_name = detector.metadata.get("thing_classes", [])[class_id]
        
        # 4. Segment the object
        mask = sam.segment_with_box(image_np, box)
        
        # 5. Crop and save the segmented object
        segmented_path = crop_and_save_segment(image_np, mask, box)
        
        # 6. Upload to Gemini and evaluate
        uploaded_file = client.upload_file(segmented_path)
        if not uploaded_file:
            print(f"Skipping evaluation for {class_name} due to upload failure.")
            continue
            
        prompt = get_deep_eval_prompt(class_name)
        response = gemini_model.generate_content([prompt, uploaded_file])
        
        try:
            eval_result = json.loads(response.text)
            score = eval_result.get("score")
            todo = eval_result.get("todo_item")
            
            if score is not None:
                overall_scores.append(score)
            if todo:
                todo_list.append(f"{class_name.capitalize()}: {todo}")
                
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Could not parse deep evaluation for {class_name}: {e}")
            
        # Clean up the uploaded file
        client.delete_file(uploaded_file.name)

    # 7. Calculate overall score
    overall_score = np.mean(overall_scores) if overall_scores else 0
    
    return round(overall_score, 2), todo_list

if __name__ == '__main__':
    # Example usage
    
    # Initialize clients and models
    client.initialize_gemini()
    gemini_model = client.get_gemini_model()
    detector = MaskRCNNDetector()
    
    # Path to an example image
    EXAMPLE_IMAGE_PATH = "path/to/your/image.jpg" # IMPORTANT: Replace with a valid image path
    
    # Run the deep evaluation
    final_score, todos = perform_deep_evaluation(gemini_model, detector, EXAMPLE_IMAGE_PATH)
    
    # Print the results
    print("\n--- Deep Dive Evaluation Complete ---")
    print(f"Overall Cleanliness Score: {final_score}/10")
    if todos:
        print("\nRecommended To-do List:")
        for item in todos:
            print(f"- {item}")
    else:
        print("\nNo to-do items. Everything looks great!")
    print("------------------------------------")
