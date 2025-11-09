"""Main upload screen with fixed top bar and bottom actions.

Responsible for:
- Letting user pick or capture an image
- Showing a helpful robot tip when no image is selected
- Replacing the tip with the preview and a submit button after upload
- Providing bottom actions: Browse, Capture, Process
"""
from __future__ import annotations
from pathlib import Path
import os
import tempfile
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from typing import Optional

try:
    # Optional camera support (desktop availability varies)
    from plyer import camera as plyer_camera  # type: ignore
except Exception:
    plyer_camera = None

from frontend.widgets.rounded_button import RoundedButton
from frontend.widgets.decor import add_rounded_background
from frontend.theme import palette


class MainScreen(Screen):
    name = "main"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=palette.PADDING, spacing=palette.SPACING)

        # Background image
        with layout.canvas.before:
            Color(*palette.WINDOW_BG)
            self._bg_rect = Rectangle(source=palette.BACKGROUND_IMAGE, pos=layout.pos, size=Window.size)

        Window.bind(size=self._update_bg_rect)

        # --- Top Navigation Bar (fixed) ---------------------------------------
        nav = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(56), padding=(dp(12), 0), spacing=dp(10))
        with nav.canvas.before:
            Color(0, 0, 0, 0.25)
            self._nav_bg = RoundedRectangle(pos=nav.pos, size=nav.size, radius=[dp(12)])
        nav.bind(pos=self._update_nav_bg, size=self._update_nav_bg)

        # Left: Logo (image if exists, else text)
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "images", "logo.png")
        if os.path.exists(logo_path):
            logo = Image(source=logo_path, size_hint=(None, 1), width=dp(120), allow_stretch=True, keep_ratio=True)
        else:
            logo = Label(text="[b]CleanVision[/b]", markup=True, color=palette.TEXT_PRIMARY, size_hint=(None, 1), width=dp(140))
        nav.add_widget(logo)

        nav.add_widget(Widget())  # spacer

        # Right: Settings button
        settings_btn = RoundedButton(text="\u2699", size_hint=(None, 0.8), width=dp(56), bg_color=palette.PRIMARY, radius=palette.BUTTON_RADIUS)
        settings_btn.bind(on_press=self.open_settings)
        nav.add_widget(settings_btn)
        layout.add_widget(nav)

        # Title label
        self.title_label = Label(
            text="CLEAN PROCESS",
            size_hint=(1, 0.09),
            font_size="26sp",
            bold=True,
            color=palette.TEXT_PRIMARY,
            halign="center",
            valign="middle",
            text_size=(Window.width - 40, None),
        )
        add_rounded_background(self.title_label, palette.DARK_SURFACE, radius=palette.CARD_RADIUS)
        layout.add_widget(self.title_label)

        # --- Middle content area (robot tip OR preview) -----------------------
        middle_area = BoxLayout(orientation="vertical", size_hint=(1, 1))
        middle_area.add_widget(Widget(size_hint_y=1))

        self.middle_container = BoxLayout(orientation="vertical", size_hint=(1, None), height=dp(360), spacing=dp(10))
        # Robot tip card
        self.robot_tip_card = self._build_robot_tip()
        # Preview card (image + submit under it)
        self.preview_card = self._build_preview_card()
        # Start with tip visible
        self.middle_container.clear_widgets()
        self.middle_container.add_widget(self.robot_tip_card)

        middle_area.add_widget(self.middle_container)
        middle_area.add_widget(Widget(size_hint_y=1))
        layout.add_widget(middle_area)

        # Result label (hidden until used)
        self.result_label = Label(text="", size_hint=(1, None), height=dp(80), text_size=(Window.width - 40, None), color=(0.08, 0.08, 0.08, 0), halign="left", valign="top")
        layout.add_widget(self.result_label)

        # --- Bottom action bar: Browse | Capture | Process ---------------------
        self.buttons_container = BoxLayout(size_hint=(1, None), height=dp(60), spacing=dp(12))
        self.browse_button = RoundedButton(text="Browse", bg_color=palette.PRIMARY, radius=palette.BUTTON_RADIUS)
        self.browse_button.bind(on_press=self.open_file_chooser)
        self.capture_button = RoundedButton(text="Capture", bg_color=palette.PRIMARY, radius=palette.BUTTON_RADIUS)
        self.capture_button.bind(on_press=self.capture_image)
        self.process_button = RoundedButton(text="Process", bg_color=palette.PRIMARY, radius=palette.BUTTON_RADIUS)
        self.process_button.bind(on_press=self.process_current)
        self.buttons_container.add_widget(self.browse_button)
        self.buttons_container.add_widget(self.capture_button)
        self.buttons_container.add_widget(self.process_button)
        layout.add_widget(self.buttons_container)

        self.add_widget(layout)
        # Track current image path (None until selected or captured)
        self.current_image_path = None  # type: Optional[Path]

    # --- Canvas/Geometry updates -------------------------------------------------
    def _update_bg_rect(self, *_):
        self._bg_rect.pos = self.children[0].pos  # layout
        self._bg_rect.size = Window.size

    def _update_nav_bg(self, instance, *_):
        # Keep the rounded background in sync with the nav bar
        self._nav_bg.pos = instance.pos
        self._nav_bg.size = instance.size

    # --- Helpers -----------------------------------------------------------------
    def set_result(self, text: str):
        if text and str(text).strip():
            self.result_label.text = str(text)
            col = list(self.result_label.color)
            col[3] = 1
            self.result_label.color = tuple(col)
        else:
            self.result_label.text = ""
            col = list(self.result_label.color)
            col[3] = 0
            self.result_label.color = tuple(col)

    # --- Actions -----------------------------------------------------------------
    def open_settings(self, _instance):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        label = Label(text="Settings coming soon...", color=palette.TEXT_PRIMARY)
        ok = RoundedButton(text="Close", bg_color=palette.PRIMARY, size_hint=(1, None), height=dp(44))
        content.add_widget(label)
        content.add_widget(ok)
        popup = Popup(title="Settings", content=content, size_hint=(0.5, 0.35))
        ok.bind(on_press=lambda *_: popup.dismiss())
        popup.open()

    def open_file_chooser(self, _instance):
        content = BoxLayout(orientation="vertical")
        file_chooser = FileChooserIconView(filters=["*.png", "*.jpg", "*.jpeg"])
        buttons_layout = BoxLayout(size_hint=(1, 0.1))
        cancel_btn = RoundedButton(text="Cancel", bg_color=(0.5, 0.5, 0.5, 1), radius=8)
        select_btn = RoundedButton(text="Select", bg_color=palette.PRIMARY, radius=8)
        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(select_btn)
        content.add_widget(file_chooser)
        content.add_widget(buttons_layout)
        popup = Popup(title="Object Image", content=content, size_hint=(0.9, 0.9))

        def select_image(_btn):
            if file_chooser.selection:
                self.load_image(file_chooser.selection[0])
                popup.dismiss()

        def cancel_selection(_btn):
            popup.dismiss()

        select_btn.bind(on_press=select_image)
        cancel_btn.bind(on_press=cancel_selection)
        popup.open()

    def load_image(self, file_path: str):
        self.current_image_path = Path(file_path)
        self.set_result("")
        self._show_preview(file_path)

    def clear_image(self, _instance):
        self.current_image_path = None
        self.set_result("")
        self._show_robot_tip()

    def go_to_results(self, _instance):
        if not self.current_image_path:
            self.set_result("Please select an image first!")
            return
        from kivy.app import App
        app = App.get_running_app()
        app.root.current = "results"
        app.root.get_screen("results").display_inspection_results(str(self.current_image_path))

    def process_current(self, _instance):
        # Right bottom button behavior
        if self.current_image_path:
            self.go_to_results(_instance)
        else:
            self.set_result("Please select or capture an image first!")

    def capture_image(self, _instance):
        # Attempt camera capture; fall back to file chooser
        if plyer_camera is None:
            self.set_result("Camera not available on this device. Please browse an image.")
            self.open_file_chooser(_instance)
            return

        tmp_file = os.path.join(tempfile.gettempdir(), f"cleanvision_capture.jpg")

        def _on_complete(path):
            # Plyer calls callback with path (may be None on cancel)
            if path and os.path.exists(path):
                self.load_image(path)
            else:
                self.set_result("Capture canceled.")

        try:
            plyer_camera.take_picture(filename=tmp_file, on_complete=_on_complete)
        except Exception:
            # Some platforms need no callback signature
            try:
                plyer_camera.take_picture(filename=tmp_file)
                if os.path.exists(tmp_file):
                    self.load_image(tmp_file)
                else:
                    self.set_result("Unable to capture image.")
            except Exception as e:
                self.set_result(f"Camera error: {e}")

    # --- UI builders ------------------------------------------------------------
    def _build_robot_tip(self) -> BoxLayout:
        card = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10), size_hint=(1, None), height=dp(260))
        with card.canvas.before:
            Color(*palette.SOFT_SURFACE)
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=lambda *_: self._sync_rect(card), size=lambda *_: self._sync_rect(card))

        # Optional robot image
        robot_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "images", "robot.png")
        if os.path.exists(robot_path):
            robot_img = Image(source=robot_path, size_hint=(1, None), height=dp(120), allow_stretch=True, keep_ratio=True)
            card.add_widget(robot_img)

        tip_title = Label(text="Hi, I'm your cleaning robot!", size_hint=(1, None), height=dp(28), color=palette.TEXT_PRIMARY, bold=True)
        tip_body = Label(
            text="Tip: Tap Browse to pick an image or Capture to take a new one. Then press Process to analyze.",
            size_hint=(1, 1),
            color=palette.TEXT_PRIMARY,
            halign="center",
            valign="middle",
        )
        tip_body.bind(size=lambda *_: setattr(tip_body, "text_size", tip_body.size))
        card.add_widget(tip_title)
        card.add_widget(tip_body)
        return card

    def _build_preview_card(self) -> BoxLayout:
        card = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10), size_hint=(1, None), height=dp(340))
        with card.canvas.before:
            Color(1, 1, 1, 0.0)
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=lambda *_: self._sync_rect(card), size=lambda *_: self._sync_rect(card))

        # Image preview with decorative frame
        self._img_container = BoxLayout(size_hint=(1, None), height=dp(260))
        self.center_image = Image(source="", size_hint=(1, 1), allow_stretch=True, keep_ratio=True, opacity=1)
        self._img_container.add_widget(self.center_image)
        with self._img_container.canvas.before:
            Color(*palette.PLACEHOLDER)
            self._placeholder_rect = RoundedRectangle(pos=(self._img_container.x - dp(12), self._img_container.y - dp(12)), size=(self._img_container.width + dp(24), self._img_container.height + dp(24)), radius=[dp(14)])
        self._img_container.bind(pos=self._update_placeholder_rect_preview, size=self._update_placeholder_rect_preview)
        card.add_widget(self._img_container)

        # Submit button under the image
        self.submit_under_preview = RoundedButton(text="Submit", size_hint=(None, None), width=dp(180), height=dp(48), bg_color=palette.PRIMARY, radius=palette.BUTTON_RADIUS)
        self.submit_under_preview.bind(on_press=self.go_to_results)
        # center horizontally using an inner BoxLayout with spacers
        row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(48))
        row.add_widget(Widget())
        row.add_widget(self.submit_under_preview)
        row.add_widget(Widget())
        card.add_widget(row)
        return card

    def _sync_rect(self, widget):
        # Helper to keep rounded rect backgrounds aligned
        if hasattr(widget, "_bg"):
            widget._bg.pos = widget.pos
            widget._bg.size = widget.size

    def _update_placeholder_rect_preview(self, *_):
        # Sync decorative preview frame
        # Find the image container via submit_under_preview parent chain if needed
        if hasattr(self, "_placeholder_rect") and self.preview_card in self.middle_container.children:
            img_container = self._img_container
            self._placeholder_rect.pos = (img_container.x - dp(12), img_container.y - dp(12))
            self._placeholder_rect.size = (img_container.width + dp(24), img_container.height + dp(24))

    # --- View switching ---------------------------------------------------------
    def _show_robot_tip(self):
        self.middle_container.clear_widgets()
        self.middle_container.add_widget(self.robot_tip_card)
        # Clear preview content
        if hasattr(self, "center_image"):
            self.center_image.source = ""

    def _show_preview(self, file_path: str):
        self.middle_container.clear_widgets()
        self.middle_container.add_widget(self.preview_card)
        self.center_image.source = file_path
