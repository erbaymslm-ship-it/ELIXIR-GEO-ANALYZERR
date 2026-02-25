"""
ELIXIR TECHNOLOGY
Yer Alti Goruntuleme Modu - Modern Tasarim
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.utils import get_color_from_hex
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from components.bluetooth_manager import BluetoothManager
from components.grid_manager import GridManager, ScanDirection, ScanType
from components.heatmap import HeatMapWidget
from components.depth_calculator import DepthCalculator
from components.data_io import DataIO
from components.filters import FILTERS, apply_filter
from components.sound_manager import SoundManager
import threading
import os
import numpy as np

KV_UNDERGROUND = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex
<IconBtn@ButtonBehavior+BoxLayout>:
    orientation: 'vertical'
    spacing: 2
    padding: [4, 4]
    size_hint_y: None
    height: dp(60)
    canvas.before:
        Color:
            rgba: get_color_from_hex('#1A1A00')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8]
        Color:
            rgba: get_color_from_hex('#3D3500')
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, 8]
            width: 1

<UndergroundScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex('#0A0A0A')
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        spacing: 3

        BoxLayout:
            size_hint_y: None
            height: dp(40)
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
                width: dp(35)
                background_normal: ''
                background_color: get_color_from_hex('#1A1A1A')
                color: get_color_from_hex('#FFD700')
                font_size: '16sp'
                on_press: root.go_back()

            Label:
                id: battery_label
                text: root.battery_text
                size_hint_x: None
                width: dp(55)
                font_size: '9sp'
                color: get_color_from_hex('#00E676')

            Label:
                text: "YER ALTI GORUNTULEME"
                font_size: '13sp'
                bold: True
                color: get_color_from_hex('#FFD700')

            Image:
                source: root.icon_heatmap
                size_hint: None, None
                size: dp(24), dp(24)
                pos_hint: {'center_y': 0.5}
                allow_stretch: True

        BoxLayout:
            size_hint_y: None
            height: dp(28)
            padding: [10, 2]
            spacing: 8
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#0F0F0F')
                Rectangle:
                    pos: self.pos
                    size: self.size

            Image:
                source: root.icon_bluetooth
                size_hint: None, None
                size: dp(16), dp(16)
                pos_hint: {'center_y': 0.5}
                allow_stretch: True

            Label:
                id: bt_status
                text: "Bluetooth: Bagli degil"
                color: get_color_from_hex('#FF5252')
                font_size: '10sp'
                text_size: self.size
                halign: 'left'
                valign: 'middle'

            Label:
                id: calib_status
                text: root.calib_text
                color: get_color_from_hex('#8B7500')
                font_size: '9sp'
                size_hint_x: 0.35
                text_size: self.size
                halign: 'right'
                valign: 'middle'

        BoxLayout:
            size_hint_y: None
            height: dp(32)
            padding: [10, 2]
            spacing: 5

            Label:
                text: "Filtre:"
                size_hint_x: 0.15
                color: get_color_from_hex('#8B7500')
                font_size: '10sp'

            Spinner:
                id: filter_spinner
                text: 'Filtre Yok'
                values: root.filter_names
                size_hint_x: 0.55
                background_normal: ''
                background_color: get_color_from_hex('#1A1A00')
                color: get_color_from_hex('#FFD700')
                font_size: '10sp'
                on_text: root.on_filter_changed(self.text)

            Button:
                text: "Renk"
                size_hint_x: 0.3
                background_normal: ''
                background_color: get_color_from_hex('#1A1A00')
                color: get_color_from_hex('#FFD700')
                font_size: '9sp'
                on_press: root.show_color_legend()

        BoxLayout:
            size_hint_y: None
            height: dp(45)
            padding: [10, 3]
            spacing: 8

            BoxLayout:
                orientation: 'vertical'
                spacing: 1

                Label:
                    text: "Grid"
                    color: get_color_from_hex('#8B7500')
                    font_size: '9sp'
                    size_hint_y: 0.4

                BoxLayout:
                    spacing: 4

                    TextInput:
                        id: grid_rows
                        text: '5'
                        input_filter: 'int'
                        multiline: False
                        background_color: get_color_from_hex('#222222')
                        foreground_color: get_color_from_hex('#FFD700')
                        cursor_color: get_color_from_hex('#FFD700')
                        font_size: '12sp'
                        padding: [6, 2]

                    Label:
                        text: "x"
                        size_hint_x: 0.2
                        color: get_color_from_hex('#666666')

                    TextInput:
                        id: grid_cols
                        text: '5'
                        input_filter: 'int'
                        multiline: False
                        background_color: get_color_from_hex('#222222')
                        foreground_color: get_color_from_hex('#FFD700')
                        cursor_color: get_color_from_hex('#FFD700')
                        font_size: '12sp'
                        padding: [6, 2]

            Button:
                text: "Grid Olustur"
                size_hint_x: 0.45
                background_normal: ''
                background_color: get_color_from_hex('#1A1A00')
                color: get_color_from_hex('#FFD700')
                font_size: '11sp'
                on_press: root.create_grid()

        BoxLayout:
            padding: [6, 3]
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#141414')
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [8]

            HeatMapWidget:
                id: heatmap
                rows: root.grid_rows
                cols: root.grid_cols

        BoxLayout:
            size_hint_y: None
            height: dp(18)
            padding: [10, 1]
            spacing: 5

            ProgressBar:
                id: progress
                value: root.scan_progress
                max: 100

            Label:
                text: f"{int(root.scan_progress)}%"
                size_hint_x: 0.1
                color: get_color_from_hex('#FFD700')
                font_size: '9sp'

        BoxLayout:
            size_hint_y: None
            height: dp(42)
            padding: [6, 2]
            spacing: 4

            Button:
                text: "ORNEK AL"
                background_normal: ''
                background_color: get_color_from_hex('#002200')
                color: get_color_from_hex('#00E676')
                font_size: '10sp'
                bold: True
                on_press: root.take_sample()

        GridLayout:
            cols: 4
            size_hint_y: None
            height: dp(50)
            padding: [6, 2]
            spacing: 4

            IconBtn:
                on_press: root.start_scan()
                Label:
                    text: "BASLAT"
                    font_size: '9sp'
                    bold: True
                    color: get_color_from_hex('#00E676')

            IconBtn:
                on_press: root.stop_scan()
                Label:
                    text: "DURDUR"
                    font_size: '9sp'
                    bold: True
                    color: get_color_from_hex('#FF5252')

            IconBtn:
                on_press: root.toggle_values()
                Label:
                    text: "DEGERLER"
                    font_size: '9sp'
                    color: get_color_from_hex('#FFD700')

            IconBtn:
                on_press: root.show_depth()
                Label:
                    text: "DERINLIK"
                    font_size: '9sp'
                    color: get_color_from_hex('#FFD700')

        GridLayout:
            cols: 3
            size_hint_y: None
            height: dp(50)
            padding: [6, 0, 6, 4]
            spacing: 4

            IconBtn:
                on_press: root.show_4d()
                Image:
                    source: root.icon_3d
                    size_hint: None, None
                    size: dp(18), dp(18)
                    pos_hint: {'center_x': 0.5}
                    allow_stretch: True
                Label:
                    text: "4D VOXEL"
                    font_size: '9sp'
                    color: get_color_from_hex('#FFE44D')
                    bold: True

            IconBtn:
                on_press: root.export_csv()
                Image:
                    source: root.icon_export
                    size_hint: None, None
                    size: dp(18), dp(18)
                    pos_hint: {'center_x': 0.5}
                    allow_stretch: True
                Label:
                    text: "CSV AKTAR"
                    font_size: '9sp'
                    color: get_color_from_hex('#FFD700')

            IconBtn:
                on_press: root.import_csv()
                Label:
                    text: "CSV YUKLE"
                    font_size: '9sp'
                    color: get_color_from_hex('#FFD700')
'''

Builder.load_string(KV_UNDERGROUND)


class UndergroundScreen(Screen):
    scan_progress = NumericProperty(0)
    grid_rows = NumericProperty(5)
    grid_cols = NumericProperty(5)
    icon_heatmap = StringProperty('')
    icon_bluetooth = StringProperty('')
    icon_3d = StringProperty('')
    icon_export = StringProperty('')
    calib_text = StringProperty('Kalibrasyon: Bekleniyor')
    battery_text = StringProperty('')
    filter_names = list(FILTERS.keys())
    current_filter = StringProperty('Filtre Yok')

    def __init__(self, **kwargs):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        for attr, fname in [
            ('icon_heatmap', 'icon_heatmap.png'),
            ('icon_bluetooth', 'icon_bluetooth.png'),
            ('icon_3d', 'icon_3d.png'),
            ('icon_export', 'icon_export.png'),
        ]:
            path = os.path.join(assets_dir, fname)
            if os.path.exists(path):
                setattr(self, attr, path)

        super(UndergroundScreen, self).__init__(**kwargs)

        self.bluetooth = BluetoothManager.get_shared()
        self.grid_manager = GridManager()
        self.depth_calculator = DepthCalculator(sensor_distance=0.5)
        self.data_io = DataIO()
        self.sound = SoundManager.get_instance()

        self.scanning = False
        self.showing_values = False
        self.depth_data = {}
        self.selected_device = None

        self.scan_direction = ScanDirection.RIGHT
        self.scan_type = ScanType.ZIGZAG
        self.start_from = ScanDirection.RIGHT

        self.bluetooth.data_callback = self.on_data_received
        Clock.schedule_interval(self.update_ui, 0.5)

    def on_enter(self):
        self.update_bluetooth_status()
        self.update_calibration_status()
        self.update_battery()
        self.ids.heatmap.cell_tap_callback = self.on_cell_tapped

    def update_ui(self, dt):
        if hasattr(self.ids, 'progress'):
            self.ids.progress.value = self.scan_progress
        self.update_calibration_status()
        self.update_battery()

    def update_battery(self):
        level = self.bluetooth.get_battery_level()
        if level is not None:
            self.battery_text = f"Pil:%{level}"
        else:
            self.battery_text = ""

    def update_calibration_status(self):
        if self.bluetooth.calibrated:
            self.calib_text = f"Kal: OK ({self.bluetooth._ground_baseline})"
        else:
            count = len(self.bluetooth._calibration_values)
            if count > 0:
                self.calib_text = f"Kal: {count}/23"
            else:
                self.calib_text = "Kal: Bekleniyor"

    def update_bluetooth_status(self):
        if hasattr(self.ids, 'bt_status'):
            if self.bluetooth.connected:
                name = self.bluetooth.device_name or 'Bagli'
                self.ids.bt_status.text = f"BT: {name}"
                self.ids.bt_status.color = get_color_from_hex('#00E676')
            else:
                self.ids.bt_status.text = "BT: Bagli degil"
                self.ids.bt_status.color = get_color_from_hex('#FF5252')

    def on_filter_changed(self, filter_name):
        self.current_filter = filter_name
        self.refresh_heatmap()

    def refresh_heatmap(self):
        if not self.grid_manager.data:
            return

        raw_data = list(self.grid_manager.data.values())
        self.ids.heatmap.grid_data = raw_data

        if self.current_filter != 'Filtre Yok':
            matrix = self.grid_manager.get_data_matrix()
            filtered = apply_filter(matrix, self.current_filter, self.grid_rows, self.grid_cols)
            self.ids.heatmap.data_matrix = filtered.astype(np.uint8)
            self.ids.heatmap.update_canvas()

    def show_color_legend(self):
        filter_info = FILTERS.get(self.current_filter, {})
        colors = filter_info.get('colors', [])
        desc = filter_info.get('description', '')

        content = BoxLayout(orientation='vertical', spacing=6, padding=10)
        content.add_widget(Label(
            text=f"Filtre: {self.current_filter}",
            font_size='13sp', bold=True,
            color=get_color_from_hex('#FFD700'),
            size_hint_y=None, height=25
        ))
        content.add_widget(Label(
            text=desc, font_size='10sp',
            color=get_color_from_hex('#AAAAAA'),
            size_hint_y=None, height=20
        ))

        for color_hex, label_text in colors:
            row = BoxLayout(size_hint_y=None, height=25, spacing=8)
            color_box = Label(size_hint_x=None, width=30)
            color_box.canvas.before.clear()
            from kivy.graphics import Color as GColor, RoundedRectangle as GRR
            with color_box.canvas.before:
                GColor(*get_color_from_hex(color_hex))
                GRR(pos=color_box.pos, size=(25, 20), radius=[3])
            row.add_widget(color_box)
            row.add_widget(Label(
                text=label_text, font_size='11sp',
                color=get_color_from_hex('#E0E0E0'),
                text_size=(200, None), halign='left'
            ))
            content.add_widget(row)

        content.add_widget(Button(
            text="Kapat", size_hint_y=None, height=35,
            background_normal='',
            background_color=get_color_from_hex('#330000'),
            color=get_color_from_hex('#FF5252'),
            on_press=lambda x: popup.dismiss()
        ))

        popup = Popup(
            title="Renk Aciklamasi", content=content,
            size_hint=(0.75, 0.55),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700')
        )
        popup.open()

    def take_sample(self):
        if not self.bluetooth.connected:
            self.show_popup("Uyari", "Once ELIXIR Goruntuleme Cihazinizi baglayiniz\n(Ayarlar ekranindan)")
            return

        if not self.bluetooth.calibrated:
            self.show_popup("Bilgi", "Kalibrasyon devam ediyor.\nLutfen bekleyin.")
            return

        if not self.grid_manager.data and not self.scanning:
            self.show_popup("Uyari", "Once grid olusturun")
            return

        self.scanning = True
        self.show_popup("Bilgi", "Ornek bekleniyor...")

    def create_grid(self):
        try:
            rows = int(self.ids.grid_rows.text)
            cols = int(self.ids.grid_cols.text)
            if rows < 1 or cols < 1:
                self.show_popup("Hata", "Grid boyutu 1'den buyuk olmali")
                return
            self.grid_rows = rows
            self.grid_cols = cols
            self.show_direction_popup()
        except ValueError:
            self.show_popup("Hata", "Gecerli sayi giriniz")

    def show_direction_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(
            text="Cekim Yonu Secin:", color=get_color_from_hex('#FFD700'),
            font_size='14sp'
        ))

        for text, direction in [("SAG", ScanDirection.RIGHT), ("SOL", ScanDirection.LEFT)]:
            btn = Button(
                text=text, size_hint_y=None, height=50,
                background_normal='',
                background_color=get_color_from_hex('#1A1A00'),
                color=get_color_from_hex('#FFD700')
            )
            btn.bind(on_press=lambda x, d=direction: self.set_direction(d))
            content.add_widget(btn)

        self.direction_popup = Popup(
            title="Cekim Yonu", content=content,
            size_hint=(0.65, 0.4),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700')
        )
        self.direction_popup.open()

    def set_direction(self, direction):
        self.start_from = direction
        self.direction_popup.dismiss()
        self.show_scan_type_popup()

    def show_scan_type_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(
            text="Tarama Tipi Secin:", color=get_color_from_hex('#FFD700'),
            font_size='14sp'
        ))

        for text, stype in [("ZIGZAG", ScanType.ZIGZAG), ("PARALEL", ScanType.PARALLEL)]:
            btn = Button(
                text=text, size_hint_y=None, height=50,
                background_normal='',
                background_color=get_color_from_hex('#1A1A00'),
                color=get_color_from_hex('#FFD700')
            )
            btn.bind(on_press=lambda x, st=stype: self.set_scan_type(st))
            content.add_widget(btn)

        self.scan_type_popup = Popup(
            title="Tarama Tipi", content=content,
            size_hint=(0.65, 0.4),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700')
        )
        self.scan_type_popup.open()

    def set_scan_type(self, scan_type):
        self.scan_type = scan_type
        self.scan_type_popup.dismiss()

        self.grid_manager.configure(
            rows=self.grid_rows, cols=self.grid_cols,
            direction=ScanDirection.RIGHT,
            scan_type=self.scan_type,
            start_from=self.start_from
        )

        self.ids.heatmap.rows = self.grid_rows
        self.ids.heatmap.cols = self.grid_cols
        self.ids.heatmap.grid_data = []

        self.show_popup("Basarili", f"Grid olusturuldu: {self.grid_rows}x{self.grid_cols}")

    def start_scan(self):
        if not self.bluetooth.connected:
            self.show_popup("Uyari", "Once ELIXIR Goruntuleme Cihazinizi baglayiniz\n(Ayarlar ekranindan)")
            return
        if not self.bluetooth.calibrated:
            self.show_popup("Bilgi", "Kalibrasyon devam ediyor.\nLutfen bekleyin.")
            return
        self.scanning = True
        self.scan_progress = 0
        self.show_popup("Bilgi", "Tarama baslatildi")

    def stop_scan(self):
        self.scanning = False
        self.show_popup("Bilgi", "Tarama durduruldu")

    def on_data_received(self, value):
        if not self.scanning:
            return

        self.sound.play_beep_for_value(abs(value))

        continue_scan = self.grid_manager.add_data(value)
        self.refresh_heatmap()
        self.scan_progress = self.grid_manager.scan_complete

        if not continue_scan:
            self.scanning = False
            self.sound.play('scan_complete')
            self.show_popup("Tamamlandi", "Tarama tamamlandi!\n4D goruntulemek icin butona tiklayin.")
            self.calculate_depths()

    def calculate_depths(self):
        self.depth_data = self.depth_calculator.calculate_grid_depths(
            self.grid_manager.data, self.grid_rows, self.grid_cols
        )

    def toggle_values(self):
        self.showing_values = not self.showing_values
        self.ids.heatmap.show_values = 1 if self.showing_values else 0

    def show_depth(self):
        if not self.depth_data:
            self.calculate_depths()

        content = BoxLayout(orientation='vertical', spacing=5, padding=10)
        scroll = ScrollView(size_hint=(1, 0.85))
        grid = GridLayout(cols=3, spacing=5, size_hint_y=None, row_default_height=30)
        grid.bind(minimum_height=grid.setter('height'))

        for text in ["X", "Y", "Derinlik (m)"]:
            grid.add_widget(Label(
                text=text, bold=True, color=get_color_from_hex('#FFD700'),
                font_size='12sp', size_hint_y=None, height=30
            ))

        for key, depth in self.depth_data.items():
            row, col = key.split(',')
            for t in [str(col), str(row), f"{depth:.2f}"]:
                grid.add_widget(Label(
                    text=t, color=get_color_from_hex('#E0E0E0'),
                    font_size='11sp', size_hint_y=None, height=25
                ))

        scroll.add_widget(grid)
        content.add_widget(scroll)
        content.add_widget(Button(
            text="Kapat", size_hint_y=None, height=40,
            background_normal='',
            background_color=get_color_from_hex('#330000'),
            color=get_color_from_hex('#FF5252'),
            on_press=lambda x: popup.dismiss()
        ))

        popup = Popup(
            title="Derinlik Degerleri", content=content,
            size_hint=(0.85, 0.7),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700')
        )
        popup.open()

    def show_4d(self):
        if not self.grid_manager.data:
            self.show_popup("Uyari", "Once veri toplayin")
            return

        from components.voxel_view import VoxelViewWidget
        matrix = self.grid_manager.get_data_matrix()

        if np.max(matrix) > np.min(matrix):
            norm_matrix = ((matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix)) * 255).astype(np.uint8)
        else:
            norm_matrix = (matrix * 255).astype(np.uint8)

        content = BoxLayout(orientation='vertical', spacing=5, padding=5)

        voxel = VoxelViewWidget(
            data_matrix=norm_matrix,
            depth_data=self.depth_data
        )
        content.add_widget(voxel)

        content.add_widget(Button(
            text="Kapat", size_hint_y=None, height=40,
            background_normal='',
            background_color=get_color_from_hex('#330000'),
            color=get_color_from_hex('#FF5252'),
            on_press=lambda x: popup.dismiss()
        ))

        popup = Popup(
            title="4D Voxel Goruntuleme", content=content,
            size_hint=(0.95, 0.85),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700')
        )
        popup.open()

    def export_csv(self):
        if not self.grid_manager.data:
            self.show_popup("Uyari", "Disa aktarilacak veri yok")
            return
        filename = self.data_io.export_to_csv(
            self.grid_manager.data, self.grid_rows, self.grid_cols, self.depth_data
        )
        self.show_popup("Basarili", f"Veriler kaydedildi:\n{filename}")

    def import_csv(self):
        csv_files = self.data_io.get_csv_files()

        if not csv_files:
            self.show_popup("Uyari", "Yuklenecek CSV dosyasi bulunamadi")
            return

        content = BoxLayout(orientation='vertical', spacing=8, padding=10)
        content.add_widget(Label(
            text="CSV Dosyasi Secin:",
            color=get_color_from_hex('#FFD700'),
            font_size='14sp', bold=True,
            size_hint_y=None, height=30
        ))

        scroll = ScrollView(size_hint=(1, 1))
        file_list = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        file_list.bind(minimum_height=file_list.setter('height'))

        popup = Popup(
            title="CSV Yukle",
            content=content,
            size_hint=(0.85, 0.6),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700')
        )

        for csv_file in csv_files:
            btn = Button(
                text=csv_file['name'],
                size_hint_y=None, height=45,
                background_normal='',
                background_color=get_color_from_hex('#1A1A00'),
                color=get_color_from_hex('#FFD700'),
                font_size='11sp',
                text_size=(None, None),
                halign='left',
                valign='middle',
                padding=[10, 0]
            )
            btn.bind(on_press=lambda x, path=csv_file['path']: self._load_csv_file(path, popup))
            file_list.add_widget(btn)

        scroll.add_widget(file_list)
        content.add_widget(scroll)

        content.add_widget(Button(
            text="Iptal", size_hint_y=None, height=40,
            background_normal='',
            background_color=get_color_from_hex('#330000'),
            color=get_color_from_hex('#FF5252'),
            on_press=lambda x: popup.dismiss()
        ))

        popup.open()

    def _load_csv_file(self, filepath, popup):
        popup.dismiss()
        data = self.data_io.import_from_csv(filepath)
        if data:
            max_row = max(item['row'] for item in data)
            max_col = max(item['col'] for item in data)
            self.grid_rows = max_row + 1
            self.grid_cols = max_col + 1
            self.grid_manager.import_from_csv_data(data)
            self.ids.heatmap.rows = self.grid_rows
            self.ids.heatmap.cols = self.grid_cols
            self.refresh_heatmap()
            self.depth_data = {}
            for item in data:
                if 'depth' in item and item['depth']:
                    key = f"{item['row']},{item['col']}"
                    self.depth_data[key] = item['depth']
            self.show_popup("Basarili", f"CSV yuklendi\n{len(data)} kayit")
        else:
            self.show_popup("Hata", "CSV dosyasi okunamadi")

    def on_cell_tapped(self, row, col, value):
        raw_value = 0
        if self.grid_manager.data:
            for item in self.grid_manager.data.values():
                if item.get('row') == row and item.get('col') == col:
                    raw_value = item.get('value', 0)
                    break

        content = BoxLayout(orientation='vertical', spacing=10, padding=15)

        info_text = (
            f"[b]Hucre Koordinatlari:[/b]\n"
            f"X: {col}    Y: {row}\n\n"
            f"[b]Ham Deger:[/b] {raw_value}\n"
            f"[b]Normalize Deger:[/b] {int(value)}"
        )
        info_label = Label(
            text=info_text,
            markup=True,
            color=get_color_from_hex('#E0E0E0'),
            font_size='13sp',
            halign='left',
            valign='top',
            size_hint_y=0.5,
        )
        info_label.bind(size=info_label.setter('text_size'))
        content.add_widget(info_label)

        btn_4d = Button(
            text="4D Goruntule",
            size_hint_y=None,
            height=45,
            background_normal='',
            background_color=get_color_from_hex('#1A1A00'),
            color=get_color_from_hex('#FFE44D'),
            font_size='13sp',
            bold=True,
        )

        btn_close = Button(
            text="Kapat",
            size_hint_y=None,
            height=40,
            background_normal='',
            background_color=get_color_from_hex('#330000'),
            color=get_color_from_hex('#FF5252'),
            font_size='12sp',
        )

        content.add_widget(btn_4d)
        content.add_widget(btn_close)

        popup = Popup(
            title=f"Hucre Bilgisi ({col}, {row})",
            content=content,
            size_hint=(0.75, 0.45),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700'),
        )

        btn_close.bind(on_press=lambda x: popup.dismiss())
        btn_4d.bind(on_press=lambda x: self._open_4d_focused(row, col, popup))

        popup.open()

    def _open_4d_focused(self, row, col, cell_popup):
        cell_popup.dismiss()
        if not self.grid_manager.data:
            self.show_popup("Uyari", "Once veri toplayin")
            return

        from components.voxel_view import VoxelViewWidget
        matrix = self.grid_manager.get_data_matrix()

        if np.max(matrix) > np.min(matrix):
            norm_matrix = ((matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix)) * 255).astype(np.uint8)
        else:
            norm_matrix = (matrix * 255).astype(np.uint8)

        content = BoxLayout(orientation='vertical', spacing=5, padding=5)

        voxel = VoxelViewWidget(
            data_matrix=norm_matrix,
            depth_data=self.depth_data,
            focus_row=row,
            focus_col=col,
        )
        content.add_widget(voxel)

        content.add_widget(Button(
            text="Kapat", size_hint_y=None, height=40,
            background_normal='',
            background_color=get_color_from_hex('#330000'),
            color=get_color_from_hex('#FF5252'),
            on_press=lambda x: popup.dismiss()
        ))

        popup = Popup(
            title=f"4D Voxel - Hucre ({col}, {row})",
            content=content,
            size_hint=(0.95, 0.85),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700'),
        )
        popup.open()

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, color=get_color_from_hex('#E0E0E0'), font_size='13sp'),
            size_hint=(0.7, 0.3),
            separator_color=get_color_from_hex('#FFD700'),
            title_color=get_color_from_hex('#FFD700')
        )
        popup.open()

    def go_back(self):
        self.stop_scan()
        self.manager.current = 'main_menu'
