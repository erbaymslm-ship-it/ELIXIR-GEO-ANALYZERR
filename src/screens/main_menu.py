"""
ELIXIR TECHNOLOGY
Ana Menu Ekrani - Modern Tasarim
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.lang import Builder
from kivy.clock import Clock
from components.bluetooth_manager import BluetoothManager
import os

KV_MAIN_MENU = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<MainMenuScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex('#0A0A0A')
        Rectangle:
            pos: self.pos
            size: self.size

    ScrollView:
        do_scroll_x: False
        bar_width: dp(3)
        bar_color: get_color_from_hex('#FFD700')

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: [15, 10]
            spacing: 8

            BoxLayout:
                size_hint_y: None
                height: dp(22)

                Label:
                    id: battery_label
                    text: root.battery_text
                    size_hint_x: 0.3
                    font_size: '9sp'
                    color: get_color_from_hex('#00E676')
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'

                Widget:

                Label:
                    id: bt_indicator
                    text: root.bt_indicator_text
                    size_hint_x: 0.4
                    font_size: '9sp'
                    color: root.bt_indicator_color
                    text_size: self.size
                    halign: 'right'
                    valign: 'middle'

            Image:
                source: root.logo_source
                size_hint: None, None
                size: dp(55), dp(55)
                pos_hint: {'center_x': 0.5}
                allow_stretch: True

            Label:
                text: "ELIXIR TECHNOLOGY"
                font_size: '18sp'
                bold: True
                color: get_color_from_hex('#FFD700')
                size_hint_y: None
                height: dp(24)
                halign: 'center'

            Label:
                text: "Jeofizik Veri Analiz Sistemi"
                font_size: '9sp'
                color: get_color_from_hex('#8B7500')
                size_hint_y: None
                height: dp(14)
                halign: 'center'

            Widget:
                size_hint_y: None
                height: dp(8)

            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: dp(80)
                padding: [12, 10]
                spacing: 3
                canvas.before:
                    Color:
                        rgba: get_color_from_hex('#1A1A1A')
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [12]
                    Color:
                        rgba: get_color_from_hex('#3D3500')
                    Line:
                        rounded_rectangle: [self.x, self.y, self.width, self.height, 12]
                        width: 1.2
                on_touch_down: root.go_to_underground() if self.collide_point(*args[1].pos) else None

                BoxLayout:
                    spacing: 10
                    Image:
                        source: root.icon_underground
                        size_hint: None, None
                        size: dp(32), dp(32)
                        pos_hint: {'center_y': 0.5}
                        allow_stretch: True
                    BoxLayout:
                        orientation: 'vertical'
                        Label:
                            text: "YER ALTI GORUNTULEME"
                            font_size: '14sp'
                            bold: True
                            color: get_color_from_hex('#FFD700')
                            text_size: self.size
                            halign: 'left'
                            valign: 'bottom'
                        Label:
                            text: "2D Isi Haritasi | 4D Voxel | 10 Filtre"
                            font_size: '9sp'
                            color: get_color_from_hex('#8B7500')
                            text_size: self.size
                            halign: 'left'
                            valign: 'top'

            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: dp(80)
                padding: [12, 10]
                spacing: 3
                canvas.before:
                    Color:
                        rgba: get_color_from_hex('#1A1A1A')
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [12]
                    Color:
                        rgba: get_color_from_hex('#3D3500')
                    Line:
                        rounded_rectangle: [self.x, self.y, self.width, self.height, 12]
                        width: 1.2
                on_touch_down: root.go_to_pointer() if self.collide_point(*args[1].pos) else None

                BoxLayout:
                    spacing: 10
                    Image:
                        source: root.icon_pointer
                        size_hint: None, None
                        size: dp(32), dp(32)
                        pos_hint: {'center_y': 0.5}
                        allow_stretch: True
                    BoxLayout:
                        orientation: 'vertical'
                        Label:
                            text: "POINTER MOD"
                            font_size: '14sp'
                            bold: True
                            color: get_color_from_hex('#FFD700')
                            text_size: self.size
                            halign: 'left'
                            valign: 'bottom'
                        Label:
                            text: "Gercek Zamanli Gosterge | Buzzer"
                            font_size: '9sp'
                            color: get_color_from_hex('#8B7500')
                            text_size: self.size
                            halign: 'left'
                            valign: 'top'

            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: dp(80)
                padding: [12, 10]
                spacing: 3
                canvas.before:
                    Color:
                        rgba: get_color_from_hex('#1A1A1A')
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [12]
                    Color:
                        rgba: get_color_from_hex('#FFD700')
                    Line:
                        rounded_rectangle: [self.x, self.y, self.width, self.height, 12]
                        width: 1.5
                on_touch_down: root.go_to_settings() if self.collide_point(*args[1].pos) else None

                BoxLayout:
                    spacing: 10
                    BoxLayout:
                        orientation: 'vertical'
                        Label:
                            text: "AYARLAR"
                            font_size: '14sp'
                            bold: True
                            color: get_color_from_hex('#FFD700')
                            text_size: self.size
                            halign: 'left'
                            valign: 'bottom'
                        Label:
                            text: "ELIXIR Cihaz Baglanti | Kalibrasyon"
                            font_size: '9sp'
                            color: get_color_from_hex('#8B7500')
                            text_size: self.size
                            halign: 'left'
                            valign: 'top'

            Widget:
                size_hint_y: None
                height: dp(10)

            Label:
                size_hint_y: None
                height: dp(18)
                text: "ELIXIR v0.1"
                font_size: '8sp'
                color: get_color_from_hex('#444444')
                halign: 'center'
'''

Builder.load_string(KV_MAIN_MENU)


class MainMenuScreen(Screen):
    logo_source = StringProperty('')
    icon_underground = StringProperty('')
    icon_pointer = StringProperty('')
    battery_text = StringProperty('')
    bt_indicator_text = StringProperty('BT: Kapali')
    bt_indicator_color = ListProperty([1, 0.32, 0.32, 1])

    def __init__(self, **kwargs):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        logo = os.path.join(assets_dir, 'elixir_logo.png')
        if os.path.exists(logo):
            self.logo_source = logo
        ug = os.path.join(assets_dir, 'icon_underground.png')
        if os.path.exists(ug):
            self.icon_underground = ug
        pt = os.path.join(assets_dir, 'icon_pointer.png')
        if os.path.exists(pt):
            self.icon_pointer = pt
        super(MainMenuScreen, self).__init__(**kwargs)
        self.bluetooth = BluetoothManager.get_shared()

    def on_enter(self):
        self.update_status()
        self._status_event = Clock.schedule_interval(self.update_status, 3.0)

    def on_leave(self):
        if hasattr(self, '_status_event'):
            self._status_event.cancel()

    def update_status(self, *args):
        level = self.bluetooth.get_battery_level()
        if level is not None:
            self.battery_text = f"Pil: %{level}"
        else:
            self.battery_text = ""

        if self.bluetooth.connected:
            self.bt_indicator_text = f"BT: {self.bluetooth.device_name or 'Bagli'}"
            self.bt_indicator_color = get_color_from_hex('#00E676')
        else:
            self.bt_indicator_text = "BT: Kapali"
            self.bt_indicator_color = get_color_from_hex('#FF5252')

    def go_to_underground(self):
        self.manager.current = 'underground'

    def go_to_pointer(self):
        self.manager.current = 'pointer'

    def go_to_settings(self):
        self.manager.current = 'settings'
