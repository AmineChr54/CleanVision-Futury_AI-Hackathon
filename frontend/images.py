import os
from typing import List, Optional

# Simple asset resolver. Looks for images in likely folders and supports a few logical names.


def _candidate_names(name: str) -> List[str]:
    mapping = {
        "logo_title": ["logo_title.png", "logo.png", "brand.png"],
        "camera": ["camera.png", "camera_icon.png", "photo.png"],
        "camera_inverted": ["camera_inverted.png"],
        "robot": ["robot.png", "assistant_robot.png"],
    }
    # If name contains an extension already, try it directly
    if any(name.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg")):
        return [name]
    return mapping.get(name, [f"{name}.png", f"{name}.jpg"])  # generic fallback


def _search(paths, names: List[str]) -> Optional[str]:
    for base in paths:
        for nm in names:
            p = os.path.join(base, nm)
            if os.path.exists(p):
                return p
    return None


def get_image_path(name: str) -> Optional[str]:
    """Resolve logical image name to an existing file path or None.

    Search order:
      1. <project_root>/images
      2. <this_dir>/images
      3. <project_root>/UI/images (for safety if structure changes)
    """
    here = os.path.dirname(__file__)
    root = here  # project root is this directory for this app layout
    candidates = _candidate_names(name)
    search_dirs = [
        os.path.join(root, "images"),
        os.path.join(here, "images"),
        os.path.join(root, "UI", "images"),
    ]
    return _search(search_dirs, candidates)
