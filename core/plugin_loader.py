"""
Plugin Yükleyici - Dinamik plugin yükleme sistemi
"""
import importlib.util
import os
import json
import logging
from pathlib import Path

class PluginLoader:
    def __init__(self):
        self.plugins = {}
        self.plugin_dir = "plugins"
        
    def load_plugins(self):
        """Tüm plugin'leri yükle"""
        loaded_plugins = []
        
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir, exist_ok=True)
            return loaded_plugins
            
        # Plugin dizinlerini tara
        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            
            if os.path.isdir(plugin_path):
                # Dizin şeklindeki plugin'ler
                main_file = os.path.join(plugin_path, '__init__.py')
                if os.path.exists(main_file):
                    plugin = self._load_plugin_from_path(main_file, item)
                    if plugin:
                        loaded_plugins.append(plugin)
                        
            elif item.endswith('.py') and item != '__init__.py':
                # Tek dosyalı plugin'ler
                plugin = self._load_plugin_from_path(plugin_path, item[:-3])
                if plugin:
                    loaded_plugins.append(plugin)
                    
        return loaded_plugins
        
    def _load_plugin_from_path(self, file_path, plugin_name):
        """Dosya yolundan plugin yükle"""
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Plugin sınıfını bul (PluginName veya Plugin şeklinde)
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    attr.__module__ == module.__name__ and
                    hasattr(attr, 'initialize')):
                    plugin_class = attr
                    break
                    
            if plugin_class:
                plugin_instance = plugin_class(self)
                if hasattr(plugin_instance, 'initialize'):
                    plugin_instance.initialize()
                    
                self.plugins[plugin_name] = plugin_instance
                logging.info(f"Plugin yüklendi: {plugin_name}")
                return plugin_instance
                
            logging.warning(f"Plugin sınıfı bulunamadı: {plugin_name}")
            return None
            
        except Exception as e:
            logging.error(f"Plugin yükleme hatası ({plugin_name}): {e}")
            return None
            
    def get_plugin(self, plugin_name):
        """Belirli bir plugin'i getir"""
        return self.plugins.get(plugin_name)
        
    def get_all_plugins(self):
        """Tüm plugin'leri getir"""
        return self.plugins
        
    def unload_plugin(self, plugin_name):
        """Plugin'i kaldır"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if hasattr(plugin, 'shutdown'):
                plugin.shutdown()
            del self.plugins[plugin_name]
            logging.info(f"Plugin kaldırıldı: {plugin_name}")
            return True
        return False
        
    def execute_plugin_command(self, plugin_name, command, *args):
        """Plugin komutu çalıştır"""
        plugin = self.get_plugin(plugin_name)
        if plugin and hasattr(plugin, 'execute_command'):
            return plugin.execute_command(command, *args)
        return None
        
    def get_plugin_info(self, plugin_name):
        """Plugin bilgilerini getir"""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return {
                'name': getattr(plugin, 'name', plugin_name),
                'version': getattr(plugin, 'version', '1.0.0'),
                'description': getattr(plugin, 'description', ''),
                'author': getattr(plugin, 'author', 'Unknown')
            }
        return None
