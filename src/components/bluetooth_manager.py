"""
ELIXIR TECHNOLOGY
Bluetooth Classic Yönetimi
"""

from kivy.utils import platform
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty
from kivy.event import EventDispatcher
import threading
import time

# Platform kontrolü
if platform == 'android':
    from android.permissions import request_permissions, Permission
    import usb4a
    import usbserial
    import jnius
else:
    # Geliştirme ortamı için mock
    class MockBluetooth:
        def __init__(self):
            self.devices = []
    import sys
    sys.modules['android'] = type('android', (), {})

class BluetoothManager(EventDispatcher):
    """
    Bluetooth Classic bağlantı yöneticisi
    """
    
    connected = BooleanProperty(False)
    devices = ListProperty([])
    current_data = ObjectProperty(None, allownone=True)
    
    def __init__(self, **kwargs):
        super(BluetoothManager, self).__init__(**kwargs)
        self._socket = None
        self._thread = None
        self._running = False
        self.data_callback = None
        self._buffer = ""
        
        # Android izinleri
        if platform == 'android':
            self._request_permissions()
    
    def _request_permissions(self):
        """Android izinlerini iste"""
        if platform == 'android':
            permissions = [
                Permission.BLUETOOTH,
                Permission.BLUETOOTH_ADMIN,
                Permission.BLUETOOTH_SCAN,
                Permission.BLUETOOTH_CONNECT,
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION
            ]
            request_permissions(permissions)
    
    def scan_devices(self):
        """Bluetooth cihazlarını tara"""
        self.devices = []
        
        if platform == 'android':
            try:
                PythonBluetooth = jnius.autoclass('android.bluetooth.BluetoothAdapter')
                BluetoothDevice = jnius.autoclass('android.bluetooth.BluetoothDevice')
                
                adapter = PythonBluetooth.getDefaultAdapter()
                
                if adapter and adapter.isEnabled():
                    # Eşleştirilmiş cihazları al
                    bonded_devices = adapter.getBondedDevices().toArray()
                    
                    for device in bonded_devices:
                        device_info = {
                            'name': device.getName(),
                            'address': device.getAddress(),
                            'type': 'bonded'
                        }
                        self.devices.append(device_info)
                        Logger.info(f"Bluetooth: Cihaz bulundu - {device_info['name']}")
            except Exception as e:
                Logger.error(f"Bluetooth tarama hatası: {e}")
        
        return self.devices
    
    def connect(self, address):
        """Bluetooth cihazına bağlan"""
        if platform == 'android':
            try:
                # UUID for Serial Port Profile (SPP)
                UUID = jnius.autoclass('java.util.UUID')
                spp_uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
                
                PythonBluetooth = jnius.autoclass('android.bluetooth.BluetoothAdapter')
                adapter = PythonBluetooth.getDefaultAdapter()
                
                device = adapter.getRemoteDevice(address)
                
                # Socket oluştur ve bağlan
                self._socket = device.createRfcommSocketToServiceRecord(spp_uuid)
                self._socket.connect()
                
                self.connected = True
                Logger.info(f"Bluetooth: {address} bağlandı")
                
                # Veri dinlemeyi başlat
                self._start_listening()
                
                return True
                
            except Exception as e:
                Logger.error(f"Bluetooth bağlantı hatası: {e}")
                self.connected = False
                return False
        else:
            # Geliştirme ortamında mock bağlantı
            Logger.info("Geliştirme modu: Mock Bluetooth bağlantısı")
            self.connected = True
            self._start_mock_data()
            return True
    
    def disconnect(self):
        """Bluetooth bağlantısını kes"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
        
        self.connected = False
        Logger.info("Bluetooth: Bağlantı kesildi")
    
    def _start_listening(self):
        """Veri dinlemeyi başlat"""
        self._running = True
        self._thread = threading.Thread(target=self._listen_thread)
        self._thread.daemon = True
        self._thread.start()
    
    def _listen_thread(self):
        """Bluetooth veri dinleme thread'i"""
        if platform == 'android' and self._socket:
            try:
                input_stream = self._socket.getInputStream()
                
                while self._running:
                    if input_stream.available() > 0:
                        data = input_stream.read()
                        if data != -1:
                            self._process_data(chr(data))
                    time.sleep(0.01)
                    
            except Exception as e:
                Logger.error(f"Bluetooth okuma hatası: {e}")
                self.connected = False
    
    def _process_data(self, char):
        """Gelen veriyi işle (satır satır integer)"""
        if char == '\n':
            if self._buffer.strip():
                try:
                    value = int(self._buffer.strip())
                    Clock.schedule_once(lambda dt: self._on_data_received(value))
                except ValueError:
                    Logger.warning(f"Geçersiz veri: {self._buffer}")
                self._buffer = ""
        else:
            self._buffer += char
    
    def _on_data_received(self, value):
        """Veri alındığında callback"""
        self.current_data = value
        if self.data_callback:
            self.data_callback(value)
    
    def _start_mock_data(self):
        """Geliştirme için mock veri üret"""
        import random
        
        def generate_mock(dt):
            if self._running:
                value = random.randint(0, 1023)
                self._on_data_received(value)
                return True
            return False
        
        Clock.schedule_interval(generate_mock, 0.5)