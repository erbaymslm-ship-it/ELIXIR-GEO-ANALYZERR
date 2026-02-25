"""
ELIXIR TECHNOLOGY
Ayarlar Ekrani
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder
from components.bluetooth_manager import BluetoothManager
from components.compass import CompassWidget
import threading

KV_SETTINGS = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex
<SettingsScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex('#0A0A0A')
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        spacing: 8

        BoxLayout:
            size_hint_y: None
            height: dp(45)
            padding: [10, 5]
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#141414')
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: "<"
                size_hint_x: None
                width: dp(40)
                background_normal: ''
                background_color: get_color_from_hex('#1A1A1A')
                color: get_color_from_hex('#FFD700')
                font_size: '18sp'
                on_press: root.go_back()

            Label:
                text: "AYARLAR"
                font_size: '16sp'
                bold: True
                color: get_color_from_hex('#FFD700')

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: [15, 10]
                spacing: 12

                BoxLayout:
                    size_hint_y: None
                    height: dp(180)
                    orientation: 'vertical'
                    padding: [12, 10]
                    spacing: 8
                    canvas.before:
                        Color:
                            rgba: get_color_from_hex('#1A1A1A')
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]
                        Color:
                            rgba: get_color_from_hex('#3D3500')
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                            width: 1

                    Label:
                        text: "BLUETOOTH BAGLANTI"
                        font_size: '14sp'
                        bold: True
                        color: get_color_from_hex('#FFD700')
                        size_hint_y: None
                        height: dp(24)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        id: bt_device_info
                        text: root.bt_status_text
                        font_size: '12sp'
                        color: get_color_from_hex('#AAAAAA')
                        size_hint_y: None
                        height: dp(20)
                        text_size: self.size
                        halign: 'left'

                    Button:
                        text: "ELIXIR CIHAZINI ARA"
                        size_hint_y: None
                        height: dp(45)
                        background_normal: ''
                        background_color: get_color_from_hex('#1A1A00')
                        color: get_color_from_hex('#FFD700')
                        font_size: '13sp'
                        bold: True
                        on_press: root.scan_devices()

                    BoxLayout:
                        size_hint_y: None
                        height: dp(38)
                        spacing: 10

                        Button:
                            text: "Son ELIXIR Cihazina Baglan"
                            background_normal: ''
                            background_color: get_color_from_hex('#002200')
                            color: get_color_from_hex('#00E676')
                            font_size: '11sp'
                            on_press: root.connect_last()

                        Button:
                            text: "Baglantiyi Kes"
                            background_normal: ''
                            background_color: get_color_from_hex('#220000')
                            color: get_color_from_hex('#FF5252')
                            font_size: '11sp'
                            on_press: root.disconnect_bt()

                BoxLayout:
                    size_hint_y: None
                    height: dp(55)
                    padding: [12, 10]
                    spacing: 10
                    canvas.before:
                        Color:
                            rgba: get_color_from_hex('#1A1A1A')
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]
                        Color:
                            rgba: get_color_from_hex('#3D3500')
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                            width: 1

                    Label:
                        text: "Otomatik Baglan"
                        font_size: '12sp'
                        color: get_color_from_hex('#FFD700')
                        text_size: self.size
                        halign: 'left'
                        valign: 'middle'

                    Switch:
                        id: auto_connect_switch
                        active: root.auto_connect_on
                        size_hint_x: 0.3
                        on_active: root.toggle_auto_connect(self.active)

                BoxLayout:
                    size_hint_y: None
                    height: dp(70)
                    orientation: 'vertical'
                    padding: [12, 10]
                    spacing: 4
                    canvas.before:
                        Color:
                            rgba: get_color_from_hex('#1A1A1A')
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]
                        Color:
                            rgba: get_color_from_hex('#3D3500')
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                            width: 1

                    Label:
                        text: "KALIBRASYON"
                        font_size: '13sp'
                        bold: True
                        color: get_color_from_hex('#FFD700')
                        size_hint_y: None
                        height: dp(20)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        id: calib_status
                        text: root.calibration_text
                        font_size: '11sp'
                        color: get_color_from_hex('#AAAAAA')
                        size_hint_y: None
                        height: dp(18)
                        text_size: self.size
                        halign: 'left'

                BoxLayout:
                    size_hint_y: None
                    height: dp(70)
                    orientation: 'vertical'
                    padding: [12, 10]
                    spacing: 4
                    canvas.before:
                        Color:
                            rgba: get_color_from_hex('#1A1A1A')
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]
                        Color:
                            rgba: get_color_from_hex('#3D3500')
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                            width: 1

                    Label:
                        text: "PIL DURUMU"
                        font_size: '13sp'
                        bold: True
                        color: get_color_from_hex('#FFD700')
                        size_hint_y: None
                        height: dp(20)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        id: battery_label
                        text: root.battery_text
                        font_size: '11sp'
                        color: get_color_from_hex('#AAAAAA')
                        size_hint_y: None
                        height: dp(18)
                        text_size: self.size
                        halign: 'left'

                BoxLayout:
                    id: compass_card
                    size_hint_y: None
                    height: dp(220)
                    orientation: 'vertical'
                    padding: [12, 10]
                    spacing: 4
                    canvas.before:
                        Color:
                            rgba: get_color_from_hex('#1A1A1A')
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]
                        Color:
                            rgba: get_color_from_hex('#3D3500')
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
                            width: 1

                    Label:
                        text: "PUSULA"
                        font_size: '13sp'
                        bold: True
                        color: get_color_from_hex('#FFD700')
                        size_hint_y: None
                        height: dp(24)
                        text_size: self.size
                        halign: 'left'

                BoxLayout:
                    size_hint_y: None
                    height: dp(50)
                    padding: [12, 10]
                    canvas.before:
                        Color:
                            rgba: get_color_from_hex('#1A1A1A')
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]

                    Label:
                        text: "ELIXIR TECHNOLOGY v0.1\\nJeofizik Veri Analiz Sistemi"
                        font_size: '10sp'
                        color: get_color_from_hex('#666666')
                        text_size: self.size
                        halign: 'center'
                        valign: 'middle'
'''

Builder.load_string(KV_SETTINGS)


class SettingsScreen(Screen):
    bt_status_text = StringProperty('ELIXIR Cihazi: Bagli degil')
    auto_connect_on = BooleanProperty(True)
    calibration_text = StringProperty('Kalibrasyon yapilmadi')
    battery_text = StringProperty('Bilinmiyor')

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.bluetooth = BluetoothManager.get_shared()
        self._compass_widget = None
        Clock.schedule_once(self._add_compass, 0)

    def _add_compass(self, dt):
        compass_card = self.ids.get('compass_card')
        if compass_card and not self._compass_widget:
            self._compass_widget = CompassWidget()
            compass_card.add_widget(self._compass_widget)

    def on_enter(self):
        self.update_status()
        self._update_event = Clock.schedule_interval(self.update_status, 2.0)
        if self._compass_widget:
            self._compass_widget.start()

    def on_leave(self):
        if hasattr(self, '_update_event'):
            self._update_event.cancel()
        if self._compass_widget:
            self._compass_widget.stop()

    def update_status(self, *args):
        if self.bluetooth.connected:
            name = self.bluetooth.device_name or 'Bilinmeyen'
            self.bt_status_text = f"Bagli: {name}"
        else:
            if self.bluetooth._last_device_address:
                self.bt_status_text = f"Bagli degil (Son: {self.bluetooth.device_name or self.bluetooth._last_device_address})"
            else:
                self.bt_status_text = "ELIXIR Cihazi: Bagli degil"

        self.auto_connect_on = self.bluetooth._auto_connect

        if self.bluetooth.calibrated:
            self.calibration_text = f"Kalibrasyon OK - Baseline: {self.bluetooth._ground_baseline}"
        else:
            count = len(self.bluetooth._calibration_values)
            if count > 0:
                self.calibration_text = f"Kalibrasyon: {count}/23 ornek alindi"
            else:
                self.calibration_text = "Kalibrasyon yapilmadi"

        battery = self.bluetooth.get_battery_level()
        if battery is not None:
            if battery > 60:
                self.battery_text = f"Pil: %{battery} (Iyi)"
            elif battery > 20:
                self.battery_text = f"Pil: %{battery} (Orta)"
            else:
                self.battery_text = f"Pil: %{battery} (Dusuk!)"
        else:
            self.battery_text = "Pil bilgisi alinamadi"

    def scan_devices(self):
        if not self.bluetooth.has_permissions():
            def after_permission(granted):
                if granted:
                    self._do_scan()
                else:
                    self.show_popup("Hata", "Bluetooth izni verilmedi.\nTelefon ayarlarindan izin verin.")
            self.bluetooth.request_permissions(callback=after_permission)
            return
        self._do_scan()

    def _do_scan(self):
        self.bt_status_text = "ELIXIR cihazi araniyor..."
        def scan_thread():
            devices = self.bluetooth.scan_devices()
            Clock.schedule_once(lambda dt: self._show_results(devices))
        threading.Thread(target=scan_thread, daemon=True).start()

    def _show_results(self, devices):
        if not devices:
            self.show_popup("Uyari", "ELIXIR cihazi bulunamadi!\n\nTelefon Ayarlari > Bluetooth\nbolumunden ELIXIR cihazinizi\nonce ESLESTIRIN.")
            self.update_status()
            return

        from kivy.uix.scrollview import ScrollView

        main_content = BoxLayout(orientation='vertical', spacing=5, padding=5)

        main_content.add_widget(Label(
            text=f"{len(devices)} cihaz bulundu",
            font_size='11sp',
            color=get_color_from_hex('#8B7500'),
            size_hint_y=None, height=25
        ))

        scroll = ScrollView(size_hint=(1, 1))
        device_list = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        device_list.bind(minimum_height=device_list.setter('height'))

        for device in devices:
            btn = Button(
                text=f"{device['name']}\n{device['address']}",
                size_hint_y=None, height=60,
                background_normal='',
                background_color=get_color_from_hex('#1A1A00'),
                color=get_color_from_hex('#FFD700'),
                font_size='13sp',
                halign='center'
            )
            btn.bind(on_press=lambda x, addr=device['address'], name=device['name']:
                     self._select_device(addr, name))
            device_list.add_widget(btn)

        scroll.add_widget(device_list)
        main_content.add_widget(scroll)

        main_content.add_widget(Button(
            text="Kapat", size_hint_y=None, height=40,
            background_normal='',
            background_color=get_color_from_hex('#330000'),
            color=get_color_from_hex('#FF5252'),
            font_size='12sp',
            on_press=lambda x: self._device_popup.dismiss()
        ))

        self._device_popup = Popup(
            title="ELIXIR Cihazi Secin",
            content=main_content,
            size_hint=(0.9, 0.65),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700')
        )
        self._device_popup.open()

    def _select_device(self, address, name):
        if hasattr(self, '_device_popup'):
            self._device_popup.dismiss()

        self.bt_status_text = f"Baglaniliyor: {name}..."
        self.show_popup("Bilgi", f"ELIXIR cihazina baglaniliyor...\n{name}")

        def connect_thread():
            success = self.bluetooth.connect(address)
            Clock.schedule_once(lambda dt: self._on_connect_result(success, name))
        threading.Thread(target=connect_thread, daemon=True).start()

    def _on_connect_result(self, success, name):
        if success:
            self.show_popup("Basarili", f"ELIXIR cihazina baglandi!\n{name}")
        else:
            self.show_popup("Hata", f"ELIXIR cihazina baglanamadi.\nCihazin acik oldugundan\nemin olun.")
        self.update_status()

    def connect_last(self):
        if self.bluetooth.connected:
            self.show_popup("Bilgi", "Zaten bagli!")
            return
        if self.bluetooth._last_device_address:
            name = self.bluetooth.device_name or self.bluetooth._last_device_address
            self.bt_status_text = f"Baglaniliyor: {name}..."
            def connect_thread():
                success = self.bluetooth.connect(self.bluetooth._last_device_address)
                Clock.schedule_once(lambda dt: self._on_connect_result(success, name))
            threading.Thread(target=connect_thread, daemon=True).start()
        else:
            self.show_popup("Uyari", "Onceki cihaz bilgisi yok.\nOnce 'ELIXIR Cihazini Ara'\nbutonuna basin.")

    def disconnect_bt(self):
        if not self.bluetooth.connected:
            self.show_popup("Bilgi", "Zaten bagli degil")
            return
        self.bluetooth.disconnect()
        self.update_status()
        self.show_popup("Bilgi", "ELIXIR cihaz baglantisi kesildi")

    def toggle_auto_connect(self, active):
        self.bluetooth._auto_connect = active
        self.bluetooth._save_config()

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, color=get_color_from_hex('#E0E0E0'), font_size='13sp'),
            size_hint=(0.75, 0.3),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700')
        )
        popup.open()

    def go_back(self):
        self.manager.current = 'main_menu'
