"""Rating screen where user can rate the inspection result.

Shows the inspected image and a simple back button to return to the results
screen. The UI is intentionally minimal — expand later with rating widgets or
stars as needed.
"""
from __future__ import annotations
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivymd.uix.card import MDCard

from widgets.rounded_button import RoundedButton
from theme import palette


class RatingScreen(Screen):
    name = "rating"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=palette.PADDING,
            spacing=palette.SPACING,
        )
        # Full beige background across entire screen
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*palette.WINDOW_BG)
            self._bg_rect = Rectangle(pos=self.pos, size=Window.size)
        self.bind(pos=self._update_bg_rect, size=self._update_bg_rect)
        Window.bind(size=self._update_bg_rect)

        # Title
        title_label = MDLabel(
            text="Rate Inspection",
            size_hint=(1, 0.1),
            font_style="H6",
            theme_text_color="Custom",
            text_color=palette.TEXT_PRIMARY,
        )
        layout.add_widget(title_label)

        # Image preview (reduced height to make room for the chart)
        # Shift image left by wrapping in a BoxLayout with right spacer
        image_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.5))
        self.rating_image = Image(
            size_hint=(0.97, 1),
            allow_stretch=True,
            keep_ratio=True,
        )
        image_row.add_widget(self.rating_image)
        # small right spacer to bias left
        image_row.add_widget(Widget(size_hint=(0.03, 1)))
        layout.add_widget(image_row)

    # Top row: two widgets side-by-side (left: score card, right: diagram card)
        top_row = BoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.4),
            spacing=dp(12),
        )

        # Left: Score card (shows the short rating and numeric score)
        score_card = MDCard(
            padding=dp(16),
            size_hint=(0.5, 1),
            radius=[dp(10)],
        )
        score_card.md_bg_color = (1, 1, 1, 1)  # White background
        self.score_label = MDLabel(
            text="",
            halign="center",
            valign="middle",
            theme_text_color="Custom",
            text_color=palette.TEXT_DARK,
            font_style="H6",
        )
        self.score_label.bind(
            size=lambda *_: setattr(
                self.score_label,
                "text_size",
                self.score_label.size,
            )
        )
        score_card.add_widget(self.score_label)

        # Right: Diagram card (holds the canvas widget where pie is drawn)
        diagram_card = MDCard(
            padding=dp(12),
            size_hint=(0.5, 1),
            radius=[dp(10)],
        )
        diagram_card.md_bg_color = (1, 1, 1, 1)  # White background
        chart_widget = Widget(
            size_hint=(None, None),
            size=(dp(280), dp(280)),
        )
        # center the chart within the card using an inner BoxLayout
        chart_container = BoxLayout()
        chart_container.add_widget(Widget())
        chart_container.add_widget(chart_widget)
        chart_container.add_widget(Widget())
        diagram_card.add_widget(chart_container)

        top_row.add_widget(score_card)
        top_row.add_widget(diagram_card)
        layout.add_widget(top_row)

        # store references the drawing code expects
        self.ids_chart = chart_widget
        # center label overlay inside the diagram_card
        self.center_label = MDLabel(
            text="",
            size_hint=(None, None),
            size=(dp(170), dp(100)),
            halign="center",
            valign="middle",
            theme_text_color="Custom",
            text_color=palette.TEXT_DARK,
        )
        self.center_label.bind(
            size=lambda *_: setattr(
                self.center_label,
                "text_size",
                self.center_label.size,
            )
        )
    # add the center label above the chart
        diagram_card.add_widget(self.center_label)
        # Redraw when the chart widget is laid out so the pie is centered
        # (initial sizes may be zero until the layout pass).
        self.ids_chart.bind(
            pos=lambda *_: self._draw_chart(),
            size=lambda *_: self._draw_chart(),
        )

        # Bottom full-width justification card
        justify_card = MDCard(
            padding=dp(12),
            size_hint=(1, 0.3),
            radius=[dp(10)],
        )
        justify_card.md_bg_color = (1, 1, 1, 1)  # White background
        self.justification_label = MDLabel(
            text="",
            halign="left",
            valign="top",
            theme_text_color="Custom",
            text_color=palette.TEXT_DARK,
        )
        self.justification_label.bind(
            size=lambda *_: setattr(
                self.justification_label,
                "text_size",
                self.justification_label.size,
            )
        )
        justify_card.add_widget(self.justification_label)
        layout.add_widget(justify_card)

        # Back button (returns to results)
        back_button = RoundedButton(
            text="Back",
            size_hint=(1, 0.1),
            bg_color=(0.92, 0.92, 0.92, 1),
            text_color=palette.PRIMARY,
        )
        back_button.bind(on_press=self.go_back_to_results)
        layout.add_widget(back_button)

        self.add_widget(layout)

    # display_rating expects (image_path, scores) from ResultsScreen

    def display_rating(
        self,
        image_path: str,
        scores: dict | None = None,
        json_data: dict | None = None,
    ):
        # Primary signature used by ResultsScreen
        # Display done image from pictures/done/done.jpg
        import os
        project_root = os.path.dirname(os.path.dirname(__file__))
        done_dir = os.path.join(project_root, "pictures", "done")
        found = None
        for ext in ("gif", "png", "jpg", "jpeg"):
            candidate = os.path.join(done_dir, f"done.{ext}")
            if os.path.exists(candidate):
                found = candidate
                break

        if found:
            self.rating_image.source = found
            try:
                if found.endswith(".gif"):
                    self.rating_image.anim_delay = 0.04
                else:
                    self.rating_image.anim_delay = -1
            except Exception:
                pass
        else:
            # Fallback to original image if done image doesn't exist
            self.rating_image.source = image_path
            try:
                self.rating_image.anim_delay = -1
            except Exception:
                pass
        
        # If JSON evaluation data is provided, prefer it to drive the screen
        if json_data and isinstance(json_data, dict):
            raw_eval = json_data.get("evaluation")
            ev = raw_eval if isinstance(raw_eval, dict) else None
        else:
            ev = None

        def _map_score(score_val):
            """Map discrete score to percent and G/O/R composition.

            Updated semantics:
              - 1 (Orange): Green 25%, Orange 50%, Red 25% (percent=Green=25)
              - 2 (Green):  Green 50%, Orange 25%, Red 25% (percent=Green=50)
              - 0 (Red):    Red 50%, Green 25%, Orange 25% (percent=Green=25)
            Returns (percent:int, segments:dict, label:str)
            """
            try:
                s = int(float(score_val))
            except Exception:
                return None
            if s == 2:
                return 50, {"green": 50, "orange": 25, "red": 25}, "Green"
            if s == 1:
                return 25, {"green": 25, "orange": 50, "red": 25}, "Orange"
            if s == 0:
                return 25, {"green": 25, "orange": 25, "red": 50}, "Red"
            # default: keep neutral split favoring red
            return 25, {"green": 25, "orange": 25, "red": 50}, "Red"

        if ev:
            # Populate score and justification from JSON with new mapping
            raw_score = ev.get("score")
            mapped = _map_score(raw_score)
            rating_short = ev.get("rating")

            if mapped is not None:
                percent, segments, mapped_label = mapped
                # Prefer explicit rating if provided; else derive from mapping
                display_label = rating_short or mapped_label
                self.score_label.text = (
                    f"{display_label}\n"  # removed [b] markup
                    f"Score: {raw_score} ({percent}%)"
                )
                # If the rating is Orange, make this label bigger
                try:
                    if str(display_label).lower() == "orange":
                        self.score_label.font_style = "H5"
                    else:
                        self.score_label.font_style = "H6"
                except Exception:
                    pass
                self.set_scores(segments)
            elif scores:
                # fallback to provided scores
                self.set_scores(scores)
                # basic label
                self.score_label.text = f"Score: {raw_score}"

            # Justification text
            justification = ev.get("justification")
            if justification:
                self.justification_label.text = justification
        else:
            # No JSON provided: use supplied scores; clear JSON-driven labels
            if scores:
                self.set_scores(scores)
            self.score_label.text = ""
            self.justification_label.text = ""

    # --- Chart rendering -------------------------------------------------
    def set_scores(self, scores: dict):
        """Receive a dict with three percentages and redraw the chart."""
        # Normalize and ensure integer percentages summing to 100
        g = int(scores.get("green", 0))
        o = int(scores.get("orange", 0))
        r = int(scores.get("red", 0))
        total = g + o + r
        if total == 0:
            # default mock
            g, o, r = 85, 7, 8
            total = 100
        if total != 100:
            # scale to 100
            g = int(round(g * 100 / total))
            o = int(round(o * 100 / total))
            r = 100 - g - o

        self._scores = {"green": g, "orange": o, "red": r}
        self._draw_chart()
        # update textual data under the chart
        if hasattr(self, "data_label"):
            self.data_label.text = (
                f"Green: {g}%   ·   Orange: {o}%   ·   Red: {r}%"
            )

    def _draw_chart(self, *args):
        # Draw three colored sectors using canvas instructions
        if not hasattr(self, "_scores"):
            return
        scores = self._scores
        widget = self.ids_chart
        # Guard: widget must have non-zero size to draw centered
        if widget.width <= 0 or widget.height <= 0:
            return

        # Clear previous canvas
        widget.canvas.clear()
        with widget.canvas:
            from kivy.graphics import Color, Ellipse

            size = min(widget.width, widget.height) * 0.5
            cx = widget.x + widget.width / 2
            cy = widget.y + widget.height / 2
            left = cx - size
            bottom = cy - size

            start = 0
            # green
            Color(*palette.PRIMARY)
            sweep = scores["green"] * 3.6
            Ellipse(
                pos=(left, bottom),
                size=(size, size),
                angle_start=start,
                angle_end=start + sweep,
            )
            start += sweep
            # orange
            Color(1, 0.6, 0, 1)
            sweep = scores["orange"] * 3.6
            Ellipse(
                pos=(left, bottom),
                size=(size, size),
                angle_start=start,
                angle_end=start + sweep,
            )
            start += sweep
            # red
            Color(1, 0, 0, 1)
            sweep = scores["red"] * 3.6
            Ellipse(
                pos=(left, bottom),
                size=(size, size),
                angle_start=start,
                angle_end=start + sweep,
            )

        # Center label update
        if hasattr(self, "center_label"):
            self.center_label.text = (
                f"G:{scores['green']}%\n"
                f"O:{scores['orange']}%\n"
                f"R:{scores['red']}%"
            )

    def go_back_to_results(self, _instance):
        # Prefer attached manager when available
        if self.manager:
            self.manager.current = "results"
            return

        from kivy.app import App
        app = App.get_running_app()
        if app and getattr(app, "root", None):
            app.root.current = "results"

    def _update_bg_rect(self, *_):
        # Keep the beige background rectangle in sync with screen size
        if hasattr(self, "_bg_rect"):
            self._bg_rect.pos = self.pos
            self._bg_rect.size = Window.size
