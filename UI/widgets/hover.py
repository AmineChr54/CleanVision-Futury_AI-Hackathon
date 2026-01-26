from kivy.core.window import Window
from kivy.clock import Clock

# Simple hover attachment utility.
# Polls mouse position; if inside widget bounds triggers on_enter/on_leave.
# NOTE: Kivy doesn't have native hover events on all platforms.


def attach_hover(widget, on_enter, on_leave, interval=0.15):
    state = {"inside": False}

    def _check(*_):
        mx, my = Window.mouse_pos
        wx, wy = widget.to_widget(mx, my)
        inside = widget.collide_point(wx, wy)
        if inside and not state["inside"]:
            state["inside"] = True
            on_enter(widget)
        elif not inside and state["inside"]:
            state["inside"] = False
            on_leave(widget)

    Clock.schedule_interval(_check, interval)
    return widget
