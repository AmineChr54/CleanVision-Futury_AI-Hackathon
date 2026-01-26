"""Results screen to display inspection output and preview image."""
from __future__ import annotations
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivymd.uix.card import MDCard

from widgets.rounded_button import RoundedButton
from theme import palette
from services.inspection_service import inspect_image, format_result


class ResultsScreen(Screen):
    name = "results"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=palette.PADDING, spacing=palette.SPACING)
        with layout.canvas.before:
            Color(*palette.WINDOW_BG)
            self._bg_rect = Rectangle(source=palette.BACKGROUND_IMAGE, pos=layout.pos, size=Window.size)

        # Title
        title_label = MDLabel(text="Inspection Results", size_hint=(1, 0.1), font_style="H6", theme_text_color="Custom", text_color=palette.TEXT_PRIMARY)
        layout.add_widget(title_label)
        with title_label.canvas.before:
            Color(*palette.DARK_SURFACE)
            self._title_bg = RoundedRectangle(pos=(title_label.x - dp(10), title_label.y - dp(6)), size=(title_label.width + dp(20), title_label.height + dp(12)), radius=[dp(8)])
        title_label.bind(pos=self._update_title_bg, size=self._update_title_bg)

        # Image preview - larger size for better visibility
        self.result_image = Image(size_hint=(1, 0.5), allow_stretch=True, keep_ratio=True)
        layout.add_widget(self.result_image)

        # Results block - now using beautiful cards for JSON data
        results_container = BoxLayout(orientation="vertical", size_hint=(1, 0.3), spacing=dp(8))
        
        # Create card for evaluation summary
        self.eval_card = MDCard(padding=dp(16), size_hint=(1, None), height=dp(120), radius=[dp(12)])
        eval_layout = BoxLayout(orientation="vertical", spacing=dp(6))
        
        # Rating badge
        self.rating_label = MDLabel(
            text="",
            halign="left",
            font_style="H5",
            bold=True,
            theme_text_color="Custom",
            text_color=palette.PRIMARY,
            size_hint_y=None,
            height=dp(40)
        )
        eval_layout.add_widget(self.rating_label)
        
        # Score label
        self.score_display = MDLabel(
            text="",
            halign="left",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=palette.TEXT_DARK,
            size_hint_y=None,
            height=dp(30)
        )
        eval_layout.add_widget(self.score_display)
        
        self.eval_card.add_widget(eval_layout)
        results_container.add_widget(self.eval_card)
        
        # Justification card
        self.justify_card = MDCard(padding=dp(16), size_hint=(1, 1), radius=[dp(12)])
        justify_layout = BoxLayout(orientation="vertical", spacing=dp(8))
        
        justify_title = MDLabel(
            text="Root Cost and Analysis",
            halign="left",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=palette.TEXT_PRIMARY,
            size_hint_y=None,
            height=dp(30)
        )
        justify_layout.add_widget(justify_title)
        
        self.justification_text = MDLabel(
            text="",
            halign="left",
            valign="top",
            font_style="Body2",
            theme_text_color="Custom",
            text_color=palette.TEXT_DARK
        )
        self.justification_text.bind(size=lambda *_: setattr(self.justification_text, "text_size", self.justification_text.size))
        justify_layout.add_widget(self.justification_text)
        
        self.justify_card.add_widget(justify_layout)
        results_container.add_widget(self.justify_card)
        
        layout.add_widget(results_container)

        # Action buttons: Rating | Back
        buttons_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=dp(12))
        rating_btn = RoundedButton(text="Rating", size_hint=(0.5, 1), bg_color=palette.PRIMARY, radius=palette.BUTTON_RADIUS)
        rating_btn.bind(on_press=self.open_rating)
        back_btn = RoundedButton(text="Back", size_hint=(0.5, 1), bg_color=(0.92, 0.92, 0.92, 1), color=palette.PRIMARY, radius=palette.BUTTON_RADIUS)
        back_btn.bind(on_press=self.go_back)
        buttons_row.add_widget(rating_btn)
        buttons_row.add_widget(back_btn)
        layout.add_widget(buttons_row)

        self.add_widget(layout)

    # --- Canvas updates ----------------------------------------------------------
    def _update_title_bg(self, *_):
        label = self.children[0].children[2]  # title_label reference via tree
        self._title_bg.pos = (label.x - dp(10), label.y - dp(6))
        self._title_bg.size = (label.width + dp(20), label.height + dp(12))

    # --- Navigation & actions ----------------------------------------------------
    def display_inspection_results(self, image_path: str):
        """Run inspection service and render outputs."""
        # keep the current image for follow-up actions
        self.current_image_path = image_path
        
        # Display processed media (prefer GIF, else PNG/JPG/JPEG, else fallback)
        import os
        project_root = os.path.dirname(os.path.dirname(__file__))
        proc_dir = os.path.join(project_root, "pictures", "process")

        found = None
        for ext in ("gif", "png", "jpg", "jpeg"):
            p = os.path.join(proc_dir, f"process.{ext}")
            if os.path.exists(p):
                found = p
                break

        if found:
            self.result_image.source = found
            try:
                # Animate only for GIFs
                self.result_image.anim_delay = 0.04 if found.endswith(
                    ".gif"
                ) else -1
            except Exception:
                pass
        else:
            # Fallback to original image if processed media doesn't exist
            self.result_image.source = image_path
            try:
                self.result_image.anim_delay = -1
            except Exception:
                pass
        
        result = inspect_image(image_path)
        # persist the last result so follow-up screens can use it
        self.last_inspection_result = result
        
        # Load JSON evaluation if available
        json_data = self._load_json_evaluation()
        
        if json_data and isinstance(json_data, dict):
            ev = json_data.get("evaluation")
            if ev and isinstance(ev, dict):
                # Display beautiful formatted JSON data
                rating = ev.get("rating", "N/A")
                score = ev.get("score", "N/A")
                justification = ev.get("justification", "No analysis available.")

                # Map discrete score to color/percent per latest semantics.
                # Percent here represents the Green percentage for display.
                def _map_score_label_percent(val):
                    try:
                        s = int(float(val))
                    except Exception:
                        return None
                    if s == 2:
                        return ("Green", 50)
                    if s == 1:
                        return ("Orange", 25)
                    if s == 0:
                        return ("Red", 25)
                    return None
                mapped = _map_score_label_percent(score)
                
                # Set rating with color based on value
                rating_colors = {
                    "Green": palette.PRIMARY,
                    "Yellow": (1, 0.8, 0, 1),
                    "Orange": (1, 0.6, 0, 1),
                    "Red": (1, 0, 0, 1),
                }

                if mapped is not None:
                    mapped_label, percent = mapped
                    # Prefer explicit rating text if present; otherwise use mapped label
                    display_label = rating if rating != "N/A" else mapped_label
                    rating_color = rating_colors.get(display_label, palette.TEXT_PRIMARY)
                    self.rating_label.text = f"Rating: {display_label}"
                    self.rating_label.text_color = rating_color
                    self.score_display.text = f"Score: {score} ({percent}%)"
                else:
                    rating_color = rating_colors.get(rating, palette.TEXT_PRIMARY)
                    self.rating_label.text = f"Rating: {rating}"
                    self.rating_label.text_color = rating_color
                    self.score_display.text = f"Score: {score}"
                
                self.justification_text.text = justification
            else:
                self._show_fallback_results(result)
        else:
            self._show_fallback_results(result)
    
    def _show_fallback_results(self, result):
        """Show basic inspection results when JSON isn't available."""
        self.rating_label.text = "Inspection Complete"
        self.rating_label.text_color = palette.TEXT_PRIMARY
        self.score_display.text = "Processing complete"
        issues = result.get("issues", [])
        if issues:
            self.justification_text.text = "\n".join([f"• {issue}" for issue in issues])
        else:
            self.justification_text.text = "The area appears clean and well-maintained."
    
    def _load_json_evaluation(self):
        """Load most recent JSON evaluation file from project root."""
        try:
            import glob
            import json
            import os

            project_root = os.path.dirname(os.path.dirname(__file__))
            json_files = []
            
            # Collect all valid JSON files with 'evaluation' key
            for p in glob.glob(os.path.join(project_root, "*.json")):
                try:
                    with open(p, "r", encoding="utf-8") as fh:
                        doc = json.load(fh)
                    # accept files that contain an 'evaluation' key
                    if isinstance(doc, dict) and "evaluation" in doc:
                        # Store file path and its modification time
                        json_files.append((p, os.path.getmtime(p), doc))
                except Exception:
                    continue
            
            # Return the most recently modified file
            if json_files:
                json_files.sort(key=lambda x: x[1], reverse=True)
                return json_files[0][2]  # Return the document
                
        except Exception:
            pass
        return None

    def open_rating(self, _instance):
        """Navigate to the rating screen and pass the current image."""
        if not hasattr(self, "current_image_path") or not self.current_image_path:
            # nothing to rate
            return

        # Build a three-part score breakdown (green/orange/red) from the
        # inspection result. If the result contains a `cleanliness_score` we
        # use it as the green percentage and split the remainder evenly between
        # orange and red. This is a reasonable default; replace with real
        # model outputs when available.
        clean = 85
        if hasattr(self, "last_inspection_result") and isinstance(self.last_inspection_result, dict):
            try:
                clean = int(self.last_inspection_result.get("cleanliness_score", clean))
            except Exception:
                pass

        green = max(0, min(100, clean))
        remainder = max(0, 100 - green)
        orange = remainder // 2
        red = remainder - orange

        scores = {"green": green, "orange": orange, "red": red}

        # Load JSON evaluation and pass to Rating screen
        json_data = self._load_json_evaluation()

        # Prefer the attached ScreenManager when available (works during
        # programmatic tests); fall back to App.get_running_app() otherwise.
        if self.manager:
            self.manager.current = "rating"
            self.manager.get_screen("rating").display_rating(
                str(self.current_image_path), scores, json_data
            )
            return

        from kivy.app import App
        app = App.get_running_app()
        if app and getattr(app, "root", None):
            app.root.current = "rating"
            app.root.get_screen("rating").display_rating(
                str(self.current_image_path), scores, json_data
            )

    def go_back(self, _instance):
        if self.manager:
            self.manager.current = "main"
            return

        from kivy.app import App
        app = App.get_running_app()
        if app and getattr(app, "root", None):
            app.root.current = "main"
