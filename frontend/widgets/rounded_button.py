"""Reusable rounded button widget.

This module defines `RoundedButton`, a drop-in replacement for Kivy's `Button`
that renders a rounded rectangle background with a soft shadow. It exposes a
small API to update the background color at runtime.

Usage:
    from frontend.widgets.rounded_button import RoundedButton

    btn = RoundedButton(text="Submit", radius=12, bg_color=(0.06, 0.45, 0.15, 1))
"""
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


class RoundedButton(Button):
    """Button with rounded background and subtle shadow.

    - Renders a soft shadow and a rounded rectangle in canvas.before
    - Hides default Kivy backgrounds so only custom background is visible
    - Keeps button text uppercased by default for visual consistency

    Parameters
    ----------
    radius: int | float
        Corner radius in dp units. Default: 12.
    bg_color: tuple[float, float, float, float]
        RGBA background color. Default: dark green (0.06, 0.45, 0.15, 1).
    **kwargs: Any
        Forwarded to `Button`.
    """

    def __init__(self, radius: int | float = 12, bg_color=(0.06, 0.45, 0.15, 1), **kwargs):
        super().__init__(**kwargs)
        # Hide default backgrounds so our rounded background shows
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        # Text defaults
        self.color = kwargs.get("color", (1, 1, 1, 1))
        self.font_size = kwargs.get("font_size", "16sp")
        self.bold = kwargs.get("bold", True)

        self._bg_color = bg_color
        self._radius = [dp(radius)]

        with self.canvas.before:
            # Soft shadow (slightly offset)
            Color(0, 0, 0, 0.18)
            self._shadow_rect = RoundedRectangle(pos=(self.x + dp(2), self.y - dp(2)), size=self.size, radius=self._radius)
            # Background color rectangle
            self._bg_color_instruction = Color(*self._bg_color)
            self._rounded_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self._radius)

        # Keep rectangles in sync
        self.bind(pos=self._update_rect, size=self._update_rect)

        # Normalize text casing for a cleaner look
        if isinstance(self.text, str) and self.text:
            try:
                self.text = self.text.upper()
            except Exception:
                pass

    def _update_rect(self, *_):
        # Shadow slightly offset
        self._shadow_rect.pos = (self.x + dp(2), self.y - dp(2))
        self._shadow_rect.size = self.size
        self._rounded_rect.pos = self.pos
        self._rounded_rect.size = self.size

    def set_bg_color(self, rgba: tuple[float, float, float, float]) -> None:
        """Change the background color of the rounded rectangle at runtime."""
        self._bg_color = rgba
        try:
            self._bg_color_instruction.rgba = rgba
        except Exception:
            # If canvas not yet initialized
            pass
