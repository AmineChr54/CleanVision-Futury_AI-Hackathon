
import os

# Temporary file paths
TMP_DIR = "/tmp"
UPLOADED_IMAGE_PATH = os.path.join(TMP_DIR, "uploaded_image.jpg")
ANNOTATED_IMAGE_PATH = os.path.join(TMP_DIR, "uploaded_with_boxes.jpg")
SEGMENTED_OBJECT_PATH = os.path.join(TMP_DIR, "segmented_object.jpg")

# Model names
GEMINI_MODEL = "gemini-pro-vision"

# Data paths
DATA_DIR = "data"
VAL_DIR = os.path.join(DATA_DIR, "val")
GENERATED_DATASET_PATH = os.path.join(DATA_DIR, "generated_dataset.csv")

# Validation report paths
VALIDATION_BENCHMARK_REPORT_PATH = "validation_benchmark_report.json"
ACCURACY_TEST_REPORT_PATH = "accuracy_test_report.json"
