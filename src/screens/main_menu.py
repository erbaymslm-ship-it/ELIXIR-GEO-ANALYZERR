"""
ELIXIR TECHNOLOGY
Ana Menü Ekranı
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.lang import Builder

KV_MAIN_MENU = '''
<MainMenuScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex('#1a1a2e')
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        padding: [20, 50]
        spacing: 30
        
        Label:
            text: "ELIXIR TECHNOLOGY"
            font_size: '28sp'
            bold: True
            color: get_color_from_hex('#4ecca3')
            size_hint_y: 0.3
        
        BoxLayout:
            orientation: 'vertical'
            spacing: 20
            size_hint_y: 0.5
            
            Button:
                text: "YER ALTI GÖRÜNTÜLEME"
                font_size: '18sp'
                background_normal: ''
                background_color: get_color_from_hex('#16213e')
                color: get_color_from_hex('#ffffff')
                on_press: root.go_to_underground()
                size_hint_y: 0.4
            
            Button:
                text: "POINTER MOD"
                font_size: '18sp'
                background_normal: ''
                background_color: get_color_from_hex('#0f3460')
                color: get_color_from_hex('#ffffff')
                on_press: root.go_to_pointer()
                size_hint_y: 0.4
'''

Builder.load_string(KV_MAIN_MENU)

class MainMenuScreen(Screen):
    """
    Ana menü ekranı
    """
    
    def go_to_underground(self):
        """Yer altı görüntüleme moduna geç"""
        self.manager.current = 'underground'
    
    def go_to_pointer(self):
        """Pointer moduna geç"""
        self.manager.current = 'pointer'