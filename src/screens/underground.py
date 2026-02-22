"""
ELIXIR TECHNOLOGY
Yer Altı Görüntüleme Modu
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
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.logger import Logger
from kivy.lang import Builder
from components.bluetooth_manager import BluetoothManager
from components.grid_manager import GridManager, ScanDirection, ScanType
from components.heatmap import HeatMapWidget
from components.depth_calculator import DepthCalculator
from components.data_io import DataIO
import threading

KV_UNDERGROUND = '''
<UndergroundScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex('#16213e')
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        
        # Başlık
        BoxLayout:
            size_hint_y: 0.08
            padding: [10, 5]
            
            Label:
                text: "YER ALTI GÖRÜNTÜLEME"
                font_size: '18sp'
                bold: True
                color: get_color_from_hex('#4ecca3')
            
            Button:
                text: "Geri"
                size_hint_x: 0.2
                background_normal: ''
                background_color: get_color_from_hex('#0f3460')
                on_press: root.go_back()
        
        # Bluetooth durumu
        BoxLayout:
            size_hint_y: 0.05
            padding: [10, 0]
            
            Label:
                id: bt_status
                text: "Bluetooth: Bağlı değil"
                color: get_color_from_hex('#ff6b6b')
                font_size: '12sp'
            
            Button:
                text: "Cihazları Tara"
                size_hint_x: 0.3
                background_normal: ''
                background_color: get_color_from_hex('#0f3460')
                on_press: root.scan_bluetooth()
        
        # Grid ayarları
        BoxLayout:
            size_hint_y: 0.15
            padding: [10, 5]
            spacing: 10
            
            BoxLayout:
                orientation: 'vertical'
                
                Label:
                    text: "Grid Boyutu"
                    color: get_color_from_hex('#ffffff')
                    size_hint_y: 0.3
                
                BoxLayout:
                    orientation: 'horizontal'
                    
                    TextInput:
                        id: grid_rows
                        text: '5'
                        input_filter: 'int'
                        multiline: False
                        size_hint_x: 0.5
                    
                    Label:
                        text: "x"
                        size_hint_x: 0.2
                    
                    TextInput:
                        id: grid_cols
                        text: '5'
                        input_filter: 'int'
                        multiline: False
                        size_hint_x: 0.5
            
            Button:
                text: "Grid Oluştur"
                size_hint_x: 0.5
                background_normal: ''
                background_color: get_color_from_hex('#4ecca3')
                on_press: root.create_grid()
        
        # Isı haritası
        BoxLayout:
            size_hint_y: 0.5
            padding: [10, 0]
            
            HeatMapWidget:
                id: heatmap
                rows: root.grid_rows
                cols: root.grid_cols
        
        # İlerleme
        BoxLayout:
            size_hint_y: 0.05
            padding: [10, 0]
            
            ProgressBar:
                id: progress
                value: root.scan_progress
                max: 100
            
            Label:
                text: f"{int(root.scan_progress)}%"
                size_hint_x: 0.15
        
        # Kontrol butonları
        GridLayout:
            size_hint_y: 0.17
            cols: 3
            padding: [10, 5]
            spacing: 5
            
            Button:
                text: "Başlat"
                background_normal: ''
                background_color: get_color_from_hex('#4ecca3')
                on_press: root.start_scan()
            
            Button:
                text: "Durdur"
                background_normal: ''
                background_color: get_color_from_hex('#ff6b6b')
                on_press: root.stop_scan()
            
            Button:
                text: "Değer Gör"
                background_normal: ''
                background_color: get_color_from_hex('#0f3460')
                on_press: root.toggle_values()
            
            Button:
                text: "Derinlik Gör"
                background_normal: ''
                background_color: get_color_from_hex('#0f3460')
                on_press: root.show_depth()
            
            Button:
                text: "3D Görüntüle"
                background_normal: ''
                background_color: get_color_from_hex('#0f3460')
                on_press: root.show_3d()
            
            Button:
                text: "CSV Export"
                background_normal: ''
                background_color: get_color_from_hex('#0f3460')
                on_press: root.export_csv()
            
            Button:
                text: "CSV Import"
                background_normal: ''
                background_color: get_color_from_hex('#0f3460')
                on_press: root.import_csv()
'''

Builder.load_string(KV_UNDERGROUND)

class UndergroundScreen(Screen):
    """
    Yer altı görüntüleme modu ekranı
    """
    
    def __init__(self, **kwargs):
        super(UndergroundScreen, self).__init__(**kwargs)
        
        # Bileşenler
        self.bluetooth = BluetoothManager()
        self.grid_manager = GridManager()
        self.depth_calculator = DepthCalculator(sensor_distance=0.5)
        self.data_io = DataIO()
        
        # Durum değişkenleri
        self.scanning = False
        self.scan_progress = 0
        self.grid_rows = 5
        self.grid_cols = 5
        self.showing_values = False
        self.depth_data = {}
        self.selected_device = None
        
        # Grid yönlendirme değişkenleri
        self.scan_direction = ScanDirection.RIGHT
        self.scan_type = ScanType.ZIGZAG
        self.start_from = ScanDirection.RIGHT
        
        # Bluetooth callback
        self.bluetooth.data_callback = self.on_data_received
        
        # Güncelleme schedule
        Clock.schedule_interval(self.update_ui, 0.1)
    
    def on_enter(self):
        """Ekrana girildiğinde"""
        self.update_bluetooth_status()
    
    def update_ui(self, dt):
        """UI güncelleme"""
        if hasattr(self.ids, 'progress'):
            self.ids.progress.value = self.scan_progress
    
    def update_bluetooth_status(self):
        """Bluetooth durumunu güncelle"""
        if hasattr(self.ids, 'bt_status'):
            if self.bluetooth.connected:
                self.ids.bt_status.text = "Bluetooth: Bağlı"
                self.ids.bt_status.color = get_color_from_hex('#4ecca3')
            else:
                self.ids.bt_status.text = "Bluetooth: Bağlı değil"
                self.ids.bt_status.color = get_color_from_hex('#ff6b6b')
    
    def scan_bluetooth(self):
        """Bluetooth cihazlarını tara"""
        def scan_thread():
            devices = self.bluetooth.scan_devices()
            Clock.schedule_once(lambda dt: self.show_device_list(devices))
        
        threading.Thread(target=scan_thread).start()
    
    def show_device_list(self, devices):
        """Cihaz listesini göster"""
        if not devices:
            self.show_popup("Uyarı", "Bluetooth cihazı bulunamadı")
            return
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        for device in devices:
            btn = Button(
                text=f"{device['name']}\n{device['address']}",
                size_hint_y=None,
                height=60,
                background_normal='',
                background_color=get_color_from_hex('#0f3460')
            )
            btn.bind(on_press=lambda x, addr=device['address']: self.connect_device(addr))
            content.add_widget(btn)
        
        content.add_widget(Button(
            text="Kapat",
            size_hint_y=None,
            height=40,
            background_normal='',
            background_color=get_color_from_hex('#ff6b6b'),
            on_press=lambda x: popup.dismiss()
        ))
        
        popup = Popup(
            title="Bluetooth Cihazları",
            content=content,
            size_hint=(0.8, 0.6)
        )
        popup.open()
    
    def connect_device(self, address):
        """Cihaza bağlan"""
        success = self.bluetooth.connect(address)
        if success:
            self.selected_device = address
            self.show_popup("Başarılı", "Bluetooth bağlantısı kuruldu")
        else:
            self.show_popup("Hata", "Bağlantı kurulamadı")
        
        self.update_bluetooth_status()
    
    def create_grid(self):
        """Grid oluştur"""
        try:
            rows = int(self.ids.grid_rows.text)
            cols = int(self.ids.grid_cols.text)
            
            if rows < 1 or cols < 1:
                self.show_popup("Hata", "Grid boyutu 1'den büyük olmalı")
                return
            
            self.grid_rows = rows
            self.grid_cols = cols
            
            # Tarama yönü seçimi
            self.show_direction_popup()
            
        except ValueError:
            self.show_popup("Hata", "Geçerli sayı giriniz")
    
    def show_direction_popup(self):
        """Tarama yönü popup'ı"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text="Çekim Yönü Seçin:", color=get_color_from_hex('#ffffff')))
        
        btn_right = Button(
            text="SAĞ",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=get_color_from_hex('#4ecca3')
        )
        btn_right.bind(on_press=lambda x: self.set_direction(ScanDirection.RIGHT))
        
        btn_left = Button(
            text="SOL",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=get_color_from_hex('#0f3460')
        )
        btn_left.bind(on_press=lambda x: self.set_direction(ScanDirection.LEFT))
        
        content.add_widget(btn_right)
        content.add_widget(btn_left)
        
        self.direction_popup = Popup(
            title="Çekim Yönü",
            content=content,
            size_hint=(0.6, 0.4)
        )
        self.direction_popup.open()
    
    def set_direction(self, direction):
        """Tarama yönünü ayarla"""
        self.start_from = direction
        self.direction_popup.dismiss()
        self.show_scan_type_popup()
    
    def show_scan_type_popup(self):
        """Tarama tipi popup'ı"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text="Tarama Tipi Seçin:", color=get_color_from_hex('#ffffff')))
        
        btn_zigzag = Button(
            text="ZIGZAG",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=get_color_from_hex('#4ecca3')
        )
        btn_zigzag.bind(on_press=lambda x: self.set_scan_type(ScanType.ZIGZAG))
        
        btn_parallel = Button(
            text="PARALEL",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=get_color_from_hex('#0f3460')
        )
        btn_parallel.bind(on_press=lambda x: self.set_scan_type(ScanType.PARALEL))
        
        content.add_widget(btn_zigzag)
        content.add_widget(btn_parallel)
        
        self.scan_type_popup = Popup(
            title="Tarama Tipi",
            content=content,
            size_hint=(0.6, 0.4)
        )
        self.scan_type_popup.open()
    
    def set_scan_type(self, scan_type):
        """Tarama tipini ayarla"""
        self.scan_type = scan_type
        self.scan_type_popup.dismiss()
        
        # Grid'i yapılandır
        self.grid_manager.configure(
            rows=self.grid_rows,
            cols=self.grid_cols,
            direction=ScanDirection.RIGHT,
            scan_type=self.scan_type,
            start_from=self.start_from
        )
        
        # Heatmap'i güncelle
        self.ids.heatmap.rows = self.grid_rows
        self.ids.heatmap.cols = self.grid_cols
        self.ids.heatmap.grid_data = []
        
        self.show_popup("Başarılı", f"Grid oluşturuldu: {self.grid_rows}x{self.grid_cols}")
    
    def start_scan(self):
        """Taramayı başlat"""
        if not self.bluetooth.connected:
            self.show_popup("Uyarı", "Önce Bluetooth bağlantısı yapın")
            return
        
        self.scanning = True
        self.scan_progress = 0
        self.show_popup("Bilgi", "Tarama başlatıldı")
    
    def stop_scan(self):
        """Taramayı durdur"""
        self.scanning = False
        self.show_popup("Bilgi", "Tarama durduruldu")
    
    def on_data_received(self, value):
        """Bluetooth'tan veri alındığında"""
        if not self.scanning:
            return
        
        # Veriyi grid'e ekle
        continue_scan = self.grid_manager.add_data(value)
        
        # Heatmap'i güncelle
        self.ids.heatmap.grid_data = list(self.grid_manager.data.values())
        
        # İlerlemeyi güncelle
        self.scan_progress = self.grid_manager.scan_complete
        
        # Tarama tamamlandı mı?
        if not continue_scan:
            self.scanning = False
            self.show_popup("Tamamlandı", "Tarama tamamlandı!\n3D görüntü için butona tıklayın.")
            
            # Derinlikleri hesapla
            self.calculate_depths()
    
    def calculate_depths(self):
        """Tüm grid için derinlik hesapla"""
        self.depth_data = self.depth_calculator.calculate_grid_depths(
            self.grid_manager.data,
            self.grid_rows,
            self.grid_cols
        )
    
    def toggle_values(self):
        """Değer göster/gizle"""
        self.showing_values = not self.showing_values
        self.ids.heatmap.show_values = 1 if self.showing_values else 0
    
    def show_depth(self):
        """Derinlik değerlerini göster"""
        if not self.depth_data:
            self.calculate_depths()
        
        # Derinlik bilgisi popup'ı
        content = BoxLayout(orientation='vertical', spacing=5, padding=10)
        
        # Scroll view ile tüm değerleri göster
        scroll = ScrollView(size_hint=(1, 0.8))
        grid = GridLayout(cols=3, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        # Başlıklar
        grid.add_widget(Label(text="X", bold=True, color=get_color_from_hex('#4ecca3')))
        grid.add_widget(Label(text="Y", bold=True, color=get_color_from_hex('#4ecca3')))
        grid.add_widget(Label(text="Derinlik (m)", bold=True, color=get_color_from_hex('#4ecca3')))
        
        # Veriler
        for key, depth in self.depth_data.items():
            row, col = key.split(',')
            grid.add_widget(Label(text=str(col)))
            grid.add_widget(Label(text=str(row)))
            grid.add_widget(Label(text=f"{depth:.2f}"))
        
        scroll.add_widget(grid)
        content.add_widget(scroll)
        
        content.add_widget(Button(
            text="Kapat",
            size_hint_y=0.1,
            background_normal='',
            background_color=get_color_from_hex('#ff6b6b'),
            on_press=lambda x: popup.dismiss()
        ))
        
        popup = Popup(
            title="Derinlik Değerleri",
            content=content,
            size_hint=(0.8, 0.7)
        )
        popup.open()
    
    def show_3d(self):
        """3D yüzey görüntüleme"""
        if not self.grid_manager.data:
            self.show_popup("Uyarı", "Önce veri toplayın")
            return
        
        # 3D görüntüleme ekranına geç
        # Not: Kivy'de 3D için kivy.garden.graph veya pyopengl kullanılabilir
        # Bu örnekte basit bir popup gösteriyoruz
        self.show_popup("Bilgi", "3D görüntüleme modülü entegre edilecek\n(OpenGL ES 2.0)")
    
    def export_csv(self):
        """CSV export"""
        if not self.grid_manager.data:
            self.show_popup("Uyarı", "Dışa aktarılacak veri yok")
            return
        
        filename = self.data_io.export_to_csv(
            self.grid_manager.data,
            self.grid_rows,
            self.grid_cols,
            self.depth_data
        )
        
        self.show_popup("Başarılı", f"Veriler kaydedildi:\n{filename}")
    
    def import_csv(self):
        """CSV import"""
        filename = self.data_io.select_csv_file()
        
        if filename:
            data = self.data_io.import_from_csv(filename)
            
            if data:
                # Grid boyutlarını belirle
                max_row = max(item['row'] for item in data)
                max_col = max(item['col'] for item in data)
                
                self.grid_rows = max_row + 1
                self.grid_cols = max_col + 1
                
                # Grid manager'ı güncelle
                self.grid_manager.import_from_csv_data(data)
                
                # Heatmap'i güncelle
                self.ids.heatmap.rows = self.grid_rows
                self.ids.heatmap.cols = self.grid_cols
                self.ids.heatmap.grid_data = list(self.grid_manager.data.values())
                
                # Derinlikleri hesapla
                self.depth_data = {}
                for item in data:
                    if 'depth' in item and item['depth']:
                        key = f"{item['row']},{item['col']}"
                        self.depth_data[key] = item['depth']
                
                self.show_popup("Başarılı", "CSV yüklendi")
    
    def show_popup(self, title, message):
        """Popup göster"""
        popup = Popup(
            title=title,
            content=Label(text=message, color=get_color_from_hex('#ffffff')),
            size_hint=(0.6, 0.3)
        )
        popup.open()
    
    def go_back(self):
        """Ana menüye dön"""
        self.stop_scan()
        self.bluetooth.disconnect()
        self.manager.current = 'main_menu'