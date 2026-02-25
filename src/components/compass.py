from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Triangle, Rectangle
from kivy.graphics.instructions import InstructionGroup
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.utils import get_color_from_hex
from kivy.core.text import Label as CoreLabel
import math
import platform

try:
    from plyer import compass as plyer_compass
    HAS_PLYER_COMPASS = True
except Exception:
    HAS_PLYER_COMPASS = False


class CompassWidget(Widget):
    heading = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CompassWidget, self).__init__(**kwargs)
        self._is_android = platform.system() == 'Linux' and hasattr(platform, 'android_ver')
        self._sensor_enabled = False
        self._demo_angle = 0
        self.bind(pos=self._redraw, size=self._redraw, heading=self._redraw)

        try:
            from android import mActivity
            self._is_android = True
        except Exception:
            self._is_android = False

    def start(self):
        if self._is_android and HAS_PLYER_COMPASS:
            try:
                plyer_compass.enable()
                self._sensor_enabled = True
                self._update_event = Clock.schedule_interval(self._update_heading, 0.1)
            except Exception:
                self._sensor_enabled = False
                self._update_event = Clock.schedule_interval(self._demo_rotation, 1.0 / 30.0)
        else:
            self._update_event = Clock.schedule_interval(self._demo_rotation, 1.0 / 30.0)

    def stop(self):
        if hasattr(self, '_update_event'):
            self._update_event.cancel()
        if self._sensor_enabled and HAS_PLYER_COMPASS:
            try:
                plyer_compass.disable()
            except Exception:
                pass
            self._sensor_enabled = False

    def _update_heading(self, dt):
        if self._sensor_enabled and HAS_PLYER_COMPASS:
            try:
                field = plyer_compass.field
                if field and field[0] is not None and field[1] is not None:
                    angle = math.degrees(math.atan2(field[0], field[1]))
                    if angle < 0:
                        angle += 360
                    self.heading = angle
            except Exception:
                pass

    def _demo_rotation(self, dt):
        self._demo_angle += 0.3
        self.heading = self._demo_angle % 360

    def _redraw(self, *args):
        self.canvas.clear()
        w, h = self.size
        cx = self.x + w / 2
        cy = self.y + h / 2
        radius = min(w, h) / 2 - 10

        if radius <= 0:
            return

        with self.canvas:
            Color(*get_color_from_hex('#1A1A1A'))
            Rectangle(pos=self.pos, size=self.size)

            Color(*get_color_from_hex('#2A2A2A'))
            Ellipse(pos=(cx - radius, cy - radius), size=(radius * 2, radius * 2))

            Color(*get_color_from_hex('#3D3500'))
            Line(circle=(cx, cy, radius), width=1.5)

            Color(*get_color_from_hex('#333333'))
            Line(circle=(cx, cy, radius * 0.7), width=0.8)

            heading_rad = math.radians(self.heading)

            for i in range(360):
                if i % 30 == 0:
                    tick_len = 12
                    tick_w = 1.5
                    Color(*get_color_from_hex('#FFD700'))
                elif i % 10 == 0:
                    tick_len = 8
                    tick_w = 1.0
                    Color(*get_color_from_hex('#666666'))
                else:
                    continue

                angle = math.radians(i) - heading_rad
                x1 = cx + (radius - tick_len) * math.sin(angle)
                y1 = cy + (radius - tick_len) * math.cos(angle)
                x2 = cx + radius * math.sin(angle)
                y2 = cy + radius * math.cos(angle)
                Line(points=[x1, y1, x2, y2], width=tick_w)

            labels = [
                (0, 'K', '#FF4444'),
                (90, 'D', '#CCCCCC'),
                (180, 'G', '#CCCCCC'),
                (270, 'B', '#CCCCCC'),
            ]

            for deg, text, color in labels:
                angle = math.radians(deg) - heading_rad
                lx = cx + (radius - 25) * math.sin(angle)
                ly = cy + (radius - 25) * math.cos(angle)
                core_label = CoreLabel(text=text, font_size=14, bold=True)
                core_label.refresh()
                tex = core_label.texture
                Color(*get_color_from_hex(color))
                Rectangle(texture=tex, pos=(lx - tex.width / 2, ly - tex.height / 2), size=tex.size)

            needle_len = radius * 0.6
            Color(*get_color_from_hex('#FFD700'))
            Triangle(points=[
                cx, cy + needle_len,
                cx - 8, cy - 5,
                cx + 8, cy - 5,
            ])

            Color(*get_color_from_hex('#888888'))
            Triangle(points=[
                cx, cy - needle_len * 0.4,
                cx - 6, cy - 5,
                cx + 6, cy - 5,
            ])

            Color(*get_color_from_hex('#FFD700'))
            Ellipse(pos=(cx - 5, cy - 5), size=(10, 10))

            deg_text = f"{int(self.heading)}°"
            core_label = CoreLabel(text=deg_text, font_size=16, bold=True)
            core_label.refresh()
            tex = core_label.texture
            Color(*get_color_from_hex('#FFD700'))
            Rectangle(texture=tex, pos=(cx - tex.width / 2, self.y + 5), size=tex.size)
