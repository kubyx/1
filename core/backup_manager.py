"""
Yedekleme Yöneticisi - Sistem yedekleme ve geri yükleme
"""
import os
import json
import shutil
import zipfile
import logging
from datetime import datetime
from pathlib import Path

class BackupManager:
    def __init__(self):
        self.backup_dir = "data/backups"
        self.restore_dir = "data/restore"
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.restore_dir, exist_ok=True)
        
    def create_backup(self, backup_name, backup_type="full", include_items=None):
        """Yedekleme oluştur"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"{backup_name}_{timestamp}")
            os.makedirs(backup_path, exist_ok=True)
            
            # Metadata
            metadata = {
                'name': backup_name,
                'type': backup_type,
                'created_at': datetime.now().isoformat(),
                'items': include_items or [],
                'system_info': self._get_system_info()
            }
            
            with open(os.path.join(backup_path, 'metadata.json'), 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)
            
            # Yedekleme işlemi
            if backup_type == "full":
                self._backup_system_files(backup_path)
            elif backup_type == "custom" and include_items:
                self._backup_custom_items(backup_path, include_items)
            
            # ZIP'e paketle
            zip_path = f"{backup_path}.zip"
            self._create_zip(backup_path, zip_path)
            
            # Geçici dizini temizle
            shutil.rmtree(backup_path)
            
            logging.info(f"Yedekleme oluşturuldu: {zip_path}")
            return zip_path
            
        except Exception as e:
            logging.error(f"Yedekleme hatası: {e}")
            return None
            
    def _backup_system_files(self, backup_path):
        """Sistem dosyalarını yedekle"""
        backup_items = [
            # Sistem ayarları
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Roaming'),
            
            # Belgeler
            os.path.join(os.environ.get('USERPROFILE', ''), 'Documents'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
            
            # Yapılandırma dosyaları
            'config',
            'data'
        ]
        
        for item in backup_items:
            if os.path.exists(item):
                dest_path = os.path.join(backup_path, os.path.basename(item))
                if os.path.isdir(item):
                    shutil.copytree(item, dest_path)
                else:
                    shutil.copy2(item, dest_path)
                    
    def _backup_custom_items(self, backup_path, items):
        """Özel öğeleri yedekle"""
        for item in items:
            if os.path.exists(item):
                dest_path = os.path.join(backup_path, os.path.basename(item))
                if os.path.isdir(item):
                    shutil.copytree(item, dest_path)
                else:
                    shutil.copy2(item, dest_path)
                    
    def _create_zip(self, source_dir, zip_path):
        """ZIP dosyası oluştur"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
                    
    def _get_system_info(self):
        """Sistem bilgilerini getir"""
        import psutil
        
        return {
            'platform': os.name,
            'cpu_cores': psutil.cpu_count(),
            'total_memory': psutil.virtual_memory().total,
            'disks': [partition.device for partition in psutil.disk_partitions()],
            'backup_time': datetime.now().isoformat()
        }
        
    def list_backups(self):
        """Yedeklemeleri listele"""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.zip'):
                file_path = os.path.join(self.backup_dir, file)
                backups.append({
                    'name': file,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path))
                })
        
        return backups
        
    def restore_backup(self, backup_path, restore_path=None):
        """Yedeklemeyi geri yükle"""
        try:
            if restore_path is None:
                restore_path = self.restore_dir
                
            # ZIP'i aç
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_path)
                
            # Metadata'yı oku
            metadata_path = os.path.join(restore_path, 'metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                logging.info(f"Yedekleme geri yüklendi: {metadata['name']}")
                return metadata
                
            return None
            
        except Exception as e:
            logging.error(f"Geri yükleme hatası: {e}")
            return None
            
    def delete_backup(self, backup_path):
        """Yedeklemeyi sil"""
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                logging.info(f"Yedekleme silindi: {backup_path}")
                return True
            return False
        except Exception as e:
            logging.error(f"Yedekleme silme hatası: {e}")
            return False
