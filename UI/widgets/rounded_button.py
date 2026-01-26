"""RoundedButton wrapper using KivyMD's fill/round button style.

This keeps the `RoundedButton` API but relies on KivyMD for visuals so the
app benefits from the MD theme and widget styles.
"""
from kivymd.uix.button import MDFillRoundFlatButton

try:
    # lazily import palette if available
    from theme import palette  # type: ignore
except Exception:
    palette = None


class RoundedButton(MDFillRoundFlatButton):
    """Thin wrapper around `MDFillRoundFlatButton` that preserves a
    `bg_color` constructor parameter and provides `set_bg_color`.
    """

    def __init__(self, radius: int | float = 12, bg_color=None, **kwargs):
        # If caller passed text casing, leave it; KivyMD buttons have sensible
        # defaults. Map None bg_color to theme primary when possible.
        if bg_color is None and palette is not None:
            # Keep palette.PRIMARY as a fallback color tuple; KivyMD will use
            # theme_cls.primary_palette for coloring most MD widgets, but
            # keep explicit color when provided.
            bg_color = getattr(palette, "PRIMARY", None)

        if bg_color is not None:
            # KivyMD buttons accept `md_bg_color` to change background
            kwargs.setdefault("md_bg_color", bg_color)

        # Map legacy 'color' kwarg (from earlier Kivy Button API) to the
        # KivyMD accepted 'text_color' property for consistency.
        if "color" in kwargs:
            try:
                kwargs.setdefault("text_color", kwargs.pop("color"))
            except Exception:
                kwargs.pop("color", None)

        # MDFillRoundFlatButton (and other KivyMD buttons) do not accept a
        # `radius` kwarg; pass remaining kwargs through to the superclass.
        super().__init__(**kwargs)

    def set_bg_color(self, rgba: tuple[float, float, float, float]) -> None:
        try:
            self.md_bg_color = rgba
        except Exception:
            pass
