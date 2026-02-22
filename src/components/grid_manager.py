"""
ELIXIR TECHNOLOGY
Grid Oluşturma ve Yönetim
"""

from kivy.event import EventDispatcher
from kivy.properties import ListProperty, DictProperty, NumericProperty, StringProperty
import numpy as np
from enum import Enum

class ScanDirection(Enum):
    """Tarama yönü"""
    RIGHT = "right"
    LEFT = "left"

class ScanType(Enum):
    """Tarama tipi"""
    ZIGZAG = "zigzag"
    PARALLEL = "parallel"

class GridManager(EventDispatcher):
    """
    Grid oluşturma ve veri yönetimi
    """
    
    grid_size = ListProperty([5, 5])  # [rows, cols]
    data = DictProperty({})  # (row, col) -> value
    current_position = ListProperty([0, 0])  # [row, col]
    scan_complete = NumericProperty(0)  # 0-100 yüzde
    
    def __init__(self, **kwargs):
        super(GridManager, self).__init__(**kwargs)
        self.rows = 5
        self.cols = 5
        self.direction = ScanDirection.RIGHT
        self.scan_type = ScanType.ZIGZAG
        self.start_from = ScanDirection.RIGHT
        self.total_cells = 25
        self.filled_cells = 0
        self._reset_grid()
    
    def configure(self, rows=5, cols=5, direction=ScanDirection.RIGHT, 
                  scan_type=ScanType.ZIGZAG, start_from=ScanDirection.RIGHT):
        """Grid yapılandırması"""
        self.rows = rows
        self.cols = cols
        self.direction = direction
        self.scan_type = scan_type
        self.start_from = start_from
        self.total_cells = rows * cols
        self._reset_grid()
    
    def _reset_grid(self):
        """Grid'i sıfırla"""
        self.data = {}
        self.current_position = [0, 0]
        self.filled_cells = 0
        self.scan_complete = 0
        
        # Başlangıç pozisyonunu ayarla
        if self.start_from == ScanDirection.LEFT:
            self.current_position = [0, self.cols - 1]
    
    def get_next_position(self):
        """Bir sonraki grid pozisyonunu hesapla"""
        row, col = self.current_position
        
        if self.scan_type == ScanType.ZIGZAG:
            return self._get_next_zigzag(row, col)
        else:  # PARALLEL
            return self._get_next_parallel(row, col)
    
    def _get_next_zigzag(self, row, col):
        """Zigzag tarama için sonraki pozisyon"""
        # Çift satırlar sağa, tek satırlar sola
        if row % 2 == 0:  # Çift satır
            if col < self.cols - 1:
                return [row, col + 1]
            else:
                if row < self.rows - 1:
                    return [row + 1, col]
        else:  # Tek satır
            if col > 0:
                return [row, col - 1]
            else:
                if row < self.rows - 1:
                    return [row + 1, col]
        
        return None  # Tarama tamamlandı
    
    def _get_next_parallel(self, row, col):
        """Paralel tarama için sonraki pozisyon"""
        if self.direction == ScanDirection.RIGHT:
            if col < self.cols - 1:
                return [row, col + 1]
            else:
                if row < self.rows - 1:
                    return [row + 1, 0]
        else:  # LEFT
            if col > 0:
                return [row, col - 1]
            else:
                if row < self.rows - 1:
                    return [row + 1, self.cols - 1]
        
        return None
    
    def add_data(self, value):
        """Mevcut pozisyona veri ekle"""
        row, col = self.current_position
        
        # Veriyi kaydet
        pos_key = f"{row},{col}"
        self.data[pos_key] = {
            'value': value,
            'row': row,
            'col': col,
            'depth': None  # Derinlik sonra hesaplanacak
        }
        
        self.filled_cells += 1
        self.scan_complete = (self.filled_cells / self.total_cells) * 100
        
        # Sonraki pozisyona geç
        next_pos = self.get_next_position()
        if next_pos:
            self.current_position = next_pos
            return True  # Tarama devam ediyor
        else:
            return False  # Tarama tamamlandı
    
    def get_data_matrix(self):
        """Veri matrisini oluştur (numpy array)"""
        matrix = np.zeros((self.rows, self.cols))
        
        for key, item in self.data.items():
            row = item['row']
            col = item['col']
            matrix[row][col] = item['value']
        
        return matrix
    
    def get_normalized_matrix(self):
        """Normalize edilmiş veri matrisi (0-1 arası)"""
        matrix = self.get_data_matrix()
        
        if np.max(matrix) > np.min(matrix):
            normalized = (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix))
        else:
            normalized = matrix
            
        return normalized
    
    def import_from_csv_data(self, data_list):
        """CSV'den yüklenen veriyi import et"""
        self._reset_grid()
        
        for item in data_list:
            if 'row' in item and 'col' in item and 'value' in item:
                pos_key = f"{item['row']},{item['col']}"
                self.data[pos_key] = {
                    'value': item['value'],
                    'row': item['row'],
                    'col': item['col'],
                    'depth': item.get('depth')
                }
                self.filled_cells += 1
        
        self.scan_complete = (self.filled_cells / self.total_cells) * 100