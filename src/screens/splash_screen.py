"""
ELIXIR TECHNOLOGY
Splash Ekrani - Modern Animasyonlu
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty, ListProperty
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle, Line, Ellipse
import math
import os

KV_SPLASH = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex
<SplashScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex('#0A0A0A')
        Rectangle:
            pos: self.pos
            size: self.size

    FloatLayout:
        Image:
            id: logo_img
            source: root.logo_source
            size_hint: None, None
            size: dp(150), dp(150)
            pos_hint: {'center_x': 0.5, 'center_y': 0.55}
            opacity: root.logo_opacity
            allow_stretch: True

        Label:
            id: title_label
            text: "ELIXIR"
            font_size: '42sp'
            bold: True
            color: root.title_color
            opacity: root.title_opacity
            size_hint: None, None
            size: self.texture_size
            pos_hint: {'center_x': 0.5, 'center_y': 0.35}

        Label:
            id: subtitle_label
            text: "TECHNOLOGY"
            font_size: '16sp'
            bold: True
            color: get_color_from_hex('#8B7500')
            opacity: root.subtitle_opacity
            size_hint: None, None
            size: self.texture_size
            pos_hint: {'center_x': 0.5, 'center_y': 0.30}
            letter_spacing: 8

        Label:
            text: "Jeofizik Veri Analiz Sistemi"
            font_size: '12sp'
            color: get_color_from_hex('#666666')
            opacity: root.desc_opacity
            size_hint: None, None
            size: self.texture_size
            pos_hint: {'center_x': 0.5, 'center_y': 0.22}

        Label:
            text: "v0.1"
            font_size: '10sp'
            color: get_color_from_hex('#444444')
            opacity: root.desc_opacity
            size_hint: None, None
            size: self.texture_size
            pos_hint: {'center_x': 0.5, 'center_y': 0.08}
'''

Builder.load_string(KV_SPLASH)


class SplashScreen(Screen):
    logo_opacity = NumericProperty(0)
    title_opacity = NumericProperty(0)
    subtitle_opacity = NumericProperty(0)
    desc_opacity = NumericProperty(0)
    title_color = ListProperty([1, 0.843, 0, 1])
    ring_angle = NumericProperty(0)
    logo_source = ''

    def __init__(self, **kwargs):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        logo_path = os.path.join(assets_dir, 'elixir_logo.png')
        if os.path.exists(logo_path):
            self.logo_source = logo_path
        super(SplashScreen, self).__init__(**kwargs)

    def on_enter(self):
        anim_logo = Animation(logo_opacity=1, duration=0.8, t='out_quad')
        anim_logo.start(self)

        Clock.schedule_once(lambda dt: Animation(title_opacity=1, duration=0.6, t='out_quad').start(self), 0.4)
        Clock.schedule_once(lambda dt: Animation(subtitle_opacity=1, duration=0.6, t='out_quad').start(self), 0.8)
        Clock.schedule_once(lambda dt: Animation(desc_opacity=1, duration=0.6, t='out_quad').start(self), 1.2)

        Clock.schedule_once(self._start_glow, 1.5)
        Clock.schedule_once(self._go_to_main_menu, 3.5)

    def _start_glow(self, dt):
        glow = (
            Animation(title_color=[1, 0.95, 0.4, 1], duration=0.5) +
            Animation(title_color=[1, 0.843, 0, 1], duration=0.5)
        )
        glow.repeat = True
        glow.start(self)

    def _go_to_main_menu(self, dt):
        self.manager.current = 'main_menu'
