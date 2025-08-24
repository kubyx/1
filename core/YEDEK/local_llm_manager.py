"""
Yerel AI Model Yöneticisi - Ollama ve yerel GGUF modellerini yönetir
"""
import subprocess
import json
import logging
from pathlib import Path

class LocalLLMManager:
    def __init__(self):
        self.available_models = []
        self.current_model = None
        self.model_config = self.load_model_config()
        
    def load_model_config(self):
        """Model konfigürasyonunu yükle"""
        try:
            with open('config/ai_models.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Model konfigürasyon yükleme hatası: {e}")
            return {"ollama_models": [], "local_models": [], "vosk_models": []}
            
    def detect_models(self):
        """Mevcut modelleri tespit et"""
        self.available_models = []
        
        # Ollama modelleri
        ollama_models = self._detect_ollama_models()
        self.available_models.extend(ollama_models)
        
        # Yerel GGUF modelleri
        local_models = self._detect_local_models()
        self.available_models.extend(local_models)
        
        # VOSK modelleri
        vosk_models = self._detect_vosk_models()
        self.available_models.extend(vosk_models)
        
        logging.info(f"{len(self.available_models)} AI modeli tespit edildi")
        return self.available_models
        
    def _detect_ollama_models(self):
        """Ollama modellerini tespit et"""
        models = []
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # İlk satır başlık
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            models.append({
                                "type": "ollama",
                                "name": parts[0],
                                "size": parts[2] if len(parts) > 2 else "N/A",
                                "modified": parts[3] if len(parts) > 3 else "N/A",
                                "status": "available"
                            })
        except Exception as e:
            logging.warning(f"Ollama model tespit hatası: {e}")
            
        return models
        
    def _detect_local_models(self):
        """Yerel GGUF modellerini tespit et"""
        models = []
        try:
            for model_path in self.model_config.get("local_models", []):
                path_obj = Path(model_path)
                if path_obj.exists():
                    size_gb = path_obj.stat().st_size / (1024 ** 3)
                    models.append({
                        "type": "local",
                        "name": path_obj.name,
                        "path": str(path_obj),
                        "size": f"{size_gb:.1f}GB",
                        "status": "available"
                    })
                else:
                    models.append({
                        "type": "local",
                        "name": Path(model_path).name,
                        "path": model_path,
                        "size": "N/A",
                        "status": "not_found"
                    })
        except Exception as e:
            logging.error(f"Yerel model tespit hatası: {e}")
            
        return models
        
    def _detect_vosk_models(self):
        """VOSK modellerini tespit et"""
        models = []
        try:
            for model_path in self.model_config.get("vosk_models", []):
                path_obj = Path(model_path)
                if path_obj.exists() and path_obj.is_dir():
                    # VOSK model dosyalarını kontrol et
                    model_files = list(path_obj.glob("*.md"))
                    if model_files:
                        models.append({
                            "type": "vosk",
                            "name": path_obj.name,
                            "path": str(path_obj),
                            "status": "available",
                            "language": self._detect_vosk_language(path_obj.name)
                        })
                    else:
                        models.append({
                            "type": "vosk",
                            "name": path_obj.name,
                            "path": str(path_obj),
                            "status": "incomplete",
                            "language": "unknown"
                        })
                else:
                    models.append({
                        "type": "vosk",
                        "name": Path(model_path).name,
                        "path": model_path,
                        "status": "not_found",
                        "language": "unknown"
                    })
        except Exception as e:
            logging.error(f"VOSK model tespit hatası: {e}")
            
        return models
        
    def _detect_vosk_language(self, model_name):
        """VOSK model dilini tespit et"""
        model_name_lower = model_name.lower()
        if 'tr' in model_name_lower or 'turk' in model_name_lower:
            return "turkish"
        elif 'en' in model_name_lower or 'eng' in model_name_lower:
            return "english"
        elif 'de' in model_name_lower or 'ger' in model_name_lower:
            return "german"
        elif 'fr' in model_name_lower or 'fre' in model_name_lower:
            return "french"
        elif 'es' in model_name_lower or 'spa' in model_name_lower:
            return "spanish"
        else:
            return "unknown"
            
    def load_model(self, model_name):
        """Model yükle"""
        try:
            # Modeli listede bul
            model = None
            for m in self.available_models:
                if m["name"] == model_name and m["status"] == "available":
                    model = m
                    break
            
            if not model:
                logging.error(f"Model bulunamadı veya kullanılamaz: {model_name}")
                return False
                
            self.current_model = model
            logging.info(f"Model yüklendi: {model_name} ({model['type']})")
            return True
            
        except Exception as e:
            logging.error(f"Model yükleme hatası: {e}")
            return False
        
    def generate_response(self, prompt, max_tokens=500, temperature=0.7):
        """Yanıt oluştur"""
        if not self.current_model:
            return "Lütfen önce bir AI modeli seçin."
            
        try:
            if self.current_model["type"] == "ollama":
                return self._generate_ollama_response(prompt, max_tokens, temperature)
            elif self.current_model["type"] == "local":
                return self._generate_local_response(prompt)
            elif self.current_model["type"] == "vosk":
                return "VOSK modelleri ses tanıma için kullanılır, metin üretimi için değil."
            else:
                return "Bilinmeyen model türü."
                
        except Exception as e:
            logging.error(f"Yanıt oluşturma hatası: {e}")
            return f"Hata: {str(e)}"
            
    def _generate_ollama_response(self, prompt, max_tokens, temperature):
        """Ollama modeli ile yanıt oluştur"""
        try:
            cmd = [
                'ollama', 'run',
                self.current_model["name"],
                f"{prompt[:2000]}"  # Prompt'u sınırla
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=120,  # 2 dakika timeout
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Ollama hatası: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Yanıt oluşturma zaman aşımına uğradı. Lütfen daha kısa bir prompt deneyin."
        except Exception as e:
            return f"Ollama çalıştırma hatası: {str(e)}"
            
    def _generate_local_response(self, prompt):
        """Yerel model ile yanıt oluştur (basit implementasyon)"""
        # Burada gerçek bir GGUF model yükleyici entegre edilebilir
        # Şimdilik basit bir kural tabanlı yanıt sistemi
        
        prompt_lower = prompt.lower()
        
        # Sistem soruları
        if any(word in prompt_lower for word in ['sistem', 'system', 'cpu', 'bellek', 'memory', 'disk']):
            return self._get_system_status_response()
        
        # Hata soruları
        elif any(word in prompt_lower for word in ['hata', 'error', 'sorun', 'problem', 'çözüm']):
            return "Sistem hatası analizi için lütfen 'Hata Tara' sekmesini kullanın. Detaylı analiz yapabilirim."
        
        # Optimizasyon soruları
        elif any(word in prompt_lower for word in ['optimize', 'hızlandır', 'performans', 'iyileştir']):
            return "Sistem optimizasyonu için çeşitli araçlar sunuyorum. Bellek temizleme, disk birleştirme ve gereksiz process'leri sonlandırma gibi işlemler yapılabilir."
        
        # Genel yardım
        elif any(word in prompt_lower for word in ['yardım', 'help', 'nasıl', 'kullanım']):
            return "Size sistem yönetimi, sorun giderme, optimizasyon ve güvenlik konularında yardımcı olabilirim. Ne yapmak istediğinizi daha spesifik sorabilir misiniz?"
        
        # Selamlama
        elif any(word in prompt_lower for word in ['merhaba', 'hello', 'hi', 'selam']):
            return "Merhaba! SystemMasterAI asistanıyım. Sistem yönetimi ve sorun giderme konularında size nasıl yardımcı olabilirim?"
        
        # Default yanıt
        else:
            return "Anladım. İstediğiniz konuda size yardımcı olmak isterim. Lütfen daha detaylı bilgi verebilir misiniz? Sistem durumu, hata analizi veya optimizasyon gibi konularda destek sunabilirim."
    
    def _get_system_status_response(self):
        """Sistem durumu yanıtı oluştur"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk_usage = []
            
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage.append(f"{partition.device}: {usage.percent}%")
                except:
                    continue
            
            response = f"""
Sistem Durumu:
- CPU Kullanımı: {cpu_percent}%
- Bellek Kullanımı: {memory.percent}%
- Disk Kullanımı: {', '.join(disk_usage)}

Durum: {'✅ İyi' if cpu_percent < 80 and memory.percent < 80 else '⚠️ Dikkat' if cpu_percent < 90 and memory.percent < 90 else '❌ Kritik'}
"""
            return response.strip()
            
        except Exception as e:
            return f"Sistem durumu alınamadı: {str(e)}"
    
    def get_model_info(self, model_name):
        """Model bilgilerini getir"""
        for model in self.available_models:
            if model["name"] == model_name:
                return model
        return None
    
    def get_current_model(self):
        """Geçerli modeli getir"""
        return self.current_model
    
    def list_models_by_type(self, model_type):
        """Türe göre modelleri listele"""
        return [model for model in self.available_models if model["type"] == model_type and model["status"] == "available"]
    
    def is_model_available(self, model_name):
        """Modelin kullanılabilir olup olmadığını kontrol et"""
        for model in self.available_models:
            if model["name"] == model_name and model["status"] == "available":
                return True
        return False
