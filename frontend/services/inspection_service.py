"""Image inspection service (placeholder logic).

Abstracts the cleanliness inspection logic away from UI code so the
implementation can evolve (e.g., calling a ML model, REST API, or on-device
inference) without changing screen code.
"""
from __future__ import annotations
from pathlib import Path
import json


def inspect_image(image_path: str | Path) -> dict:
    """Return a structured inspection result for the given image.

    Parameters
    ----------
    image_path: str | Path
        Path to the image file.

    Returns
    -------
    dict
        Dictionary with keys: cleanliness_score (int), issues (list[str]), image (str)

    Notes
    -----
    Currently returns a mocked response. Replace with real model inference.
    Example extension:
        - Load a trained classifier
        - Preprocess image
        - Run prediction
        - Aggregate anomalies / cleanliness metrics
    """
    image_path = Path(image_path)

    # Placeholder deterministic mock (could hash filename for variability)
    cleanliness_score = 85
    issues = ["Dust on surfaces"]

    return {
        "cleanliness_score": cleanliness_score,
        "issues": issues,
        "image": image_path.name,
    }


def format_result(result: dict) -> str:
    """Return pretty-formatted JSON string for display."""
    return json.dumps(result, indent=2)
