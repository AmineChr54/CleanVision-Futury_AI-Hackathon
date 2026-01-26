"""Small decoration utilities for Kivy widgets."""
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


def add_rounded_background(widget, bg_color, radius=8, padx=12, pady=6):
    """Add a rounded translucent background to any widget.

    The rounded rectangle is drawn in canvas.before and automatically tracks
    the widget's position and size. Useful for label chips and subtle panels.
    """
    with widget.canvas.before:
        Color(*bg_color)
        rect = RoundedRectangle(
            pos=(widget.x - dp(padx // 2), widget.y - dp(pady // 2)),
            size=(widget.width + dp(padx), widget.height + dp(pady)),
            radius=[dp(radius)],
        )

    def _update_rect(*_):
        rect.pos = (widget.x - dp(padx // 2), widget.y - dp(pady // 2))
        rect.size = (widget.width + dp(padx), widget.height + dp(pady))

    widget.bind(pos=_update_rect, size=_update_rect)
