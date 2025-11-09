"""Design tokens for app theming.

Centralize colors and spacing to keep a consistent look & feel. If you adopt
KivyMD later, you can map these to the Material theme palette.
"""
from kivy.core.window import Window

# Base window background (white)
WINDOW_BG = (1, 1, 1, 1)

# Brand / primary colors
PRIMARY = (0.06, 0.45, 0.15, 1)  # Dark green
DARK_SURFACE = (0.06, 0.12, 0.2, 0.75)  # Deep bluish overlay (title chips)
SOFT_SURFACE = (0.06, 0.12, 0.2, 0.45)  # Softer overlay (info blocks)
PLACEHOLDER = (1, 1, 1, 0.25)  # Transparent white frame
TEXT_PRIMARY = (1, 1, 1, 1)
TEXT_DARK = (0.08, 0.08, 0.08, 1)

# Common sizes
PADDING = 20
SPACING = 15
BUTTON_RADIUS = 10
CARD_RADIUS = 12

# Background image relative path
BACKGROUND_IMAGE = "images/menu.webp"
