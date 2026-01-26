from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Ellipse
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.metrics import dp

class RoundImageButton(ButtonBehavior, Widget):
    """Circular image button used for camera capture icon.

    Properties:
      icon_path: path to image file (png/svg rasterized) displayed centered.
      diameter: outer diameter in dp of the circular button.
      bg_rgba: background color of the circle.
      icon_scale: scale factor (0-1) of icon size relative to diameter.
    Methods:
      set_bg_rgba(rgba): change background color and redraw.
    """
    icon_path = StringProperty("")
    diameter = NumericProperty(56)
    bg_rgba = ListProperty([0.2, 0.6, 0.2, 1])
    icon_scale = NumericProperty(0.55)

    def __init__(self, icon_path: str = "", diameter: int = 56, bg_rgba=None, icon_scale: float = 0.55, **kwargs):
        super().__init__(**kwargs)
        if icon_path:
            self.icon_path = icon_path
        self.diameter = diameter
        if bg_rgba is not None:
            self.bg_rgba = bg_rgba
        self.icon_scale = icon_scale
        self.size_hint = (None, None)
        self.size = (dp(self.diameter), dp(self.diameter))
        self._img = Image(source=self.icon_path, allow_stretch=True, keep_ratio=True)
        self.add_widget(self._img)
        self.bind(pos=self._redraw, size=self._redraw, icon_path=self._update_image)
        self._redraw()

    def _update_image(self, *_):
        self._img.source = self.icon_path
        self._redraw()

    def set_bg_rgba(self, rgba):
        self.bg_rgba = rgba
        self._redraw()

    def _redraw(self, *_):
        self.canvas.clear()
        with self.canvas:
            Color(*self.bg_rgba)
            Ellipse(pos=self.pos, size=self.size)
        # Position inner image
        icon_size = dp(self.diameter * self.icon_scale)
        self._img.size = (icon_size, icon_size)
        self._img.pos = (self.x + (self.width - icon_size) / 2, self.y + (self.height - icon_size) / 2)
