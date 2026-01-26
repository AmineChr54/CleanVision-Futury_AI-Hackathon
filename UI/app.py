"""CleanVision Kivy app entrypoint.

Modularized from the previous monolithic `Web.py` so screens, widgets, and
services live in their own modules. This makes the UI easier to scale and
maintain.
"""
from kivy.uix.screenmanager import ScreenManager    
from kivy.core.window import Window

from kivymd.app import MDApp

from theme import palette
from screens.main_screen import MainScreen
from screens.results_screen import ResultsScreen
from screens.rating_screen import RatingScreen


class CleanVisionApp(MDApp):
    """Main application class wired to KivyMD's MDApp.

    Keeps the same ScreenManager-based layout but enables KivyMD theming
    through `self.theme_cls` so child widgets can use the MD theme.
    """

    def build(self):
        # Apply global window background
        Window.clearcolor = palette.WINDOW_BG

        # Configure a simple MD theme that matches the palette preference.
        # Use a green/viridian-like primary palette and light theme style.
        try:
            # Prefer a close built-in palette and hue; the exact viridian color
            # is preserved in `theme/palette.py` for explicit usage when needed.
            self.theme_cls.primary_palette = "Green"
            self.theme_cls.primary_hue = "600"
            self.theme_cls.theme_style = "Light"
        except Exception:
            # If theme_cls isn't available for any reason, continue gracefully.
            pass

        sm = ScreenManager()
        sm.add_widget(MainScreen())
        sm.add_widget(ResultsScreen())
        sm.add_widget(RatingScreen())
        return sm


if __name__ == "__main__":
    CleanVisionApp().run()
