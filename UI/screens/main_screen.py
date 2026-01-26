"""Main upload screen (KivyMD version).

Reimplemented using KivyMD components for a more professional Material look:
    - MDToolbar for top navigation with brand logo title and settings icon
    - MDCard for robot tip and image preview area
    - MDRaisedButton & MDIconButton variants for actions
    - RoundImageButton retained for custom circular icon styling (camera capture)
"""
from __future__ import annotations
from pathlib import Path
import os
import tempfile
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout


from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton

try:  # optional camera
    from plyer import camera as plyer_camera  # type: ignore
except Exception:
    plyer_camera = None

from widgets.round_image_button import RoundImageButton
from images import get_image_path
from theme import palette
from widgets.hover import attach_hover


class TopBar(MDBoxLayout):
    """Lightweight custom top bar for legacy KivyMD 1.2.0 without MDToolbar availability."""
    def __init__(self, title: str = "", **kwargs):
        super().__init__(orientation="horizontal", size_hint=(1, None), height=dp(56), padding=(dp(14), 0), spacing=dp(6), **kwargs)
        self._title_label = MDLabel(text=title, halign="left", font_style="H6")
        self.add_widget(self._title_label)
        self._spacer = Widget()
        self.add_widget(self._spacer)
        self._actions_box = MDBoxLayout(orientation="horizontal", size_hint=(None, 1), spacing=dp(4))
        self.add_widget(self._actions_box)

    @property
    def title(self) -> str:
        return self._title_label.text

    @title.setter
    def title(self, value: str) -> None:
        self._title_label.text = value

    @property
    def right_action_items(self):
        return getattr(self, "_right_items", [])

    @right_action_items.setter
    def right_action_items(self, items):
        self._right_items = items or []
        self._actions_box.clear_widgets()
        for icon, cb in self._right_items:
            btn = MDIconButton(icon=icon)
            btn.bind(on_release=lambda *_: cb())
            self._actions_box.add_widget(btn)

    def set_title_widget(self, widget: Widget):
        """Replace the text title with a custom widget (e.g., an Image logo)."""
        if self._title_label in self.children:
            self.remove_widget(self._title_label)
        # Insert at the beginning to keep it on the left
        self.add_widget(widget, index=len(self.children))


class MainScreen(MDScreen):
    name = "main"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Slightly tighter vertical spacing to pull content closer to the top bar
        root_layout = MDBoxLayout(orientation="vertical", spacing=dp(6))

        # Set screen background to theme window color
        try:
            self.md_bg_color = palette.WINDOW_BG
        except Exception:
            pass

        # Top bar (custom, avoids missing MDToolbar in deprecated KivyMD 1.2.0)
        logo_title = get_image_path("logo_title")
        toolbar = TopBar(title="")
        if logo_title:
            logo_widget = Image(source=logo_title, size_hint=(None, None), size=(dp(180), dp(44)), allow_stretch=True, keep_ratio=True)
            toolbar.set_title_widget(logo_widget)
        else:
            toolbar.title = "CleanVision"
        toolbar.right_action_items = [("cog", lambda *_: self.open_settings(None))]
        root_layout.add_widget(toolbar)

        # Content area (robot tip or preview) - reduced top padding to shift upward
        self.content_container = MDBoxLayout(orientation="vertical", padding=(dp(8), dp(4), dp(8), dp(8)), spacing=dp(12))
        try:
            self.content_container.md_bg_color = palette.WINDOW_BG
        except Exception:
            pass
        self.robot_tip_card = self._build_robot_tip_card()
        self.preview_card = self._build_preview_card()
        self._show_robot_tip()
        root_layout.add_widget(self.content_container)

        # Bottom action bar (left aligned, flex-like spacing) with window background
        self.bottom_bar = MDBoxLayout(orientation="horizontal", adaptive_height=True, padding=(dp(16), dp(6)), spacing=dp(20))
        self.bottom_bar.md_bg_color = palette.WINDOW_BG
        self._build_bottom_bar()
        root_layout.add_widget(self.bottom_bar)

        self.add_widget(root_layout)

        # Track current image path (None until selected or captured)
        self.current_image_path = None  # type: Optional[Path]

        # Apply hover to toolbar actions (e.g., settings cog) if present
        try:
            self._apply_hover_to_toolbar(toolbar)
        except Exception:
            pass

    # --- Canvas/Geometry updates -------------------------------------------------
    # --- Bottom bar construction -----------------------------------------------
    def _build_bottom_bar(self):
        # Capture round button (smaller diameter). Prefer dynamically generated inverted icon.
        camera_icon = get_image_path("camera_inverted") or get_image_path("camera")
        self.capture_btn = RoundImageButton(icon_path=camera_icon, diameter=56, bg_rgba=palette.PRIMARY, icon_scale=0.5)
        self.capture_btn.bind(on_release=self.capture_image)
        self.bottom_bar.add_widget(self._wrap_center(self.capture_btn))

        # Browse button with primary bg and themed text color
        self.browse_btn = MDRaisedButton(text="Browse", md_bg_color=palette.PRIMARY, text_color=palette.TEXT_PRIMARY)
        self.browse_btn.bind(on_release=self.open_file_chooser)
        self.bottom_bar.add_widget(self._wrap_center(self.browse_btn))

        # Hover effects: lighten on hover
        self._apply_hover_to_primary_button(self.browse_btn)
        self._apply_hover_to_round(self.capture_btn)


    def _wrap_center(self, child):
        """Wrap a widget so it's vertically centered within the bottom bar.

        Uses AnchorLayout to center on Y regardless of the child's own height.
        """
        wrapper = AnchorLayout(anchor_x='left', anchor_y='center', size_hint=(None, None), height=dp(60))

        def _sync_width(*_):
            # keep wrapper at least the child's width
            wrapper.width = max(child.width, dp(56))

        child.bind(size=_sync_width)
        _sync_width()
        wrapper.add_widget(child)
        return wrapper

    # --- Helpers -----------------------------------------------------------------
    def set_result(self, text: str):
        if text and str(text).strip():
            toast(str(text))

    # --- Actions -----------------------------------------------------------------
    def open_settings(self, _instance):
        toast("Settings dialog coming soon.")

    def open_file_chooser(self, _instance):
        # Simple MD popup replacement using standard Popup for now.
        content = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(12))
        chooser = FileChooserIconView(filters=["*.png", "*.jpg", "*.jpeg"], size_hint=(1, 0.9))
        btn_row = MDBoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=dp(12))
        cancel = MDRaisedButton(text="Cancel")
        select = MDRaisedButton(text="Select", md_bg_color=palette.PRIMARY)
        btn_row.add_widget(cancel)
        btn_row.add_widget(select)
        content.add_widget(chooser)
        content.add_widget(btn_row)
        popup = Popup(title="Select Image", content=content, size_hint=(0.9, 0.9))

        def _do_select(_):
            if chooser.selection:
                self.load_image(chooser.selection[0])
                popup.dismiss()
        select.bind(on_release=_do_select)
        cancel.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def load_image(self, file_path: str):
        self.current_image_path = Path(file_path)
        self.set_result("")
        self._show_preview(file_path)

    def clear_image(self, _instance):
        self.current_image_path = None
        self._show_robot_tip()
        toast("Image cleared.")

    def go_to_results(self, _instance):
        if not self.current_image_path:
            self.set_result("Please select an image first!")
            return
        from kivy.app import App
        app = App.get_running_app()
        app.root.current = "results"
        app.root.get_screen("results").display_inspection_results(str(self.current_image_path))

    def process_current(self, _instance):
        if not self.current_image_path:
            toast("Select or capture an image first.")
            return
        self.go_to_results(_instance)

    def capture_image(self, _instance):
        # Attempt camera capture; fall back to file chooser
        if plyer_camera is None:
            self.set_result("Camera not available on this device. Please browse an image.")
            self.open_file_chooser(_instance)
            return
        ################################## give to backend
        tmp_file = os.path.join(tempfile.gettempdir(), "cleanvision_capture.jpg")

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
    def _build_robot_tip_card(self):
        card = MDCard(orientation="vertical", padding=dp(18), size_hint=(1, None), height=dp(300), elevation=0, radius=[dp(18)])
        card.spacing = dp(12)
        robot_path = get_image_path("robot")
        if robot_path:
            robot_img = Image(source=robot_path, size_hint=(1, None), height=dp(150), allow_stretch=True, keep_ratio=True)
            card.add_widget(robot_img)
        title = MDLabel(text="Hi, I'm your cleaning robot!", font_style="H6", halign="center")
        body = MDLabel(text="Tip: Browse to pick an image or use the camera to capture one, then press Process to analyze.", halign="center", theme_text_color="Secondary")
        card.add_widget(title)
        card.add_widget(body)
        return card

    def _build_preview_card(self):
        card = MDCard(orientation="vertical", padding=dp(18), size_hint=(1, None), height=dp(400), elevation=0, radius=[dp(22)])
        card.spacing = dp(16)
        # Image preview
        self._img_container = MDBoxLayout(size_hint=(1, None), height=dp(280))
        self.center_image = Image(source="", allow_stretch=True, keep_ratio=True)
        self._img_container.add_widget(self.center_image)
        card.add_widget(self._img_container)
        # Action buttons row
        actions_row = MDBoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(60), spacing=dp(20), padding=(0, 0))
        self.clear_under_preview = MDRaisedButton(text="Clear")
        self.clear_under_preview.bind(on_release=self.clear_image)
        self.submit_under_preview = MDRaisedButton(text="Submit", md_bg_color=palette.PRIMARY)
        self.submit_under_preview.bind(on_release=self.go_to_results)
        actions_row.add_widget(self.clear_under_preview)
        actions_row.add_widget(self.submit_under_preview)
        # Hover: subtle overlay for clear, lighten for submit
        self._apply_hover_to_clear(self.clear_under_preview)
        self._apply_hover_to_primary_button(self.submit_under_preview)
        card.add_widget(actions_row)
        return card

    # Legacy helpers removed (canvas rect sync no longer needed with MDCard)

    # --- View switching ---------------------------------------------------------
    def _show_robot_tip(self):
        self.content_container.clear_widgets()
        self.content_container.add_widget(self.robot_tip_card)
        self.center_image.source = ""

    def _show_preview(self, file_path: str):
        self.content_container.clear_widgets()
        self.content_container.add_widget(self.preview_card)
        self.center_image.source = file_path

    # --- Hover helpers ---------------------------------------------------------
    def _lighten(self, rgba, factor=0.12):
        r, g, b, a = rgba
        return (r + (1 - r) * factor, g + (1 - g) * factor, b + (1 - b) * factor, a)

    def _apply_hover_to_primary_button(self, btn: MDRaisedButton):
        normal = getattr(btn, "md_bg_color", palette.PRIMARY)
        hover = self._lighten(normal, 0.14)

        def on_enter(_w):
            try:
                btn.md_bg_color = hover
            except Exception:
                pass

        def on_leave(_w):
            try:
                btn.md_bg_color = normal
            except Exception:
                pass

        attach_hover(btn, on_enter, on_leave)

    def _apply_hover_to_clear(self, btn: MDRaisedButton):
        # Subtle translucent overlay on hover
        normal = getattr(btn, "md_bg_color", (0, 0, 0, 0))
        hover = (0, 0, 0, 0.06)

        def on_enter(_w):
            try:
                btn.md_bg_color = hover
            except Exception:
                pass

        def on_leave(_w):
            try:
                btn.md_bg_color = normal
            except Exception:
                pass

        attach_hover(btn, on_enter, on_leave)

    def _apply_hover_to_round(self, btn: RoundImageButton):
        normal = getattr(btn, "bg_rgba", palette.PRIMARY)
        hover = self._lighten(normal, 0.14)

        def on_enter(_w):
            try:
                btn.set_bg_rgba(hover)
            except Exception:
                pass

        def on_leave(_w):
            try:
                btn.set_bg_rgba(normal)
            except Exception:
                pass

        attach_hover(btn, on_enter, on_leave)

    def _apply_hover_to_toolbar(self, toolbar: TopBar):
        # Apply hover to all action buttons in toolbar (e.g., settings)
        if not hasattr(toolbar, "_actions_box"):
            return
        for child in toolbar._actions_box.children:
            if isinstance(child, MDIconButton):
                # Ensure we can control color directly
                try:
                    child.theme_text_color = "Custom"
                except Exception:
                    pass
                normal_col = getattr(child, "text_color", (0.2, 0.2, 0.2, 1))
                hover_col = palette.PRIMARY

                def on_enter(_w, c=child, col=hover_col):
                    try:
                        c.text_color = col
                    except Exception:
                        pass

                def on_leave(_w, c=child, col=normal_col):
                    try:
                        c.text_color = col
                    except Exception:
                        pass

                attach_hover(child, on_enter, on_leave)
