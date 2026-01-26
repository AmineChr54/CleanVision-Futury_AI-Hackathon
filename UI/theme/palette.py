"""Design tokens for app theming.

Centralize colors and spacing to keep a consistent look & feel. If you adopt
KivyMD later, you can map these to the Material theme palette.
"""
from kivy.core.window import Window

# Base window background (beige)
WINDOW_BG = (0.96, 0.94, 0.88, 1)

# Brand / primary colors (viridian for buttons)
# Viridian approximately rgb(64,130,109) -> normalized
PRIMARY = (0.25098, 0.5098, 0.42745, 1)  # Viridian
DARK_SURFACE = (0.06, 0.12, 0.2, 0.75)  # Deep bluish overlay (title chips)
SOFT_SURFACE = (0.06, 0.12, 0.2, 0.45)  # Softer overlay (info blocks)
PLACEHOLDER = (1, 1, 1, 0.25)  # Transparent white frame
# Text colors: primary text should be dark on a light/beige background
TEXT_PRIMARY = (0.08, 0.08, 0.08, 1)
TEXT_DARK = (0.04, 0.04, 0.04, 1)

# Common sizes
PADDING = 20
SPACING = 15
BUTTON_RADIUS = 10
CARD_RADIUS = 12

# Background image relative path
BACKGROUND_IMAGE = "images/menu.webp"
