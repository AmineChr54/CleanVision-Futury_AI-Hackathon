"""Image inspection service (placeholder logic).

Abstracts the cleanliness inspection logic away from UI code so the
implementation can evolve (e.g., calling a ML model, REST API, or on-device
inference) without changing screen code.
"""
from __future__ import annotations
from pathlib import Path
import json


def inspect_image(image_path: str | Path) -> dict:
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
