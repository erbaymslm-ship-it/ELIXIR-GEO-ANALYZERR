"""
ELIXIR TECHNOLOGY
Dinamik 2D Isı Haritası
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.graphics.texture import Texture
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.clock import Clock
import numpy as np
from kivy.core.image import Image
from PIL import Image as PILImage
import io

class HeatMapWidget(Widget):
    """
    Gerçek zamanlı 2D ısı haritası
    """
    
    grid_data = ListProperty([])
    rows = NumericProperty(5)
    cols = NumericProperty(5)
    show_values = NumericProperty(0)  # 0: gizli, 1: görünür
    texture = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(HeatMapWidget, self).__init__(**kwargs)
        self.data_matrix = np.zeros((5, 5))
        self.cell_size = 0
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.bind(grid_data=self.update_heatmap)
        self.bind(show_values=self.update_canvas)
    
    def update_heatmap(self, *args):
        """Grid verisi değiştiğinde ısı haritasını güncelle"""
        if not self.grid_data:
            return
        
        # Veri matrisini oluştur
        matrix = np.zeros((self.rows, self.cols))
        
        for item in self.grid_data:
            row = item.get('row', 0)
            col = item.get('col', 0)
            value = item.get('value', 0)
            
            if row < self.rows and col < self.cols:
                matrix[row][col] = value
        
        # Normalize et (0-255 arası)
        if np.max(matrix) > np.min(matrix):
            normalized = (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix)) * 255
        else:
            normalized = matrix * 255
        
        self.data_matrix = normalized.astype(np.uint8)
        self.update_canvas()
    
    def _get_color_for_value(self, value, normalized=True):
        """
        Değere göre RGB renk döndür
        Düşük: Mavi (0,0,255)
        Orta: Yeşil (0,255,0)
        Yüksek: Kırmızı (255,0,0)
        """
        if normalized:
            # 0-1 arası normalized değer
            if value < 0.33:
                # Mavi -> Yeşil
                t = value / 0.33
                return (0, int(255 * t), int(255 * (1 - t)))
            elif value < 0.66:
                # Yeşil -> Kırmızı
                t = (value - 0.33) / 0.33
                return (int(255 * t), int(255 * (1 - t)), 0)
            else:
                # Kırmızı (sabit)
                return (255, 0, 0)
        else:
            # Raw değer için
            if value < 341:
                t = value / 340
                return (0, int(255 * t), int(255 * (1 - t)))
            elif value < 682:
                t = (value - 341) / 340
                return (int(255 * t), int(255 * (1 - t)), 0)
            else:
                return (255, 0, 0)
    
    def update_canvas(self, *args):
        """Canvas'i güncelle"""
        if self.width == 0 or self.height == 0:
            return
        
        self.canvas.clear()
        
        with self.canvas:
            # Hücre boyutunu hesapla
            cell_width = self.width / self.cols
            cell_height = self.height / self.rows
            self.cell_size = min(cell_width, cell_height)
            
            # Izgara çiz
            Color(0.3, 0.3, 0.3, 1)
            
            # Dikey çizgiler
            for i in range(self.cols + 1):
                x = self.x + i * cell_width
                Line(points=[x, self.y, x, self.y + self.height], width=1)
            
            # Yatay çizgiler
            for i in range(self.rows + 1):
                y = self.y + i * cell_height
                Line(points=[self.x, y, self.x + self.width, y], width=1)
            
            # Hücreleri doldur
            for row in range(self.rows):
                for col in range(self.cols):
                    if row < len(self.data_matrix) and col < len(self.data_matrix[0]):
                        value = self.data_matrix[row][col]
                        
                        # Normalize değer (0-1)
                        if value > 0:
                            norm_value = value / 255.0
                        else:
                            norm_value = 0
                        
                        # Rengi al
                        r, g, b = self._get_color_for_value(norm_value, normalized=True)
                        
                        Color(r/255, g/255, b/255, 0.8)
                        
                        x = self.x + col * cell_width
                        y = self.y + (self.rows - 1 - row) * cell_height
                        
                        Rectangle(pos=(x, y), size=(cell_width - 2, cell_height - 2))
                        
                        # Değer gösterimi
                        if self.show_values == 1:
                            Color(1, 1, 1, 1)
                            from kivy.uix.label import Label
                            from kivy.core.text import Label as CoreLabel
                            
                            # Kısaca değer gösterimi için texture kullan
                            # Not: Gerçek uygulamada Label widget'ları daha uygun
                            label = CoreLabel(text=f"{int(value)}", font_size=12)
                            label.refresh()
                            texture = label.texture
                            
                            Rectangle(
                                texture=texture,
                                pos=(x + 5, y + 5),
                                size=texture.size
                            )