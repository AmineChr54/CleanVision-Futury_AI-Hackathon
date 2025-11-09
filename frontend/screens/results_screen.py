"""Results screen to display inspection output and preview image."""
from __future__ import annotations
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle

from frontend.widgets.rounded_button import RoundedButton
from frontend.theme import palette
from frontend.services.inspection_service import inspect_image, format_result


class ResultsScreen(Screen):
    name = "results"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=palette.PADDING, spacing=palette.SPACING)
        with layout.canvas.before:
            Color(*palette.WINDOW_BG)
            self._bg_rect = Rectangle(source=palette.BACKGROUND_IMAGE, pos=layout.pos, size=Window.size)

        # Title
        title_label = Label(text="Inspection Results", size_hint=(1, 0.1), font_size="20sp", bold=True, color=palette.TEXT_PRIMARY)
        layout.add_widget(title_label)
        with title_label.canvas.before:
            Color(*palette.DARK_SURFACE)
            self._title_bg = RoundedRectangle(pos=(title_label.x - dp(10), title_label.y - dp(6)), size=(title_label.width + dp(20), title_label.height + dp(12)), radius=[dp(8)])
        title_label.bind(pos=self._update_title_bg, size=self._update_title_bg)

        # Image preview
        self.result_image = Image(size_hint=(1, 0.4), allow_stretch=True, keep_ratio=True)
        layout.add_widget(self.result_image)

        # Results block
        self.results_label = Label(text="Processing...", size_hint=(1, 0.4), text_size=(Window.width - 40, None), color=palette.TEXT_PRIMARY)
        layout.add_widget(self.results_label)
        with self.results_label.canvas.before:
            Color(*palette.SOFT_SURFACE)
            self._results_bg = RoundedRectangle(pos=(self.results_label.x - dp(12), self.results_label.y - dp(6)), size=(self.results_label.width + dp(24), self.results_label.height + dp(12)), radius=[dp(10)])
        self.results_label.bind(pos=self._update_results_bg, size=self._update_results_bg)

        # Back button
        back_button = RoundedButton(text="Back to Menu", size_hint=(1, 0.1), bg_color=palette.PRIMARY, radius=palette.BUTTON_RADIUS)
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    # --- Canvas updates ----------------------------------------------------------
    def _update_title_bg(self, *_):
        label = self.children[0].children[2]  # title_label reference via tree
        self._title_bg.pos = (label.x - dp(10), label.y - dp(6))
        self._title_bg.size = (label.width + dp(20), label.height + dp(12))

    def _update_results_bg(self, *_):
        self._results_bg.pos = (self.results_label.x - dp(12), self.results_label.y - dp(6))
        self._results_bg.size = (self.results_label.width + dp(24), self.results_label.height + dp(12))

    # --- Navigation & actions ----------------------------------------------------
    def display_inspection_results(self, image_path: str):
        """Run inspection service and render outputs."""
        self.result_image.source = image_path
        result = inspect_image(image_path)
        self.results_label.text = f"Results:\n{format_result(result)}"

    def go_back(self, _instance):
        from kivy.app import App
        app = App.get_running_app()
        app.root.current = "main"
