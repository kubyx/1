"""
AI Entegrasyon Modülü - Yerel ve çevrimiçi AI modellerini yönetir
"""
import json
import logging
import subprocess
import requests
from pathlib import Path
from .local_llm_manager import LocalLLMManager

class AIIntegration:
    def __init__(self):
        self.local_manager = LocalLLMManager()
        self.current_model = None
        self.model_config = {}
        self.ollama_url = "http://localhost:11434"
        self.is_connected = False
        
    def load_models(self):
        """Tüm AI modellerini yükle"""
        try:
            # Model konfigürasyonunu yükle
            with open('config/ai_models.json', 'r', encoding='utf-8') as f:
                self.model_config = json.load(f)
            
            # Ollama bağlantısını kontrol et
            self.check_ollama_connection()
            
            # Yerel modelleri tespit et
            available_models = self.local_manager.detect_models()
            logging.info(f"{len(available_models)} AI modeli tespit edildi")
            
            return available_models
            
        except Exception as e:
            logging.error(f"Model yükleme hatası: {e}")
            return []
    
    def check_ollama_connection(self):
        """Ollama bağlantısını kontrol et"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.is_connected = True
                logging.info("Ollama bağlantısı başarılı")
                return True
        except Exception as e:
            logging.warning(f"Ollama bağlantı hatası: {e}")
            self.is_connected = False
        return False
    
    def set_model(self, model_name):
        """Aktif modeli ayarla"""
        try:
            # Ollama modeli mi kontrol et
            if model_name.startswith("Ollama - "):
                model_clean = model_name.replace("Ollama - ", "").lower()
                success = self.check_ollama_model(model_clean)
                if success:
                    self.current_model = model_name
                    logging.info(f"Aktif model: {model_name}")
                    return True
            else:
                # Yerel model
                success = self.local_manager.load_model(model_name)
                if success:
                    self.current_model = model_name
                    logging.info(f"Aktif model: {model_name}")
                    return True
            return False
        except Exception as e:
            logging.error(f"Model ayarlama hatası: {e}")
            return False
    
    def check_ollama_model(self, model_name):
        """Ollama modelinin var olup olmadığını kontrol et"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    if model_name in model.get('name', ''):
                        return True
            return False
        except Exception as e:
            logging.error(f"Model kontrol hatası: {e}")
            return False
    
    def generate_response(self, prompt, context=None):
        """AI yanıtı oluştur"""
        try:
            if not self.current_model:
                return "Lütfen önce bir AI modeli seçin."
            
            # Bağlamı prompt'a ekle
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nSoru: {prompt}"
            
            # Ollama modeli
            if self.current_model.startswith("Ollama - "):
                model_clean = self.current_model.replace("Ollama - ", "").lower()
                response = self.generate_ollama_response(model_clean, full_prompt)
            else:
                # Yerel model
                response = self.local_manager.generate_response(full_prompt)
            
            return response
            
        except Exception as e:
            logging.error(f"Yanıt oluşturma hatası: {e}")
            return f"Hata: {str(e)}"
    
    def generate_ollama_response(self, model_name, prompt):
        """Ollama API ile yanıt oluştur"""
        try:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_ctx": 4096
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Yanıt alınamadı')
            else:
                return f"API hatası: {response.status_code}"
                
        except Exception as e:
            return f"Ollama bağlantı hatası: {str(e)}"
    
    def analyze_system(self):
        """Sistem analizi yap"""
        system_info = self.get_system_status()
        prompt = f"""
        Aşağıdaki sistem bilgilerini analiz et ve olası sorunları, optimizasyon önerilerini,
        güvenlik açıklarını ve performans iyileştirmelerini listeleyerek detaylı bir rapor oluştur.
        
        Sistem Bilgileri:
        {system_info}
        
        Lütfen Türkçe olarak yanıt ver.
        """
        
        return self.generate_response(prompt)
    
    def get_system_status(self):
        """Sistem durum bilgilerini getir"""
        try:
            import psutil
            
            info = {
                "cpu_usage": f"{psutil.cpu_percent()}%",
                "memory_usage": f"{psutil.virtual_memory().percent}%",
                "disk_usage": [],
                "running_processes": len(list(psutil.process_iter())),
                "boot_time": psutil.boot_time()
            }
            
            # Disk kullanım bilgileri
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    info["disk_usage"].append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "percent": f"{usage.percent}%"
                    })
                except:
                    continue
            
            return str(info)
            
        except Exception as e:
            return f"Sistem bilgisi alınamadı: {e}"
    
    def shutdown(self):
        """AI sistemini kapat"""
        self.current_model = None
        self.is_connected = False
        logging.info("AI entegrasyonu kapatıldı")
