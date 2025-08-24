"""
AI Entegrasyon Modülü - Yerel ve çevrimiçi AI modellerini yönetir
"""
import json
import logging
import subprocess
from pathlib import Path
from .local_llm_manager import LocalLLMManager

class AIIntegration:
    def __init__(self):
        self.local_manager = LocalLLMManager()
        self.current_model = None
        self.model_config = {}
        
    def load_models(self):
        """Tüm AI modellerini yükle"""
        try:
            # Model konfigürasyonunu yükle
            with open('config/ai_models.json', 'r', encoding='utf-8') as f:
                self.model_config = json.load(f)
            
            # Yerel modelleri tespit et
            available_models = self.local_manager.detect_models()
            logging.info(f"{len(available_models)} AI modeli tespit edildi")
            
            return available_models
            
        except Exception as e:
            logging.error(f"Model yükleme hatası: {e}")
            return []
    
    def set_model(self, model_name):
        """Aktif modeli ayarla"""
        try:
            success = self.local_manager.load_model(model_name)
            if success:
                self.current_model = model_name
                logging.info(f"Aktif model: {model_name}")
            return success
        except Exception as e:
            logging.error(f"Model ayarlama hatası: {e}")
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
            
            response = self.local_manager.generate_response(full_prompt)
            return response
            
        except Exception as e:
            logging.error(f"Yanıt oluşturma hatası: {e}")
            return f"Hata: {str(e)}"
    
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
        logging.info("AI entegrasyonu kapatıldı")
