# -*- coding: utf-8 -*-
import time
from kivy.logger import Logger
from kivy.utils import platform
from plyer import bluetooth

# Android'e özel izin yönetimi
if platform == 'android':
    from android.permissions import request_permissions, Permission, check_permission
    from android import api_version

class BluetoothManager:
    def __init__(self):
        self.connected_device = None
        self.socket = None
        self.buffer = b''

    def check_permissions(self):
        """Android'de Bluetooth izinlerini kontrol et ve iste."""
        if platform != 'android':
            return True

        # Android 12+ (API 31+) için yeni izinler
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

        # İzinleri iste (asenkron, hemen döner)
        request_permissions(permissions)
        
        # İzinlerin verilip verilmediğini kontrol et (kısa bir bekleme ile)
        time.sleep(0.5)  # izin dialogunun görünmesi için kısa bekleme
        for perm in permissions:
            if not check_permission(perm):
                Logger.warning(f"BluetoothManager: {perm} izni verilmemiş!")
                return False
        return True

    def get_paired_devices(self):
        """Eşleştirilmiş cihazların listesini döndürür."""
        if platform == 'android' and not self.check_permissions():
            return []
        try:
            devices = bluetooth.get_paired_devices()
            return devices
        except Exception as e:
            Logger.error(f"BluetoothManager: Cihazlar alınamadı - {e}")
            return []

    def connect(self, address, uuid="00001101-0000-1000-8000-00805f9b34fb"):
        """
        Belirtilen adrese (MAC) ve UUID'ye göre Bluetooth bağlantısı kurar.
        UUID: SPP (Serial Port Profile) için standart UUID.
        """
        if platform == 'android' and not self.check_permissions():
            Logger.error("BluetoothManager: İzinler yok, bağlantı kurulamaz.")
            return False

        try:
            device = bluetooth.get_device(address)
            if not device:
                Logger.error(f"BluetoothManager: {address} adresinde cihaz bulunamadı.")
                return False

            # Socket oluştur ve bağlan
            self.socket = device.create_rfcomm_socket(uuid)
            self.socket.connect()
            self.connected_device = device
            Logger.info(f"BluetoothManager: {address} bağlantı başarılı.")
            return True
        except Exception as e:
            Logger.error(f"BluetoothManager: Bağlantı hatası - {e}")
            return False

    def disconnect(self):
        """Bağlantıyı kapat."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.connected_device = None
            Logger.info("BluetoothManager: Bağlantı kapatıldı.")

    def send(self, data):
        """Veri gönder (string veya bytes)."""
        if not self.socket:
            Logger.error("BluetoothManager: Bağlantı yok, gönderilemez.")
            return False
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            self.socket.send(data)
            return True
        except Exception as e:
            Logger.error(f"BluetoothManager: Gönderme hatası - {e}")
            return False

    def receive(self, num_bytes=1024):
        """Veri al. Gelen veriyi tamponda biriktirir, satır satır döndürür."""
        if not self.socket:
            return None
        try:
            data = self.socket.recv(num_bytes)
            if not data:
                return None
            self.buffer += data
            # Satır sonu ('\n') gelene kadar bekle, sonra satırları ayır
            if b'\n' in self.buffer:
                lines = self.buffer.split(b'\n')
                # Son satır eksik olabilir, tamponda bırak
                self.buffer = lines[-1]
                for line in lines[:-1]:
                    if line:
                        yield line.decode('utf-8', errors='replace')
        except Exception as e:
            Logger.error(f"BluetoothManager: Alma hatası - {e}")
            return None

    def is_connected(self):
        return self.socket is not None
