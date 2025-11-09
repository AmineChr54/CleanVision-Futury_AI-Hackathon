"""CleanVision Kivy app entrypoint.

Modularized from the previous monolithic `Web.py` so screens, widgets, and
services live in their own modules. This makes the UI easier to scale and
maintain.
"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from frontend.theme import palette
from frontend.screens.main_screen import MainScreen
from frontend.screens.results_screen import ResultsScreen


class CleanVisionApp(App):
    """Main application class wiring together screens and theme."""

    def build(self):
        # Apply global window background
        Window.clearcolor = palette.WINDOW_BG

        sm = ScreenManager()
        sm.add_widget(MainScreen())
        sm.add_widget(ResultsScreen())
        return sm


if __name__ == "__main__":
    CleanVisionApp().run()
