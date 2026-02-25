"""
ELIXIR TECHNOLOGY
Bluetooth Classic Yonetimi
"""

from kivy.utils import platform
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, StringProperty
from kivy.event import EventDispatcher
import threading
import time
import json
import os

CALIBRATION_SAMPLES = 23


class BluetoothManager(EventDispatcher):
    connected = BooleanProperty(False)
    devices = ListProperty([])
    current_data = ObjectProperty(None, allownone=True)
    device_name = StringProperty('')
    calibrated = BooleanProperty(False)
    battery_level = ObjectProperty(None, allownone=True)

    _shared_instance = None

    @staticmethod
    def get_shared():
        if BluetoothManager._shared_instance is None:
            BluetoothManager._shared_instance = BluetoothManager()
        return BluetoothManager._shared_instance

    def __init__(self, **kwargs):
        super(BluetoothManager, self).__init__(**kwargs)
        self._socket = None
        self._thread = None
        self._running = False
        self.data_callback = None
        self._buffer = ""
        self._calibration_values = []
        self._ground_baseline = 0
        self.calibrated = False
        self._last_device_address = None
        self._auto_connect = True
        self._adapter = None
        self._config_path = self._get_config_path()
        self._load_config()

    def _get_adapter(self):
        if platform == 'android' and self._adapter is None:
            try:
                from jnius import autoclass
                BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                self._adapter = BluetoothAdapter.getDefaultAdapter()
            except Exception as e:
                Logger.error(f"BT Adapter hatasi: {e}")
        return self._adapter

    def _get_config_path(self):
        if platform == 'android':
            try:
                from android.storage import app_storage_path
                return os.path.join(app_storage_path(), 'bt_config.json')
            except:
                pass
        return os.path.join(os.path.expanduser('~'), '.elixir_bt_config.json')

    def _load_config(self):
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r') as f:
                    config = json.load(f)
                    self._last_device_address = config.get('last_device', None)
                    self._auto_connect = config.get('auto_connect', True)
                    self.device_name = config.get('device_name', '')
        except Exception as e:
            Logger.warning(f"BT Config yukleme hatasi: {e}")

    def _save_config(self):
        try:
            config = {
                'last_device': self._last_device_address,
                'auto_connect': self._auto_connect,
                'device_name': self.device_name
            }
            config_dir = os.path.dirname(self._config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            with open(self._config_path, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            Logger.warning(f"BT Config kaydetme hatasi: {e}")

    def request_permissions(self, callback=None):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission

                def on_permissions(permissions, grants):
                    Logger.info(f"BT Izinler: {list(zip(permissions, grants))}")
                    if callback:
                        Clock.schedule_once(lambda dt: callback(all(grants)), 0)

                perms = [
                    Permission.BLUETOOTH,
                    Permission.BLUETOOTH_ADMIN,
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION
                ]
                try:
                    perms.append(Permission.BLUETOOTH_SCAN)
                    perms.append(Permission.BLUETOOTH_CONNECT)
                except:
                    pass

                request_permissions(perms, on_permissions)
            except Exception as e:
                Logger.error(f"Izin isteme hatasi: {e}")
                if callback:
                    callback(False)
        else:
            if callback:
                callback(True)

    def has_permissions(self):
        if platform == 'android':
            try:
                from android.permissions import check_permission, Permission
                has_bt = check_permission(Permission.BLUETOOTH)
                has_loc = check_permission(Permission.ACCESS_FINE_LOCATION)
                return has_bt and has_loc
            except:
                return True
        return True

    def try_auto_connect(self):
        if self._auto_connect and self._last_device_address and not self.connected:
            def auto_thread():
                time.sleep(1)
                self.connect(self._last_device_address)
            threading.Thread(target=auto_thread, daemon=True).start()

    def scan_devices(self):
        self.devices = []

        if platform == 'android':
            try:
                adapter = self._get_adapter()

                if adapter is None:
                    Logger.error("BT: Adapter bulunamadi - Bluetooth desteklenmiyor")
                    return self.devices

                if not adapter.isEnabled():
                    Logger.error("BT: Bluetooth kapali")
                    return self.devices

                bonded = adapter.getBondedDevices()
                Logger.info(f"BT: Eslesmis cihaz sayisi: {bonded.size()}")

                if bonded and bonded.size() > 0:
                    iterator = bonded.iterator()
                    while iterator.hasNext():
                        device = iterator.next()
                        try:
                            name = device.getName()
                            address = device.getAddress()
                            if name is None:
                                name = 'Bilinmeyen Cihaz'
                            device_info = {
                                'name': str(name),
                                'address': str(address),
                                'type': 'bonded'
                            }
                            self.devices.append(device_info)
                            Logger.info(f"BT Cihaz bulundu: {name} [{address}]")
                        except Exception as de:
                            Logger.warning(f"BT Cihaz okuma hatasi: {de}")
                else:
                    Logger.info("BT: Eslesmis cihaz yok")

            except Exception as e:
                Logger.error(f"BT tarama hatasi: {e}")
                import traceback
                traceback.print_exc()
        else:
            self.devices = [
                {'name': 'HC-05 (Mock)', 'address': 'AA:BB:CC:DD:EE:FF', 'type': 'mock'},
                {'name': 'HC-06 (Mock)', 'address': '11:22:33:44:55:66', 'type': 'mock'}
            ]

        Logger.info(f"BT: Toplam {len(self.devices)} cihaz bulundu")
        return self.devices

    def connect(self, address):
        if platform == 'android':
            try:
                from jnius import autoclass

                UUID_class = autoclass('java.util.UUID')
                spp_uuid = UUID_class.fromString("00001101-0000-1000-8000-00805F9B34FB")

                adapter = self._get_adapter()
                if adapter is None:
                    Logger.error("BT: Adapter yok")
                    return False

                adapter.cancelDiscovery()

                device = adapter.getRemoteDevice(address)

                Logger.info(f"BT: Baglaniliyor {address}...")
                self._socket = device.createRfcommSocketToServiceRecord(spp_uuid)
                self._socket.connect()

                self.connected = True
                try:
                    self.device_name = str(device.getName() or address)
                except:
                    self.device_name = address
                self._last_device_address = address
                self._save_config()
                self._start_listening()
                Logger.info(f"BT: Baglandi - {self.device_name}")
                return True

            except Exception as e:
                Logger.error(f"BT baglanti hatasi: {e}")
                self.connected = False
                if self._socket:
                    try:
                        self._socket.close()
                    except:
                        pass
                    self._socket = None
                return False
        else:
            Logger.info("Mock BT baglantisi")
            self.connected = True
            self.device_name = 'HC-05 (Mock)'
            self._last_device_address = address
            self._save_config()
            self._start_mock_data()
            return True

    def disconnect(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            self._socket = None
        self.connected = False
        self.calibrated = False
        self._calibration_values = []
        self._ground_baseline = 0
        Logger.info("BT: Baglanti kesildi")

    def reset_calibration(self):
        self.calibrated = False
        self._calibration_values = []
        self._ground_baseline = 0

    def _start_listening(self):
        self._running = True
        self._thread = threading.Thread(target=self._listen_thread)
        self._thread.daemon = True
        self._thread.start()

    def _listen_thread(self):
        if platform == 'android' and self._socket:
            try:
                input_stream = self._socket.getInputStream()
                while self._running:
                    try:
                        if input_stream.available() > 0:
                            data = input_stream.read()
                            if data != -1:
                                self._process_data(chr(data))
                        time.sleep(0.01)
                    except Exception as re:
                        Logger.warning(f"BT okuma hatasi: {re}")
                        break
            except Exception as e:
                Logger.error(f"BT stream hatasi: {e}")
            Clock.schedule_once(lambda dt: setattr(self, 'connected', False))

    def _process_data(self, char):
        if char == '\n':
            if self._buffer.strip():
                try:
                    value = int(self._buffer.strip())
                    Clock.schedule_once(lambda dt, v=value: self._handle_value(v))
                except ValueError:
                    pass
                self._buffer = ""
        else:
            self._buffer += char

    def _handle_value(self, raw_value):
        if not self.calibrated:
            self._calibration_values.append(raw_value)
            if len(self._calibration_values) >= CALIBRATION_SAMPLES:
                self._ground_baseline = sum(self._calibration_values) // len(self._calibration_values)
                self.calibrated = True
                Logger.info(f"Kalibrasyon tamamlandi. Baseline: {self._ground_baseline}")
            return

        calibrated_value = raw_value - self._ground_baseline
        self._on_data_received(calibrated_value)

    def _on_data_received(self, value):
        self.current_data = value
        if self.data_callback:
            self.data_callback(value)

    def _start_mock_data(self):
        import random
        self._running = True

        def generate_mock(dt):
            if not self._running:
                return False

            raw = random.randint(400, 600)

            if not self.calibrated:
                self._calibration_values.append(raw)
                if len(self._calibration_values) >= CALIBRATION_SAMPLES:
                    self._ground_baseline = sum(self._calibration_values) // len(self._calibration_values)
                    self.calibrated = True
                return True

            value = raw - self._ground_baseline + random.randint(-50, 200)
            self._on_data_received(value)
            return True

        Clock.schedule_interval(generate_mock, 0.3)

    def get_battery_level(self):
        if platform == 'android':
            try:
                from jnius import autoclass

                Intent = autoclass('android.content.Intent')
                IntentFilter = autoclass('android.content.IntentFilter')
                BatteryManager = autoclass('android.os.BatteryManager')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')

                ifilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
                battery_status = PythonActivity.mActivity.registerReceiver(None, ifilter)

                if battery_status:
                    level = battery_status.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                    scale = battery_status.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                    if level >= 0 and scale > 0:
                        self.battery_level = int(level * 100 / scale)
                        return self.battery_level
            except Exception as e:
                Logger.warning(f"Pil seviyesi alinamadi: {e}")
        return None
