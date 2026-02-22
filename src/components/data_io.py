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
        """Platforma göre temel dizin"""
        if platform == 'android':
            from android.storage import primary_external_storage_path
            return primary_external_storage_path()
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
    
    def select_csv_file(self):
        """
        CSV dosyası seçme dialog'u
        
        Returns:
            str: Seçilen dosya yolu veya None
        """
        # Android'de file chooser kullan
        if platform == 'android':
            from android.activity import result_callback
            from android import activity
            import android.content.Intent as Intent
            import android.net.Uri as Uri
            
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("text/csv")
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            
            # Result callback
            def on_activity_result(request_code, result_code, intent):
                if result_code == activity.RESULT_OK and intent:
                    uri = intent.getData()
                    # URI'den dosya yolunu al
                    # Not: Android'de content:// URI'leri için özel işlem gerekir
                    return uri.getPath()
                return None
            
            result_callback(on_activity_result)
            activity.startActivityForResult(intent, 1001)
            return None
        else:
            # Geliştirme ortamında simüle et
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            filepath = filedialog.askopenfilename(
                title="CSV Dosyası Seç",
                filetypes=[("CSV files", "*.csv")]
            )
            
            return filepath if filepath else None