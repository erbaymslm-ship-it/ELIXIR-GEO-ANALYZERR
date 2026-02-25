from kivy.app import App
from kivy.utils import platform
from components.bluetooth_manager import BluetoothManager

class ElixirApp(App):
    def build(self):
        # Uygulama başlarken Bluetooth izinlerini kontrol et
        if platform == 'android':
            bt_manager = BluetoothManager()
            bt_manager.check_permissions()
        # ... geri kalan kodlar ...
