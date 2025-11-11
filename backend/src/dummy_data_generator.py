
import os
import pandas as pd
from PIL import Image
from src import config

def create_dummy_validation_data():
    """Creates dummy data for the validation benchmark if it doesn't exist."""
    if not os.path.exists(config.VAL_DIR):
        print("Creating dummy validation data...")
        os.makedirs(os.path.join(config.VAL_DIR, '0'), exist_ok=True)
        os.makedirs(os.path.join(config.VAL_DIR, '1'), exist_ok=True)
        os.makedirs(os.path.join(config.VAL_DIR, '2'), exist_ok=True)
        Image.new('RGB', (100, 100), color = 'red').save(os.path.join(config.VAL_DIR, '0', 'dummy_clean.jpg'))
        Image.new('RGB', (100, 100), color = 'yellow').save(os.path.join(config.VAL_DIR, '1', 'dummy_mid.jpg'))
        Image.new('RGB', (100, 100), color = 'green').save(os.path.join(config.VAL_DIR, '2', 'dummy_dirty.jpg'))
        print("Dummy validation data created.")

def create_dummy_ground_truth_data():
    """Creates a dummy ground truth file for the accuracy test if it doesn't exist."""
    if not os.path.exists(config.GENERATED_DATASET_PATH):
        print("Creating dummy ground truth data...")
        dummy_data = {
            'image_path': [
                os.path.join(config.VAL_DIR, '0', 'dummy_clean.jpg'),
                os.path.join(config.VAL_DIR, '1', 'dummy_mid.jpg'),
                os.path.join(config.VAL_DIR, '2', 'dummy_dirty.jpg')
            ],
            'ground_truth_score': [9.5, 5.2, 2.8]
        }
        df_ground_truth = pd.DataFrame(dummy_data)
        df_ground_truth.to_csv(config.GENERATED_DATASET_PATH, index=False)
        print("Dummy ground truth data created.")

if __name__ == '__main__':
    create_dummy_validation_data()
    create_dummy_ground_truth_data()
