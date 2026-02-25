"""
ELIXIR TECHNOLOGY
Pointer Modu - Modern Tasarim
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.animation import Animation
from kivy.lang import Builder
from components.bluetooth_manager import BluetoothManager
from components.sound_manager import SoundManager
import math
import threading
import os

KV_POINTER = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex
<PointerScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex('#0A0A0A')
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        spacing: 5

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            padding: [10, 5]
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#141414')
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: "<"
                size_hint_x: None
                width: dp(35)
                background_normal: ''
                background_color: get_color_from_hex('#1A1A1A')
                color: get_color_from_hex('#FFD700')
                font_size: '16sp'
                on_press: root.go_back()

            Label:
                id: battery_label
                text: root.battery_text
                size_hint_x: None
                width: dp(55)
                font_size: '9sp'
                color: get_color_from_hex('#00E676')

            Label:
                text: "POINTER MOD"
                font_size: '14sp'
                bold: True
                color: get_color_from_hex('#FFD700')

            Image:
                source: root.icon_pointer
                size_hint: None, None
                size: dp(24), dp(24)
                pos_hint: {'center_y': 0.5}
                allow_stretch: True

        BoxLayout:
            size_hint_y: None
            height: dp(28)
            padding: [10, 2]
            spacing: 8
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#0F0F0F')
                Rectangle:
                    pos: self.pos
                    size: self.size

            Image:
                source: root.icon_bluetooth
                size_hint: None, None
                size: dp(16), dp(16)
                pos_hint: {'center_y': 0.5}
                allow_stretch: True

            Label:
                id: bt_status
                text: "Bluetooth: Bagli degil"
                color: get_color_from_hex('#FF5252')
                font_size: '10sp'
                text_size: self.size
                halign: 'left'
                valign: 'middle'

        PointerGauge:
            id: gauge
            size_hint_y: 0.55
            value: root.current_value

        BoxLayout:
            size_hint_y: 0.3
            orientation: 'vertical'
            padding: [15, 5]
            spacing: 8

            BoxLayout:
                size_hint_y: 0.5
                padding: [10, 10]
                spacing: 10
                canvas.before:
                    Color:
                        rgba: get_color_from_hex('#1A1A1A')
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [10]
                    Color:
                        rgba: get_color_from_hex('#3D3500')
                    Line:
                        rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                        width: 1

                BoxLayout:
                    orientation: 'vertical'
                    spacing: 2

                    Label:
                        text: "DEGER"
                        font_size: '9sp'
                        color: get_color_from_hex('#8B7500')

                    Label:
                        text: str(root.current_value)
                        font_size: '28sp'
                        bold: True
                        color: root.get_text_color()

                BoxLayout:
                    orientation: 'vertical'
                    spacing: 2

                    Label:
                        text: "DURUM"
                        font_size: '9sp'
                        color: get_color_from_hex('#8B7500')

                    Label:
                        text: root.get_status_text()
                        font_size: '20sp'
                        bold: True
                        color: root.get_text_color()

            BoxLayout:
                size_hint_y: 0.3
                padding: [5, 0]
                spacing: 5

                Label:
                    text: "0"
                    size_hint_x: 0.08
                    color: get_color_from_hex('#448AFF')
                    font_size: '9sp'

                ProgressBar:
                    id: intensity_bar
                    max: 1023
                    value: root.current_value

                Label:
                    text: "1023"
                    size_hint_x: 0.1
                    color: get_color_from_hex('#FF5252')
                    font_size: '9sp'

            Label:
                text: "Bluetooth uzerinden canli sensor verisi"
                font_size: '9sp'
                color: get_color_from_hex('#444444')
                size_hint_y: 0.2
'''

Builder.load_string(KV_POINTER)


class PointerGauge(Widget):
    value = NumericProperty(0)
    pulse_scale = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super(PointerGauge, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.bind(value=self.update_canvas)
        self.animate_pulse()

    def animate_pulse(self):
        anim = Animation(pulse_scale=1.08, duration=0.6) + Animation(pulse_scale=1.0, duration=0.6)
        anim.repeat = True
        anim.start(self)

    def update_canvas(self, *args):
        self.canvas.clear()

        with self.canvas:
            Color(*get_color_from_hex('#0A0A0A'))
            Rectangle(pos=self.pos, size=self.size)

            cx = self.center_x
            cy = self.center_y
            radius = min(self.width, self.height) * 0.38
            scaled_radius = radius * self.pulse_scale

            r, g, b = self.get_color_for_value(self.value)

            Color(r, g, b, 0.08)
            Ellipse(
                pos=(cx - scaled_radius * 1.2, cy - scaled_radius * 1.2),
                size=(scaled_radius * 2.4, scaled_radius * 2.4)
            )

            Color(*get_color_from_hex('#1A1A1A'))
            Ellipse(
                pos=(cx - radius, cy - radius),
                size=(radius * 2, radius * 2)
            )

            Color(*get_color_from_hex('#3D3500'), 0.5)
            Line(circle=(cx, cy, radius), width=2)

            num_ticks = 24
            for i in range(num_ticks):
                angle = i * (360 / num_ticks) - 90
                inner_r = radius * 0.88
                outer_r = radius * 0.95
                if i % 6 == 0:
                    inner_r = radius * 0.82
                    Color(*get_color_from_hex('#FFD700'), 0.7)
                else:
                    Color(*get_color_from_hex('#3D3500'), 0.4)

                x1 = cx + math.cos(math.radians(angle)) * inner_r
                y1 = cy + math.sin(math.radians(angle)) * inner_r
                x2 = cx + math.cos(math.radians(angle)) * outer_r
                y2 = cy + math.sin(math.radians(angle)) * outer_r
                Line(points=[x1, y1, x2, y2], width=1.2)

            Color(r, g, b, 0.15)
            sweep_angle = (self.value / 1023) * 360
            Ellipse(
                pos=(cx - radius * 0.75, cy - radius * 0.75),
                size=(radius * 1.5, radius * 1.5),
                angle_start=0, angle_end=sweep_angle
            )

            Color(*get_color_from_hex('#0F0F0F'))
            core_r = radius * 0.35
            Ellipse(
                pos=(cx - core_r, cy - core_r),
                size=(core_r * 2, core_r * 2)
            )

            angle = (self.value / 1023) * 360 - 90
            needle_len = radius * 0.75
            end_x = cx + math.cos(math.radians(angle)) * needle_len
            end_y = cy + math.sin(math.radians(angle)) * needle_len

            Color(r, g, b, 0.9)
            Line(points=[cx, cy, end_x, end_y], width=2.5)

            Color(r, g, b, 0.4)
            glow_r = 6
            Ellipse(
                pos=(end_x - glow_r, end_y - glow_r),
                size=(glow_r * 2, glow_r * 2)
            )

            Color(*get_color_from_hex('#FFD700'))
            dot_r = 4
            Ellipse(pos=(cx - dot_r, cy - dot_r), size=(dot_r * 2, dot_r * 2))

    def get_color_for_value(self, value):
        if value < 341:
            t = value / 340
            return (0.1 + t * 0.15, 0.3 + t * 0.4, 0.8 - t * 0.2)
        elif value < 682:
            t = (value - 341) / 340
            return (0.1 + t * 0.8, 0.7 - t * 0.2, 0.3 - t * 0.3)
        else:
            t = (value - 682) / 341
            return (0.9 + t * 0.1, 0.3 - t * 0.3, 0.0)


class PointerScreen(Screen):
    current_value = NumericProperty(0)
    icon_pointer = StringProperty('')
    icon_bluetooth = StringProperty('')
    battery_text = StringProperty('')

    def __init__(self, **kwargs):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        for attr, fname in [
            ('icon_pointer', 'icon_pointer.png'),
            ('icon_bluetooth', 'icon_bluetooth.png'),
        ]:
            path = os.path.join(assets_dir, fname)
            if os.path.exists(path):
                setattr(self, attr, path)

        super(PointerScreen, self).__init__(**kwargs)

        self.bluetooth = BluetoothManager.get_shared()
        self.bluetooth.data_callback = self.on_data_received
        self.sound = SoundManager.get_instance()
        self._beep_scheduled = None

        Clock.schedule_interval(self.update_ui, 0.05)

    def on_enter(self):
        self.update_bluetooth_status()
        self.update_battery()
        self._beep_scheduled = Clock.schedule_interval(self._continuous_beep, 0.4)

    def on_leave(self):
        if self._beep_scheduled:
            self._beep_scheduled.cancel()
            self._beep_scheduled = None

    def _continuous_beep(self, dt):
        if self.bluetooth.connected and self.current_value > 0:
            self.sound.play_beep_for_value(abs(self.current_value))

    def update_ui(self, dt):
        if hasattr(self.ids, 'gauge'):
            self.ids.gauge.value = self.current_value
        if hasattr(self.ids, 'intensity_bar'):
            self.ids.intensity_bar.value = max(0, self.current_value)

    def update_bluetooth_status(self):
        if hasattr(self.ids, 'bt_status'):
            if self.bluetooth.connected:
                name = self.bluetooth.device_name or 'Bagli'
                self.ids.bt_status.text = f"BT: {name}"
                self.ids.bt_status.color = get_color_from_hex('#00E676')
            else:
                self.ids.bt_status.text = "BT: Bagli degil"
                self.ids.bt_status.color = get_color_from_hex('#FF5252')

    def update_battery(self):
        level = self.bluetooth.get_battery_level()
        if level is not None:
            self.battery_text = f"Pil:%{level}"
        else:
            self.battery_text = ""

    def on_data_received(self, value):
        self.current_value = value

    def get_text_color(self):
        if self.current_value < 341:
            return get_color_from_hex('#448AFF')
        elif self.current_value < 682:
            return get_color_from_hex('#00E676')
        else:
            return get_color_from_hex('#FF5252')

    def get_status_text(self):
        if self.current_value < 341:
            return "DUSUK"
        elif self.current_value < 682:
            return "ORTA"
        else:
            return "YUKSEK"

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, color=get_color_from_hex('#E0E0E0'), font_size='13sp'),
            size_hint=(0.7, 0.3),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700')
        )
        popup.open()

    def go_back(self):
        if self._beep_scheduled:
            self._beep_scheduled.cancel()
            self._beep_scheduled = None
        self.manager.current = 'main_menu'
