
import os
import torch
import numpy as np
from segment_anything import sam_model_registry, SamPredictor
import requests
from tqdm import tqdm

def download_sam_checkpoint(model_type="vit_h", save_path="models"):
    """
    Downloads the SAM checkpoint if it doesn't already exist.
    
    Args:
        model_type (str): The type of SAM model (e.g., "vit_h", "vit_l", "vit_b").
        save_path (str): The directory to save the checkpoint in.
        
    Returns:
        str: The path to the downloaded checkpoint.
    """
    checkpoints = {
        "vit_h": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        "vit_l": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
        "vit_b": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    }
    
    if model_type not in checkpoints:
        raise ValueError(f"Invalid model type. Choose from {list(checkpoints.keys())}")
        
    url = checkpoints[model_type]
    filename = os.path.basename(url)
    checkpoint_path = os.path.join(save_path, filename)
    
    if not os.path.exists(checkpoint_path):
        print(f"Downloading SAM checkpoint for {model_type}...")
        os.makedirs(save_path, exist_ok=True)
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(checkpoint_path, 'wb') as f, tqdm(
                desc=filename,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    size = f.write(chunk)
                    bar.update(size)
                    
            print(f"Checkpoint downloaded to {checkpoint_path}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading checkpoint: {e}")
            return None
            
    return checkpoint_path

class SAM_Segmenter:
    """
    A class to handle object segmentation using the Segment Anything Model (SAM).
    """
    def __init__(self, model_type="vit_h", checkpoint_path=None):
        """
        Initializes the SAM model and predictor.
        
        Args:
            model_type (str): The type of SAM model to use.
            checkpoint_path (str, optional): Path to the SAM checkpoint. If None, it will be downloaded.
        """
        if checkpoint_path is None:
            checkpoint_path = download_sam_checkpoint(model_type)
            if checkpoint_path is None:
                raise RuntimeError("Failed to download or find SAM checkpoint.")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"SAM using device: {self.device}")
        
        # Load the SAM model
        self.sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
        self.sam.to(device=self.device)
        
        # Create the predictor
        self.predictor = SamPredictor(self.sam)

    def segment_with_box(self, image_np, box):
        """
        Performs segmentation on an image given a bounding box.
        
        Args:
            image_np: The input image as a NumPy array (H, W, C) in RGB format.
            box: A bounding box in the format [x_min, y_min, x_max, y_max].
            
        Returns:
            A boolean mask of the segmented object.
        """
        # Set the image for the predictor
        self.predictor.set_image(image_np)
        
        # Define the input box for the prompt
        input_box = np.array(box)
        
        # Predict the mask
        masks, _, _ = self.predictor.predict(
            point_coords=None,
            point_labels=None,
            box=input_box[None, :],
            multimask_output=False,
        )
        
        return masks[0]

if __name__ == '__main__':
    # This is an example of how to use the SAM_Segmenter class.
    
    from PIL import Image
    import matplotlib.pyplot as plt

    # --- Configuration ---
    MODEL_TYPE = "vit_h" # or "vit_l", "vit_b"
    EXAMPLE_IMAGE_PATH = "path/to/your/image.jpg" # IMPORTANT: Replace with a valid image path
    # Example bounding box (x_min, y_min, x_max, y_max) - you would get this from an object detector
    EXAMPLE_BOX = [100, 100, 300, 300] # IMPORTANT: Replace with a valid bounding box for your image

    # --- Main Execution ---
    
    # 1. Initialize the segmenter
    try:
        segmenter = SAM_Segmenter(model_type=MODEL_TYPE)
    except (RuntimeError, ValueError) as e:
        print(f"Error initializing segmenter: {e}")
        exit()

    # 2. Load the image
    try:
        image = Image.open(EXAMPLE_IMAGE_PATH).convert("RGB")
        image_np = np.array(image)
    except FileNotFoundError:
        print(f"Error: Image not found at {EXAMPLE_IMAGE_PATH}")
        exit()

    # 3. Perform segmentation
    print(f"Running segmentation on box: {EXAMPLE_BOX}")
    mask = segmenter.segment_with_box(image_np, EXAMPLE_BOX)

    # 4. Visualize the result
    plt.figure(figsize=(10, 10))
    plt.imshow(image_np)
    
    # Show the mask
    mask_color = np.array([30/255, 144/255, 255/255, 0.6]) # Blue with transparency
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * mask_color.reshape(1, 1, -1)
    plt.imshow(mask_image)
    
    # Show the bounding box
    x0, y0, x1, y1 = EXAMPLE_BOX
    plt.gca().add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, edgecolor='green', facecolor=(0,0,0,0), lw=2))
    
    plt.axis('off')
    plt.title("SAM Segmentation Result")
    plt.show()
