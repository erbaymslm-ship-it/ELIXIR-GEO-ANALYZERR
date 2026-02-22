"""
ELIXIR TECHNOLOGY
Pointer Modu - Gerçek Zamanlı Gösterge
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty, ListProperty
from kivy.animation import Animation
from kivy.lang import Builder
from components.bluetooth_manager import BluetoothManager
from kivy.core.audio import SoundLoader
import math
import threading

KV_POINTER = '''
<PointerScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex('#1a1a2e')
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        
        # Başlık
        BoxLayout:
            size_hint_y: 0.1
            padding: [10, 5]
            
            Label:
                text: "POINTER MOD"
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
                text: "Bağlan"
                size_hint_x: 0.2
                background_normal: ''
                background_color: get_color_from_hex('#0f3460')
                on_press: root.connect_bluetooth()
        
        # Gösterge
        PointerGauge:
            id: gauge
            size_hint_y: 0.6
            value: root.current_value
        
        # Değer ve durum
        BoxLayout:
            size_hint_y: 0.25
            orientation: 'vertical'
            padding: [20, 10]
            spacing: 10
            
            Label:
                text: f"Değer: {root.current_value}"
                font_size: '24sp'
                bold: True
                color: root.get_text_color()
            
            Label:
                text: root.get_status_text()
                font_size: '18sp'
                color: root.get_text_color()
            
            ProgressBar:
                id: intensity_bar
                max: 1023
                value: root.current_value
                size_hint_y: 0.2
'''

Builder.load_string(KV_POINTER)

class PointerGauge(Widget):
    """
    Dairesel gösterge widget'ı
    """
    
    value = NumericProperty(0)
    pulse_scale = NumericProperty(1.0)
    
    def __init__(self, **kwargs):
        super(PointerGauge, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.bind(value=self.update_canvas)
        
        # Pulse animasyonu
        self.animate_pulse()
    
    def animate_pulse(self):
        """Pulse animasyonu"""
        anim = Animation(pulse_scale=1.2, duration=0.5) + Animation(pulse_scale=1.0, duration=0.5)
        anim.repeat = True
        anim.start(self)
    
    def update_canvas(self, *args):
        """Göstergeyi güncelle"""
        self.canvas.clear()
        
        with self.canvas:
            # Merkez ve yarıçap
            cx = self.center_x
            cy = self.center_y
            radius = min(self.width, self.height) * 0.4
            
            # Pulse efekti için scale
            scaled_radius = radius * self.pulse_scale
            
            # Değere göre renk
            r, g, b = self.get_color_for_value(self.value)
            
            # Dış daire
            Color(r, g, b, 0.3)
            Ellipse(pos=(cx - scaled_radius, cy - scaled_radius),
                   size=(scaled_radius * 2, scaled_radius * 2))
            
            # İç daire
            Color(r, g, b, 0.8)
            inner_radius = radius * 0.7
            Ellipse(pos=(cx - inner_radius, cy - inner_radius),
                   size=(inner_radius * 2, inner_radius * 2))
            
            # En iç daire
            Color(0.1, 0.1, 0.2, 1)
            core_radius = radius * 0.3
            Ellipse(pos=(cx - core_radius, cy - core_radius),
                   size=(core_radius * 2, core_radius * 2))
            
            # Değer göstergesi (doluluk)
            Color(r, g, b, 0.5)
            angle = (self.value / 1023) * 360
            from kivy.graphics import Mesh
            
            # Basit bir gösterge için çizgi
            import math
            end_x = cx + math.cos(math.radians(angle)) * radius * 0.9
            end_y = cy + math.sin(math.radians(angle)) * radius * 0.9
            
            Color(1, 1, 1, 1)
            Line(points=[cx, cy, end_x, end_y], width=3)
            
            # Merkez nokta
            Color(1, 1, 1, 1)
            Ellipse(pos=(cx - 5, cy - 5), size=(10, 10))
    
    def get_color_for_value(self, value):
        """Değere göre RGB renk döndür"""
        if value < 341:
            # Düşük -> Mavi
            t = value / 340
            return (0, t, 1 - t)
        elif value < 682:
            # Orta -> Yeşil
            t = (value - 341) / 340
            return (t, 1 - t, 0)
        else:
            # Yüksek -> Kırmızı
            t = (value - 682) / 341
            return (1, 0, t)

class PointerScreen(Screen):
    """
    Pointer modu ekranı
    """
    
    current_value = NumericProperty(0)
    beep_sound = None
    
    def __init__(self, **kwargs):
        super(PointerScreen, self).__init__(**kwargs)
        
        # Bluetooth yöneticisi
        self.bluetooth = BluetoothManager()
        self.bluetooth.data_callback = self.on_data_received
        
        # Sesler
        self.load_sounds()
        
        # Güncelleme
        Clock.schedule_interval(self.update_ui, 0.05)
        Clock.schedule_interval(self.update_beep, 0.1)
    
    def load_sounds(self):
        """Ses dosyalarını yükle"""
        # Not: Gerçek uygulamada ses dosyaları assets'e eklenmeli
        # Bu örnekte basit bip sesleri için dummy ses oluşturuyoruz
        try:
            self.low_beep = SoundLoader.load('assets/sounds/beep_low.wav')
            self.medium_beep = SoundLoader.load('assets/sounds/beep_medium.wav')
            self.high_beep = SoundLoader.load('assets/sounds/beep_high.wav')
        except:
            # Ses yoksa sessiz çalış
            self.low_beep = None
            self.medium_beep = None
            self.high_beep = None
    
    def on_enter(self):
        """Ekrana girildiğinde"""
        self.update_bluetooth_status()
    
    def update_ui(self, dt):
        """UI güncelleme"""
        if hasattr(self.ids, 'gauge'):
            self.ids.gauge.value = self.current_value
        
        if hasattr(self.ids, 'intensity_bar'):
            self.ids.intensity_bar.value = self.current_value
    
    def update_bluetooth_status(self):
        """Bluetooth durumunu güncelle"""
        if hasattr(self.ids, 'bt_status'):
            if self.bluetooth.connected:
                self.ids.bt_status.text = "Bluetooth: Bağlı"
                self.ids.bt_status.color = get_color_from_hex('#4ecca3')
            else:
                self.ids.bt_status.text = "Bluetooth: Bağlı değil"
                self.ids.bt_status.color = get_color_from_hex('#ff6b6b')
    
    def connect_bluetooth(self):
        """Bluetooth bağlantısı yap"""
        def connect_thread():
            devices = self.bluetooth.scan_devices()
            if devices:
                # İlk cihaza bağlan (veya kullanıcı seçimi yap)
                Clock.schedule_once(lambda dt: self.show_device_selection(devices))
            else:
                Clock.schedule_once(lambda dt: self.show_popup("Hata", "Cihaz bulunamadı"))
        
        threading.Thread(target=connect_thread).start()
    
    def show_device_selection(self, devices):
        """Cihaz seçim popup'ı"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        for device in devices:
            btn = Button(
                text=f"{device['name']}\n{device['address']}",
                size_hint_y=None,
                height=60,
                background_normal='',
                background_color=get_color_from_hex('#0f3460')
            )
            btn.bind(on_press=lambda x, addr=device['address']: self.do_connect(addr))
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
    
    def do_connect(self, address):
        """Cihaza bağlan"""
        success = self.bluetooth.connect(address)
        if success:
            self.show_popup("Başarılı", "Bluetooth bağlantısı kuruldu")
        else:
            self.show_popup("Hata", "Bağlantı kurulamadı")
        
        self.update_bluetooth_status()
    
    def on_data_received(self, value):
        """Bluetooth'tan veri alındığında"""
        self.current_value = value
        
        # Pulse hızını ayarla (değer arttıkça hızlanır)
        speed = 0.5 + (value / 1023) * 2.0
        if hasattr(self.ids, 'gauge'):
            self.ids.gauge.animate_pulse()
    
    def update_beep(self, dt):
        """Bip sesini güncelle"""
        if not self.bluetooth.connected or self.current_value == 0:
            return
        
        # Değere göre bip frekansı
        if self.current_value < 341:
            # Düşük - yavaş bip
            interval = 0.5
            sound = self.low_beep
        elif self.current_value < 682:
            # Orta - orta hız
            interval = 0.3
            sound = self.medium_beep
        else:
            # Yüksek - hızlı bip
            interval = 0.1
            sound = self.high_beep
        
        # Bip sesi çal
        if sound:
            sound.play()
    
    def get_text_color(self):
        """Değere göre metin rengi"""
        if self.current_value < 341:
            return get_color_from_hex('#4dabf7')
        elif self.current_value < 682:
            return get_color_from_hex('#51cf66')
        else:
            return get_color_from_hex('#ff6b6b')
    
    def get_status_text(self):
        """Durum metni"""
        if self.current_value < 341:
            return "DÜŞÜK"
        elif self.current_value < 682:
            return "ORTA"
        else:
            return "YÜKSEK"
    
    def show_popup(self, title, message):
        """Popup göster"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        popup = Popup(
            title=title,
            content=Label(text=message, color=get_color_from_hex('#ffffff')),
            size_hint=(0.6, 0.3)
        )
        popup.open()
    
    def go_back(self):
        """Ana menüye dön"""
        self.bluetooth.disconnect()
        self.manager.current = 'main_menu'