"""
Plugin Şablonu - Yeni plugin'ler için temel yapı
"""
import json
import logging

class PluginTemplate:
    def __init__(self, app):
        self.app = app
        self.name = "PluginTemplate"
        self.version = "1.0.0"
        self.description = "Örnek plugin açıklaması"
        self.config = {}
        
    def initialize(self):
        """Plugin'i başlat"""
        self.load_config()
        logging.info(f"{self.name} plugin initialized")
        return self
        
    def shutdown(self):
        """Plugin'i kapat"""
        self.save_config()
        logging.info(f"{self.name} plugin shutdown")
        
    def load_config(self):
        """Konfigürasyon yükle"""
        try:
            config_path = f"data/plugins/{self.name}.json"
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {}
            
    def save_config(self):
        """Konfigürasyon kaydet"""
        try:
            config_path = f"data/plugins/{self.name}.json"
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error(f"Config save error: {e}")
            
    def get_gui_component(self):
        """GUI bileşeni döndür"""
        return None
        
    def execute_command(self, command, *args):
        """Komut çalıştır"""
        return f"Command executed: {command}"
