"""
ELIXIR TECHNOLOGY
Derinlik Hesaplama Modülü

Formül: r = -3H / (dH/dr)
dH/dr = (H1 - H2) / sensor_mesafesi
"""

import numpy as np
from kivy.logger import Logger

class DepthCalculator:
    """
    Manyetik gradyometre verilerinden derinlik hesaplama
    """
    
    def __init__(self, sensor_distance=0.5):
        """
        Args:
            sensor_distance: Sensörler arası mesafe (metre)
        """
        self.sensor_distance = sensor_distance  # metre
        self.gradiometer_mode = True  # True: gradyometre, False: manyometre
    
    def calculate_depth(self, H1, H2=None):
        """
        Derinlik hesapla
        
        Args:
            H1: Birinci sensör değeri (veya tek sensör değeri)
            H2: İkinci sensör değeri (gradyometre modunda)
            
        Returns:
            float: Hesaplanan derinlik (metre)
        """
        try:
            if self.gradiometer_mode and H2 is not None:
                # Gradyometre modu
                dH = H1 - H2
                if dH == 0:
                    return 0
                
                dH_dr = dH / self.sensor_distance
                H = (H1 + H2) / 2  # Ortalama alan
                
                # r = -3H / (dH/dr)
                depth = abs(-3 * H / dH_dr)
                
                # Mantıklı aralıkta mı?
                if depth > 1000:  # 1km'den fazla derinlik mantıksız
                    depth = depth / 1000  # Birim düzeltmesi
                
                return depth
            else:
                # Manyometre modu (yarı nicel yaklaşım)
                # Yarım dalga boyu yöntemi veya diğer yaklaşımlar
                # Basit bir yaklaşım: değer büyüdükçe derinlik azalır
                if H1 == 0:
                    return 0
                
                # Varsayılan derinlik hesaplama
                # Not: Gerçek uygulamada kalibrasyon gerektirir
                depth = 1000 / (abs(H1) + 1)
                return depth
                
        except Exception as e:
            Logger.error(f"Derinlik hesaplama hatası: {e}")
            return 0
    
    def calculate_grid_depths(self, grid_data, rows, cols):
        """
        Grid'deki tüm hücreler için derinlik hesapla
        
        Args:
            grid_data: Grid veri sözlüğü
            rows: Satır sayısı
            cols: Sütun sayısı
            
        Returns:
            dict: Derinlik verileri
        """
        depth_data = {}
        
        for key, item in grid_data.items():
            if self.gradiometer_mode:
                # Her hücre için çevresindeki değerlerle gradyan hesapla
                row = item['row']
                col = item['col']
                H1 = item['value']
                
                # Komşu hücrelerle gradyan hesapla
                depths = []
                
                # Sağ komşu
                if col < cols - 1:
                    right_key = f"{row},{col+1}"
                    if right_key in grid_data:
                        H2 = grid_data[right_key]['value']
                        depths.append(self.calculate_depth(H1, H2))
                
                # Sol komşu
                if col > 0:
                    left_key = f"{row},{col-1}"
                    if left_key in grid_data:
                        H2 = grid_data[left_key]['value']
                        depths.append(self.calculate_depth(H1, H2))
                
                # Alt komşu
                if row < rows - 1:
                    down_key = f"{row+1},{col}"
                    if down_key in grid_data:
                        H2 = grid_data[down_key]['value']
                        depths.append(self.calculate_depth(H1, H2))
                
                # Üst komşu
                if row > 0:
                    up_key = f"{row-1},{col}"
                    if up_key in grid_data:
                        H2 = grid_data[up_key]['value']
                        depths.append(self.calculate_depth(H1, H2))
                
                # Ortalama derinlik
                if depths:
                    depth_data[key] = sum(depths) / len(depths)
                else:
                    depth_data[key] = self.calculate_depth(H1)
            else:
                # Manyometre modu
                depth_data[key] = self.calculate_depth(item['value'])
        
        return depth_data