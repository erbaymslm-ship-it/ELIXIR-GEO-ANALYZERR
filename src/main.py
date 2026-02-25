"""
ELIXIR TECHNOLOGY
Ana Uygulama Giris Noktasi
"""

__version__ = '0.1'

import os
import sys

os.environ['KIVY_NO_CONSOLELOG'] = '0'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivy.logger import Logger
from kivy.clock import Clock

if platform != 'android':
    Window.size = (400, 700)

from screens.splash_screen import SplashScreen
from screens.main_menu import MainMenuScreen
from screens.underground import UndergroundScreen
from screens.pointer import PointerScreen
from screens.settings_screen import SettingsScreen
from components.bluetooth_manager import BluetoothManager


class ElixirApp(App):
    title = "ELIXIR TECHNOLOGY"

    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(UndergroundScreen(name='underground'))
        sm.add_widget(PointerScreen(name='pointer'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

    def on_start(self):
        bt = BluetoothManager.get_shared()
        if platform == 'android':
            bt.request_permissions(callback=self._on_permissions_result)
        else:
            Clock.schedule_once(self._try_auto_connect, 4.0)

    def _on_permissions_result(self, granted):
        Logger.info(f"Izinler verildi: {granted}")
        Clock.schedule_once(self._try_auto_connect, 2.0)

    def _try_auto_connect(self, dt):
        bt = BluetoothManager.get_shared()
        bt.try_auto_connect()


if __name__ == '__main__':
    ElixirApp().run()
