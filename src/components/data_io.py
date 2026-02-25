"""
ELIXIR TECHNOLOGY
CSV Import/Export Modülü
"""

import csv
import os
from datetime import datetime
from kivy.utils import platform
from kivy.logger import Logger
from kivy.storage.jsonstore import JsonStore

class DataIO:
    """
    CSV veri işlemleri
    """
    
    def __init__(self):
        self.store = None
        self.base_path = self._get_base_path()
        
        # Storage oluştur
        if self.base_path:
            store_path = os.path.join(self.base_path, 'elixir_data.json')
            self.store = JsonStore(store_path)
    
    def _get_base_path(self):
        """Platforma gore temel dizin"""
        if platform == 'android':
            try:
                from android.storage import primary_external_storage_path
                return primary_external_storage_path()
            except ImportError:
                return os.path.expanduser('~')
        elif platform == 'win':
            return os.path.expanduser('~\\Documents')
        else:
            return os.path.expanduser('~')
    
    def export_to_csv(self, grid_data, rows, cols, depth_data=None):
        """
        Grid verilerini CSV'ye aktar
        
        Args:
            grid_data: Grid veri sözlüğü
            rows: Satır sayısı
            cols: Sütun sayısı
            depth_data: Derinlik verileri (opsiyonel)
            
        Returns:
            str: Kaydedilen dosya yolu
        """
        if not grid_data:
            return None
        
        try:
            # Dosya adı oluştur
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"elixir_export_{timestamp}.csv"
            filepath = os.path.join(self.base_path, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Başlık satırı
                if depth_data:
                    writer.writerow(['X', 'Y', 'Z_Value', 'Depth_m'])
                else:
                    writer.writerow(['X', 'Y', 'Z_Value'])
                
                # Verileri yaz
                for key, item in grid_data.items():
                    row = item['row']
                    col = item['col']
                    value = item['value']
                    
                    if depth_data and key in depth_data:
                        writer.writerow([col, row, value, depth_data[key]])
                    else:
                        writer.writerow([col, row, value])
            
            Logger.info(f"CSV export: {filepath}")
            return filepath
            
        except Exception as e:
            Logger.error(f"CSV export hatası: {e}")
            return None
    
    def import_from_csv(self, filepath):
        """
        CSV'den veri yükle
        
        Args:
            filepath: CSV dosya yolu
            
        Returns:
            list: Veri listesi [{'row':r, 'col':c, 'value':v, 'depth':d}]
        """
        data = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                
                # Başlığı oku
                header = next(reader)
                
                # Sütun indekslerini belirle
                col_x = header.index('X') if 'X' in header else 0
                col_y = header.index('Y') if 'Y' in header else 1
                col_value = header.index('Z_Value') if 'Z_Value' in header else 2
                col_depth = header.index('Depth_m') if 'Depth_m' in header else None
                
                # Verileri oku
                for row in reader:
                    try:
                        item = {
                            'col': int(row[col_x]),
                            'row': int(row[col_y]),
                            'value': float(row[col_value])
                        }
                        
                        if col_depth is not None and len(row) > col_depth:
                            item['depth'] = float(row[col_depth])
                        
                        data.append(item)
                    except (ValueError, IndexError) as e:
                        Logger.warning(f"Satır atlandı: {row} - {e}")
            
            Logger.info(f"CSV import: {filepath} - {len(data)} kayıt")
            
        except Exception as e:
            Logger.error(f"CSV import hatası: {e}")
        
        return data
    
    def get_example_csv_path(self):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        example_path = os.path.join(assets_dir, 'ornek_veri.csv')
        if os.path.exists(example_path):
            return example_path
        return None

    def get_csv_files(self):
        files = []

        example_path = self.get_example_csv_path()
        if example_path:
            files.append({'name': 'Ornek Veri (ornek_veri.csv)', 'path': example_path})

        try:
            if self.base_path and os.path.exists(self.base_path):
                for f in sorted(os.listdir(self.base_path), reverse=True):
                    if f.endswith('.csv'):
                        full_path = os.path.join(self.base_path, f)
                        files.append({'name': f, 'path': full_path})
        except Exception as e:
            Logger.error(f"CSV dosya listeleme hatasi: {e}")

        return files

    def select_csv_file(self):
        csv_files = self.get_csv_files()
        if csv_files:
            return csv_files[0]['path']
        return None