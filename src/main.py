"""
ELIXIR TECHNOLOGY
Ana Uygulama Dosyası
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from screens.splash_screen import SplashScreen
from screens.main_menu import MainMenuScreen
from screens.underground import UndergroundScreen
from screens.pointer import PointerScreen

# Pencere boyutu (sadece geliştirme için)
if platform == 'win' or platform == 'linux':
    Window.size = (400, 700)

class ElixirApp(App):
    """
    Ana uygulama sınıfı
    """
    
    def build(self):
        self.title = "ELIXIR TECHNOLOGY"
        self.icon = 'assets/icons/app_icon.png'
        
        # Screen manager oluştur
        sm = ScreenManager()
        
        # Ekranları ekle
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(UndergroundScreen(name='underground'))
        sm.add_widget(PointerScreen(name='pointer'))
        
        return sm
    
    def on_pause(self):
        """Uygulama arka plana alındığında"""
        return True
    
    def on_resume(self):
        """Uygulama ön plana alındığında"""
        pass

if __name__ == '__main__':
    ElixirApp().run()