"""Legacy entry point retained for backward compatibility.

The original monolithic UI has been refactored into a modular package. The
new entrypoint is `frontend/app.py`. This shim allows running:

    python frontend/Web.py

When running this file directly, Python's import path doesn't include the
project root, so we add it if needed before importing `frontend.app`.
"""

# Ensure imports work both when executed as a module and as a script.
try:
    # Prefer the local app module in this repository layout
    from app import CleanVisionApp  # type: ignore
except ModuleNotFoundError:  # fallback: adjust sys.path when executed from subdirectory
    import sys, os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from app import CleanVisionApp  # type: ignore

if __name__ == "__main__":  # pragma: no cover - manual launch convenience
    CleanVisionApp().run()
