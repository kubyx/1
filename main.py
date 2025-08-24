#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SystemMasterAI - Gelişmiş Sistem Yönetim Asistanı
Windows 11 ve Linux için tam sistem kontrolü
"""

import os
import sys
import logging
import json
from pathlib import Path

# Encoding ayarları
if sys.platform == "win32":
    try:
        import win32console
        win32console.SetConsoleOutputCP(65001)  # UTF-8
    except:
        pass

# Önce gerekli kütüphaneleri kontrol et
try:
    import customtkinter as ctk
    import psutil
    from core.system_controller import SystemController
    from core.ai_integration import AIIntegration
    from core.error_handler import ErrorHandler
    from core.program_launcher import ProgramLauncher
    from core.local_llm_manager import LocalLLMManager
    from core.process_manager import ProcessManager
    from core.security_monitor import SecurityMonitor
    from core.voice_control import VoiceControl
    from core.backup_manager import BackupManager
    from core.plugin_loader import PluginLoader
    from gui.main_window import MainWindow
except ImportError as e:
    print(f"Gerekli kütüphane eksik: {e}")
    print("Lütfen 'pip install -r requirements.txt' komutunu çalıştırın")
    sys.exit(1)

class SystemMasterAI:
    def __init__(self):
        self.setup_logging()
        self.load_config()
        self.init_components()
        self.create_gui()
        
    def setup_logging(self):
        """Loglama sistemini kur"""
        log_dir = "data/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Türkçe karakterleri İngilizce'ye çeviren formatter
        class TurkishSafeFormatter(logging.Formatter):
            def format(self, record):
                message = super().format(record)
                turkish_to_english = {
                    'ş': 's', 'ğ': 'g', 'ü': 'u', 'ö': 'o', 
                    'ç': 'c', 'ı': 'i', 'Ş': 'S', 'Ğ': 'G',
                    'Ü': 'U', 'Ö': 'O', 'Ç': 'C', 'İ': 'I'
                }
                for turkish, english in turkish_to_english.items():
                    message = message.replace(turkish, english)
                return message
        
        # Handler'ları oluştur
        file_handler = logging.FileHandler(os.path.join(log_dir, 'system_master.log'), encoding='utf-8')
        stream_handler = logging.StreamHandler()
        
        # Formatter'ı ayarla
        formatter = TurkishSafeFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        
        # Logger'ı ayarla
        self.logger = logging.getLogger('SystemMasterAI')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        
        self.logger.info("SystemMasterAI baslatiliyor...")
        
    def load_config(self):
        """Konfigürasyon yükle"""
        self.config = {}
        try:
            config_path = "config/settings.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # Varsayılan config
                self.config = {
                    "theme": "dark",
                    "language": "tr",
                    "auto_backup": True,
                    "backup_interval": 24,
                    "auto_update": False,
                    "voice_feedback": True,
                    "ai_model": "local",
                    "system_monitoring": True,
                    "security_scan_interval": 3600,
                    "error_check_interval": 300
                }
                # Config dosyasını kaydet
                os.makedirs("config", exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                    
        except Exception as e:
            self.logger.error(f"Config yukleme hatasi: {e}")
            
    def init_components(self):
        """Bileşenleri başlat"""
        self.logger.info("Bilesenler baslatiliyor...")
        
        self.system_controller = SystemController()
        self.ai_integration = AIIntegration()
        self.error_handler = ErrorHandler()
        self.program_launcher = ProgramLauncher()
        self.process_manager = ProcessManager()
        self.security_monitor = SecurityMonitor()
        self.voice_control = VoiceControl()
        self.backup_manager = BackupManager()
        self.plugin_loader = PluginLoader()
        self.local_llm_manager = LocalLLMManager()
        
        # AI modellerini yükle
        self.ai_integration.load_models()
        
        # Plugin'leri yükle
        self.loaded_plugins = self.plugin_loader.load_plugins()
        
        self.logger.info(f"{len(self.loaded_plugins)} plugin yuklendi")
        
    def create_gui(self):
        """GUI'yi oluştur"""
        self.logger.info("GUI olusturuluyor...")
        self.gui = MainWindow(self)
        
        # Sistem izlemeyi başlat
        self.start_system_monitoring()
        
    def start_system_monitoring(self):
        """Sistem izlemeyi başlat"""
        self.logger.info("Sistem izleme baslatiliyor...")
        
        # Başlangıç sistem bilgilerini al
        system_info = self.system_controller.get_system_info()
        self.logger.info(f"Sistem bilgileri alindi: {system_info['platform']}")
        
        # İlk hata taraması
        initial_errors = self.error_handler.scan_errors("quick")
        if initial_errors:
            self.logger.warning(f"Baslangicta {len(initial_errors)} hata tespit edildi")
        
    def run(self):
        """Uygulamayı çalıştır"""
        self.logger.info("Uygulama calistiriliyor...")
        try:
            self.gui.run()
        except Exception as e:
            self.logger.error(f"Uygulama hatasi: {e}")
            raise
            
    def shutdown(self):
        """Uygulamayı kapat"""
        self.logger.info("Uygulama kapatiliyor...")
        
        # Kaynakları serbest bırak
        if hasattr(self, 'ai_integration'):
            self.ai_integration.shutdown()
            
        if hasattr(self, 'plugin_loader'):
            for plugin_name in list(self.plugin_loader.plugins.keys()):
                self.plugin_loader.unload_plugin(plugin_name)
                
        # GUI'yi kapat
        if hasattr(self, 'gui'):
            self.gui.shutdown()
            
        self.logger.info("SystemMasterAI basariyla kapatildi")
            
def main():
    """Ana fonksiyon"""
    try:
        app = SystemMasterAI()
        app.run()
    except Exception as e:
        logging.error(f"Uygulama hatasi: {e}")
        print(f"Uygulama hatasi: {e}")
        
if __name__ == "__main__":
    main()
