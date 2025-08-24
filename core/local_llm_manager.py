"""
Yerel LLM Yöneticisi - Yerel AI modellerini yönetir
"""
import logging
import subprocess
import json
from pathlib import Path

class LocalLLMManager:
    def __init__(self):
        self.current_model = None
        self.model_process = None
        
    def detect_models(self):
        """Mevcut modelleri tespit et"""
        models = []
        
        try:
            # config/ai_models.json'dan modelleri yükle
            with open('config/ai_models.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Yerel modeller
            for model_path in config.get('local_models', []):
                if Path(model_path).exists():
                    model_name = Path(model_path).stem
                    models.append(f"Local - {model_name}")
                    
        except Exception as e:
            logging.error(f"Model tespit hatası: {e}")
            
        return models
    
    def load_model(self, model_name):
        """Model yükle"""
        try:
            # Model ismini temizle
            clean_name = model_name.replace("Local - ", "")
            
            # Model yolunu bul
            model_path = self.find_model_path(clean_name)
            if not model_path:
                logging.error(f"Model bulunamadı: {clean_name}")
                return False
                
            self.current_model = model_name
            logging.info(f"Yerel model yüklendi: {model_name}")
            return True
            
        except Exception as e:
            logging.error(f"Model yükleme hatası: {e}")
            return False
    
    def find_model_path(self, model_name):
        """Model dosya yolunu bul"""
        try:
            with open('config/ai_models.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            for model_path in config.get('local_models', []):
                if model_name in model_path:
                    return model_path
                    
            return None
        except Exception as e:
            logging.error(f"Model yol bulma hatası: {e}")
            return None
    
    def generate_response(self, prompt):
        """Yerel modelden yanıt oluştur"""
        # Basit simülasyon - gerçek implementasyon için llama.cpp veya benzeri kütüphane gerekli
        return f"Yerel model yanıtı: {prompt[:50]}... (Gerçek implementasyon için llama.cpp entegrasyonu gerekli)"
    
    def shutdown(self):
        """Modeli kapat"""
        if self.model_process:
            self.model_process.terminate()
        self.current_model = None
