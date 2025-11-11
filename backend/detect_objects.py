import argparse
from ultralytics import YOLO
import cv2
import os

def detect_objects_in_image(image_path, model_path='yolov8n.pt', output_dir='runs/detect'):
    """
    Detects objects in an image using a YOLOv8 model and saves the annotated image.

    Args:
        image_path (str): Path to the input image.
        model_path (str): Path to the YOLOv8 model weights.
        output_dir (str): Directory to save the annotated image.
    """
    # Load a pretrained YOLOv8n model
    model = YOLO(model_path)

    # Run inference on the image
    results = model(image_path)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process results
    for r in results:
        im_bgr = r.plot()  # plot a BGR numpy array of predictions
        
        # Save the annotated image
        output_image_path = os.path.join(output_dir, os.path.basename(image_path))
        cv2.imwrite(output_image_path, im_bgr)
        print(f"Annotated image saved to {output_image_path}")

        # Print detection details
        print(f"\nDetections for {os.path.basename(image_path)}:")
        for box in r.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            confidence = float(box.conf[0])
            xyxy = box.xyxy[0].tolist() # Bounding box in [x1, y1, x2, y2] format

            print(f"  Object: {class_name}, Confidence: {confidence:.2f}, Bounding Box: {xyxy}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Detect objects in an image using YOLOv8.")
    parser.add_argument("image_path", type=str, help="Path to the input image.")
    parser.add_argument("--model", type=str, default='yolov8n.pt', 
                        help="Path to the YOLOv8 model weights (e.g., yolov8n.pt).")
    parser.add_argument("--output_dir", type=str, default='runs/detect', 
                        help="Directory to save the annotated image.")
    
    args = parser.parse_args()

    detect_objects_in_image(args.image_path, args.model, args.output_dir)
