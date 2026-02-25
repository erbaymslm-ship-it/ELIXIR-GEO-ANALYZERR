# bluetooth_manager.py

from kivy.utils import platform
from kivy.logger import Logger
import time

# Android'e özel izin kütüphanesi
if platform == 'android':
    from android.permissions import request_permissions, check_permission, Permission
    from android import api_version
    from jnius import autoclass

    # Android Bluetooth sınıfları
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    UUID = autoclass('java.util.UUID')
else:
    # Diğer platformlar için sahte sınıflar (opsiyonel)
    BluetoothAdapter = None
    BluetoothDevice = None
    UUID = None

class BluetoothManager:
    def __init__(self):
        self.adapter = None
        self.device = None
        self.socket = None
        self.connected = False

    def check_permissions(self):
        """Android'de izinleri kontrol et ve iste."""
        if platform != 'android':
            return True

        # Android 12+ için farklı izinler
        if api_version >= 31:
            permissions = [
                Permission.BLUETOOTH_SCAN,
                Permission.BLUETOOTH_CONNECT,
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION
            ]
        else:
            permissions = [
                Permission.BLUETOOTH,
                Permission.BLUETOOTH_ADMIN,
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION
            ]

        # İzinleri iste
        request_permissions(permissions)
        
        # İzinlerin verilip verilmediğini kontrol et (basit)
        for p in permissions:
            if not check_permission(p):
                Logger.warning(f"BluetoothManager: {p} izni verilmemiş!")
                return False
        return True

    def enable_bluetooth(self):
        """Bluetooth'u aç (kullanıcı onayı gerektirebilir)."""
        if platform != 'android':
            return False
        adapter = BluetoothAdapter.getDefaultAdapter()
        if not adapter.isEnabled():
            # Kullanıcıya Bluetooth açma isteği gönder
            adapter.enable()  # Bu direkt açar, bazı cihazlarda çalışmaz; intent kullanmak daha iyi
            # Alternatif: Intent ile açma (daha karmaşık)
            return False
        return True

    def connect(self, mac_address):
        """Belirtilen MAC adresine bağlan."""
        if not self.check_permissions():
            Logger.error("BluetoothManager: İzinler yok, bağlanılamıyor")
            return False

        if platform != 'android':
            Logger.error("BluetoothManager: Sadece Android'de çalışır")
            return False

        adapter = BluetoothAdapter.getDefaultAdapter()
        if not adapter:
            Logger.error("BluetoothManager: Bluetooth adaptörü yok")
            return False

        if not adapter.isEnabled():
            Logger.info("BluetoothManager: Bluetooth kapalı, açılıyor...")
            # Basitçe açmayı dene (kullanıcı onayı gerekebilir)
            adapter.enable()
            time.sleep(2)  # açılmasını bekle

        # Cihazı al
        device = adapter.getRemoteDevice(mac_address)
        if not device:
            Logger.error(f"BluetoothManager: {mac_address} adresinde cihaz bulunamadı")
            return False

        # UUID (SPP için standart UUID)
        spp_uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
        
        try:
            # Socket oluştur ve bağlan
            socket = device.createRfcommSocketToServiceRecord(spp_uuid)
            socket.connect()
            self.socket = socket
            self.device = device
            self.connected = True
            Logger.info(f"BluetoothManager: {mac_address} bağlantı başarılı")
            return True
        except Exception as e:
            Logger.error(f"BluetoothManager: Bağlantı hatası: {e}")
            return False

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False

    def send(self, data):
        if not self.connected or not self.socket:
            return False
        try:
            self.socket.getOutputStream().write(data.encode())
            return True
        except Exception as e:
            Logger.error(f"BluetoothManager: Gönderme hatası: {e}")
            return False

    def receive(self, buffer_size=1024):
        if not self.connected or not self.socket:
            return None
        try:
            input_stream = self.socket.getInputStream()
            if input_stream.available() > 0:
                data = input_stream.read(buffer_size)
                return data
            return None
        except Exception as e:
            Logger.error(f"BluetoothManager: Okuma hatası: {e}")
            return None
