# CleanVision

CleanVision is an AI-powered cleanliness inspection tool developed during the Futury_AI Hackathon with WISAG. It leverages computer vision and generative AI to assess the cleanliness of a space from an image, providing detailed evaluations and actionable insights.

## Features

- **Quick Evaluation:** Get an immediate cleanliness score and a brief justification for an uploaded image.
- **Deep Dive Evaluation:** Receive a comprehensive cleanliness report, including an overall score and a prioritized to-do list for specific detected objects that require attention.
- **Object Detection (Mask R-CNN):** Utilizes a Mask R-CNN model to accurately identify and locate various objects within an image.
- **Object Segmentation (SAM):** Employs the Segment Anything Model (SAM) to precisely segment detected objects, allowing for granular analysis.
- **Validation & Accuracy Testing:** Tools to benchmark the model's performance against a validation set and compare predictions with ground truth data.

## Getting Started

Follow these instructions to set up and run the CleanVision backend application.

### Prerequisites

- Python 3.10+
- `pip` for package installation
- A Google Gemini API Key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yuanfan-sun/CleanVision-Futury_AI-Hackathon.git
    cd CleanVision-Futury_AI-Hackathon
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install backend dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Set up your Gemini API Key:**
    - Obtain a Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    - Create a `.env` file in the root of the project directory (e.g., `/Users/yuanfansun/PycharmProjects/CleanVision-Futury_AI-Hackathon/.env`).
    - Add your Gemini API key to the `.env` file:
      ```
      GEMINI_API_KEY="YOUR_API_KEY"
      ```
      Replace `"YOUR_API_KEY"` with your actual API key.

### Project Structure

```
.
├── backend/
│   ├── app.py                  # Main Gradio application for the backend
│   ├── requirements.txt        # Python dependencies for the backend
│   ├── data/                   # Data related to models and datasets
│   │   ├── generated_dataset.csv # Generated dataset for evaluation
│   │   └── processed/          # Processed image data (train/val splits)
│   │       ├── train/
│   │       └── val/
│   └── src/                    # Core backend logic and utilities
│       ├── client.py           # Gemini API client functions
│       ├── config.py           # Configuration settings
│       ├── deep_evaluation.py  # Logic for deep dive evaluations
│       ├── dummy_data_generator.py # Script to generate dummy data
│       ├── evaluation.py       # Logic for quick evaluations
│       ├── maskrcnn_detector.py # Mask R-CNN object detection module
│       └── segmenter.py        # SAM (Segment Anything Model) segmentation module
├── frontend/                   # Frontend application (e.g., Kivy app)
├── docs/                       # Project documentation
└── README.md                   # Project overview and setup instructions
```

## Usage

To start the CleanVision backend application, navigate to the project root directory in your terminal and run:

```bash
python backend/app.py
```

The application will launch a Gradio web interface. You can access it by opening the URL displayed in your terminal (e.g., `http://127.0.0.1:7860`).