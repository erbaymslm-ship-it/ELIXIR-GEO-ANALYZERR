"""
ELIXIR TECHNOLOGY
Splash Ekranı
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, NumericProperty
from kivy.lang import Builder
import os

# KV string for splash screen
KV_SPLASH = '''
<SplashScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex('#000000')
        Rectangle:
            pos: self.pos
            size: self.size
    
    FloatLayout:
        Label:
            text: "ELIXIR TECHNOLOGY"
            font_size: '24sp'
            bold: True
            color: get_color_from_hex('#FFFFFF')
            opacity: root.label_opacity
            size_hint: None, None
            size: self.texture_size
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
'''

Builder.load_string(KV_SPLASH)

class SplashScreen(Screen):
    """
    Splash ekranı - 3 saniye fade animasyonu ile
    """
    
    label_opacity = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        self._keyboard = None
    
    def on_enter(self):
        """Ekrana girildiğinde"""
        # Fade in animasyonu
        anim = Animation(label_opacity=1, duration=1.5)
        anim.bind(on_complete=self._on_fade_in_complete)
        anim.start(self)
    
    def _on_fade_in_complete(self, *args):
        """Fade in tamamlandı"""
        # 1.5 saniye bekle (toplam 3 saniye)
        Clock.schedule_once(self._go_to_main_menu, 1.5)
    
    def _go_to_main_menu(self, dt):
        """Ana menüye geç"""
        self.manager.current = 'main_menu'