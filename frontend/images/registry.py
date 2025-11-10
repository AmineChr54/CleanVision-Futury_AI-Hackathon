"""Image registry to centralize asset paths and provide fallbacks.

Usage:
    from frontend.images import get_image_path
    path = get_image_path("settings")

Keys:
- settings: settings icon
- camera: camera icon
- logo_title: CleanVision logo with name for navbar title
- robot: Housekeeping robot illustration for tip card
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

# Default filenames expected in this package directory
_DEFAULT_MAP = {
    "settings": ["settings.png", "settings.jpg", "settings.webp"],
    "camera": ["camera.png", "camera.jpg", "camera.webp", "camera_icon.png"],
    "logo_title": ["CleanVision_logo_name.png", "logo_title.png", "logo.png", "CleanVision_logo_name.webp"],
    "robot": ["Housekeeping_Robot.png", "robot.png", "robot.webp"],
    # dynamic variant keys (generated when requested)
    "camera_inverted": ["camera_inverted.png"],
}

IMAGE_KEYS = tuple(_DEFAULT_MAP.keys())


def _find_first_existing(base_dir: Path, candidates: list[str]) -> Optional[Path]:
    for name in candidates:
        p = base_dir / name
        if p.exists():
            return p
    return None


def get_image_path(key: str) -> Optional[str]:
    """Return absolute path to an image for a logical key or None if not found.

    Search order:
    1) This package directory: frontend/images/
    2) Repository-level images/ directory (two levels up from this file)
    """
    # If requesting an inverted camera icon, attempt on-demand generation.
    if key == "camera_inverted":
        _ensure_inverted_variant("camera", "camera_inverted")
    files = _DEFAULT_MAP.get(key, [])
    pkg_dir = Path(__file__).parent
    # package dir
    found = _find_first_existing(pkg_dir, files)
    if found:
        return str(found)
    # project images dir (../../images relative to this file)
    project_images = (pkg_dir.parent.parent / "images").resolve()
    if project_images.exists():
        found = _find_first_existing(project_images, files)
        if found:
            return str(found)
    return None


def _ensure_inverted_variant(base_key: str, inverted_key: str) -> None:
    """Generate an inverted-color PNG for base_key into inverted_key list first filename.

    Only runs if Pillow is available AND the target file doesn't already exist.
    Alpha channel preserved; RGB inverted with ImageOps.invert.
    """
    try:
        from PIL import Image, ImageOps  # type: ignore
    except Exception:
        return  # Pillow not installed; silently skip

    pkg_dir = Path(__file__).parent
    target_candidates = _DEFAULT_MAP.get(inverted_key, [])
    if not target_candidates:
        return
    target_file = pkg_dir / target_candidates[0]
    if target_file.exists():
        return  # already generated

    # locate original
    base_path_str = get_image_path(base_key)
    if not base_path_str:
        return
    base_path = Path(base_path_str)
    try:
        with Image.open(base_path) as im:
            im = im.convert("RGBA")
            r, g, b, a = im.split()
            rgb = Image.merge("RGB", (r, g, b))
            inverted_rgb = ImageOps.invert(rgb)
            r2, g2, b2 = inverted_rgb.split()
            inverted = Image.merge("RGBA", (r2, g2, b2, a))
            inverted.save(target_file)
    except Exception:
        return
