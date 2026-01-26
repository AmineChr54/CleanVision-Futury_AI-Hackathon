# CleanVision UI Architecture

This document explains the refactored, modular Kivy architecture replacing the original monolithic `Web.py` implementation.

## Goals
- Separation of concerns (screens, widgets, services, theme)
- Easier to scale: add features without touching unrelated code
- Reusable visual components & centralized design tokens
- Clear extension points for ML model integration

## Directory Structure
```
frontend/
  app.py                 # Application entrypoint (use this going forward)
  Web.py                 # Legacy shim kept for backward compatibility
  __init__.py
  screens/
    main_screen.py       # Image upload & navigation logic
    results_screen.py    # Displays inspection results
  widgets/
    rounded_button.py    # Reusable styled button
    decor.py             # Visual decoration helpers
  services/
    inspection_service.py# Business / ML placeholder logic
  theme/
    palette.py           # Design tokens (colors, spacing, image path)
  README_UI.md           # This documentation
```

## Component Roles
### `app.CleanVisionApp`
Bootstraps the `ScreenManager` and sets global theme values.

### Screens
- `MainScreen` – handles file selection, preview, and transitions.
- `ResultsScreen` – runs the inspection service and renders results.

### Widgets
- `RoundedButton` – shared rounded button with shadow & uppercase text.
- `decor.add_rounded_background` – utility to add pill backgrounds to labels.

### Services
- `inspection_service.inspect_image(path)` – placeholder returning a mocked result. Replace with real model inference.

### Theme
`palette.py` centralizes colors, radii, spacing, and the background image path.

## How to Run
From repository root:
```powershell
python -m frontend.app
```
(Or still: `python frontend/Web.py` while legacy file remains.)

## Extending the App
### Add a New Screen
1. Create `frontend/screens/my_screen.py` with a `class MyScreen(Screen)`.
2. Register it in `app.py` after imports:
   ```python
   from frontend.screens.my_screen import MyScreen
   sm.add_widget(MyScreen())
   ```
3. Navigate via: `app.root.current = "my_screen"`.

### Integrate a Real Model
Replace logic in `inspection_service.inspect_image`:
```python
from PIL import Image
import torch

def inspect_image(image_path):
    img = Image.open(image_path)
    # preprocess -> model -> postprocess
    return {"cleanliness_score": score, "issues": issues, "image": Path(image_path).name}
```
Then UI automatically shows new JSON.

### Theming
Adjust values in `palette.py`. Consider migrating to KivyMD by mapping `PRIMARY` etc. to MDTheme if needed.

## Design Decisions
- Kept canvas-drawn decorations in Python for clarity instead of heavy KV conversion at this stage.
- Avoided KivyMD dependency to reduce setup friction; easy to add later.
- Added docstrings & typed hints to improve discoverability.

## Future Enhancements
- Add per-screen `.kv` files for more declarative layout.
- Introduce state management (e.g., a simple event bus) if logic grows.
- Implement drag & drop image import.
- Progress indicator while model runs (async thread + spinner).

## Quick API Reference
| Component | Responsibility |
|-----------|----------------|
| `RoundedButton.set_bg_color(rgba)` | Dynamically recolor button |
| `MainScreen.set_result(text)` | Show/hide status message |
| `inspect_image(path)` | Return JSON-able result dict |
| `format_result(result)` | Pretty JSON string |

## Testing Ideas
- Unit test `inspection_service.inspect_image` once real logic exists.
- UI smoke test: launch app and confirm screens register (can use `kivy.base.EventLoop.ensure_window()`).

---
Feel free to prune `Web.py` once all scripts invoke `frontend/app.py`.
