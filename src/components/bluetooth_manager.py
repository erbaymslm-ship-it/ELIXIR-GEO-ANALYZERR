# -*- coding: utf-8 -*-
"""
Bluetooth Manager - ELIXIR GEO ANALYZER
Android için Bluetooth bağlantı yönetimi, izinler ve veri okuma
"""

import time
import threading
from kivy.logger import Logger
from kivy.utils import platform
from kivy.clock import Clock

# Platforma göre import'lar
if platform == 'android':
    from android import BluetoothAdapter, BluetoothDevice
    from android.permissions import request_permissions, Permission
    from android import api_version
else:
    # Android dışı platformlar için sahte sınıflar (opsiyonel)
    BluetoothAdapter = None
    BluetoothDevice = None
    Permission = None
    request_permissions = None
    api_version = 0


class BluetoothManager:
    """
    Bluetooth bağlantılarını yönetir, cihazları tarar, veri okur.
    """

    def __init__(self):
        self.adapter = None
        self.device = None
        self.socket = None
        self.is_connected = False
        self.is_scanning = False
        self.devices_found = []
        self.callback_on_data = None
        self.callback_on_device_found = None
        self.read_thread = None
        self.running = False

        if platform == 'android':
            self._init_android_adapter()

    def _init_android_adapter(self):
        """Android Bluetooth adaptörünü al"""
        try:
            self.adapter = BluetoothAdapter.getDefaultAdapter()
            if not self.adapter:
                Logger.error("BluetoothManager: Bu cihazda Bluetooth yok.")
        except Exception as e:
            Logger.error(f"BluetoothManager: Adaptör alınamadı: {e}")

    # -------------------------------------------------------------------------
    # İzin yönetimi (Android)
    # -------------------------------------------------------------------------
    def check_and_request_permissions(self, callback=None):
        """
        Bluetooth için gerekli izinleri kontrol eder ve ister.
        callback: İzinler verildikten sonra çağrılacak fonksiyon
        """
        if platform != 'android':
            if callback:
                callback(True)
            return True

        # Android 12+ (API 31+) için yeni izinler
        if api_version >= 31:
            permissions = [
                Permission.BLUETOOTH_SCAN,
                Permission.BLUETOOTH_CONNECT,
                Permission.ACCESS_FINE_LOCATION
            ]
        else:
            permissions = [
                Permission.BLUETOOTH,
                Permission.BLUETOOTH_ADMIN,
                Permission.ACCESS_FINE_LOCATION
            ]

        def on_permissions(permissions, grants):
            all_granted = all(grants)
            if all_granted:
                Logger.info("BluetoothManager: Tüm izinler verildi.")
            else:
                Logger.warning("BluetoothManager: Bazı izinler verilmedi.")
            if callback:
                callback(all_granted)

        request_permissions(permissions, on_permissions)
        return False  # İzinler hemen verilmemiş olabilir

    # -------------------------------------------------------------------------
    # Bluetooth açık mı?
    # -------------------------------------------------------------------------
    def is_bluetooth_enabled(self):
        """Bluetooth'un açık olup olmadığını döndürür."""
        if platform != 'android':
            return False
        if not self.adapter:
            return False
        return self.adapter.isEnabled()

    def enable_bluetooth(self):
        """Bluetooth'u açar (kullanıcı onayı gerekebilir)."""
        if platform != 'android':
            return False
        if not self.adapter:
            return False
        if not self.adapter.isEnabled():
            # Android'de kullanıcıdan izin ister
            self.adapter.enable()
            return True
        return True

    # -------------------------------------------------------------------------
    # Cihaz tarama
    # -------------------------------------------------------------------------
    def start_scan(self, duration=12):
        """
        Bluetooth cihazlarını taramaya başlar.
        duration: saniye cinsinden tarama süresi
        """
        if platform != 'android':
            Logger.warning("BluetoothManager: Tarama sadece Android'de desteklenir.")
            return

        if not self.adapter:
            Logger.error("BluetoothManager: Adaptör yok.")
            return

        if not self.is_bluetooth_enabled():
            Logger.warning("BluetoothManager: Bluetooth kapalı, önce açın.")
            return

        self.is_scanning = True
        self.devices_found = []

        # BroadcastReceiver ile cihaz bulunduğunda çağrılacak
        from android.broadcast import BroadcastReceiver

        def on_device_found(context, intent):
            device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
            if device and device.getName():
                name = device.getName()
                address = device.getAddress()
                if address not in [d['address'] for d in self.devices_found]:
                    self.devices_found.append({
                        'name': name,
                        'address': address,
                        'device': device
                    })
                    Logger.info(f"BluetoothManager: Cihaz bulundu {name} [{address}]")
                    if self.callback_on_device_found:
                        self.callback_on_device_found(name, address)

        self.receiver = BroadcastReceiver(
            on_device_found,
            actions=[BluetoothDevice.ACTION_FOUND]
        )
        self.receiver.start()

        # Taramayı başlat
        self.adapter.startDiscovery()

        # Belirtilen süre sonra taramayı durdur
        Clock.schedule_once(lambda dt: self.stop_scan(), duration)

    def stop_scan(self):
        """Tarama işlemini durdurur."""
        if platform != 'android':
            return
        if self.is_scanning and self.adapter:
            self.adapter.cancelDiscovery()
            if hasattr(self, 'receiver'):
                self.receiver.stop()
            self.is_scanning = False
            Logger.info("BluetoothManager: Tarama durduruldu.")

    # -------------------------------------------------------------------------
    # Bağlantı kurma
    # -------------------------------------------------------------------------
    def connect(self, address, uuid='00001101-0000-1000-8000-00805F9B34FB'):
        """
        Belirtilen MAC adresine ve UUID'ye göre cihaza bağlanır.
        Varsayılan UUID: SPP (Serial Port Profile)
        """
        if platform != 'android':
            Logger.error("BluetoothManager: Bağlantı sadece Android'de çalışır.")
            return False

        if not self.adapter:
            Logger.error("BluetoothManager: Adaptör yok.")
            return False

        # Önce izinleri kontrol et (zaten verilmiş olmalı)
        self.check_and_request_permissions()

        try:
            # Cihazı al
            device = self.adapter.getRemoteDevice(address)
            if not device:
                Logger.error(f"BluetoothManager: {address} adresinde cihaz bulunamadı.")
                return False

            # UUID'yi java.util.UUID'ye çevir
            from java import jclass
            UUID = jclass('java.util.UUID')
            sock_uuid = UUID.fromString(uuid)

            # RFCOMM soketi oluştur
            self.socket = device.createRfcommSocketToServiceRecord(sock_uuid)

            # Bağlan
            Logger.info(f"BluetoothManager: {address} adresine bağlanıyor...")
            self.socket.connect()
            self.is_connected = True
            self.device = device
            Logger.info("BluetoothManager: Bağlantı başarılı!")

            # Veri okuma thread'ini başlat
            self.running = True
            self.read_thread = threading.Thread(target=self._read_data)
            self.read_thread.daemon = True
            self.read_thread.start()

            return True

        except Exception as e:
            Logger.error(f"BluetoothManager: Bağlantı hatası: {e}")
            self.is_connected = False
            self.socket = None
            return False

    def disconnect(self):
        """Bağlantıyı kapatır."""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.is_connected = False
        Logger.info("BluetoothManager: Bağlantı kapatıldı.")

    # -------------------------------------------------------------------------
    # Veri okuma (arka plan thread'i)
    # -------------------------------------------------------------------------
    def _read_data(self):
        """InputStream'den veri okur ve callback'i çağırır."""
        if not self.socket:
            return

        try:
            # Java InputStream al
            input_stream = self.socket.getInputStream()
        except Exception as e:
            Logger.error(f"BluetoothManager: InputStream alınamadı: {e}")
            return

        buffer_size = 1024
        while self.running:
            try:
                # Veri varsa oku
                if input_stream.available() > 0:
                    data = input_stream.read(buffer_size)
                    if data and len(data) > 0:
                        # Byte dizisini string'e çevir (UTF-8)
                        try:
                            text = data.decode('utf-8').strip()
                        except:
                            text = str(data)
                        Logger.debug(f"BluetoothManager: Veri alındı: {text}")

                        if self.callback_on_data:
                            Clock.schedule_once(lambda dt, t=text: self.callback_on_data(t), 0)
                else:
                    # Veri yoksa bekle
                    time.sleep(0.1)
            except Exception as e:
                Logger.error(f"BluetoothManager: Veri okuma hatası: {e}")
                break

    # -------------------------------------------------------------------------
    # Veri gönderme (opsiyonel)
    # -------------------------------------------------------------------------
    def send_data(self, data):
        """Bluetooth üzerinden veri gönderir."""
        if not self.is_connected or not self.socket:
            Logger.error("BluetoothManager: Bağlantı yok.")
            return False

        try:
            output_stream = self.socket.getOutputStream()
            if isinstance(data, str):
                data = data.encode('utf-8')
            output_stream.write(data)
            output_stream.flush()
            Logger.debug(f"BluetoothManager: Veri gönderildi: {data}")
            return True
        except Exception as e:
            Logger.error(f"BluetoothManager: Veri gönderme hatası: {e}")
            return False


# -----------------------------------------------------------------------------
# Kullanım örneği (main.py veya başka bir yerden çağrılabilir)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Test kodu (sadece Android'de çalışır)
    def on_device(name, addr):
        print(f"Cihaz: {name} - {addr}")

    def on_data(text):
        print(f"Gelen veri: {text}")

    bt = BluetoothManager()
    bt.callback_on_device_found = on_device
    bt.callback_on_data = on_data

    # İzinleri iste
    bt.check_and_request_permissions(lambda granted: print(f"İzinler: {granted}"))

    # Bluetooth açık mı kontrol et
    if not bt.is_bluetooth_enabled():
        bt.enable_bluetooth()
        time.sleep(3)

    # Tarama başlat
    bt.start_scan(10)
    time.sleep(12)  # tarama bitsin

    # Cihaz listesini yazdır
    for d in bt.devices_found:
        print(f"{d['name']} - {d['address']}")

    # Bağlan (MAC adresini gerçek adresle değiştir)
    # bt.connect("00:11:22:33:44:55")
    # time.sleep(30)
    # bt.disconnect()
