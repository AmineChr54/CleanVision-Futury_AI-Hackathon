"""Image asset registry package.

Place image files in this directory (e.g. settings.png, camera.png, logo.png,
robot.png) and the registry will resolve them with graceful fallbacks.
"""
from .registry import get_image_path, IMAGE_KEYS
__all__ = ["get_image_path", "IMAGE_KEYS"]
