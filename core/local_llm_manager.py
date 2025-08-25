"""
Yerel LLM Yöneticisi - Tüm Yerel AI Çatılarını ve Modelleri Yönetir
"""
import logging
import subprocess
import json
import requests
import time
import sys
import os
from pathlib import Path
from functools import wraps

def retry_on_timeout(max_retries=3, delay=2):
    """Timeout durumunda yeniden deneme dekoratörü"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Timeout, {delay} saniye bekleniyor... (Deneme {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        self.logger.error("Timeout hatası: Maksimum deneme sayısı aşıldı")
                        raise
            return wrapper
        return decorator
    return decorator

class LocalLLMManager:
    def __init__(self):
        self.current_model = None
        self.current_backend = None
        self.backend_urls = {
            'ollama': 'http://localhost:11434',
            'gpt4all': 'http://localhost:4891',
            'lmstudio': 'http://localhost:1234'
        }
        self.timeout = 30
        self.logger = logging.getLogger('SystemMasterAI')
        self.available_backends = []
        self.vosk_models = []
        self.all_models = []  # TÜM modellerin listesi
        self.load_config()
        self.detect_backends()
        self.scan_all_models()  # TÜM modelleri tara
        
    def load_config(self):
        """Konfigürasyon dosyasını yükle"""
        try:
            config_path = Path('config/ai_models.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.vosk_models = config.get('vosk_models', [])
            else:
                self.logger.warning("ai_models.json bulunamadı")
        except Exception as e:
            self.logger.error(f"Config yükleme hatası: {e}")
    
    def detect_backends(self):
        """Mevcut AI çatılarını tespit et"""
        self.available_backends = []
        
        # Ollama kontrol
        try:
            response = requests.get(f"{self.backend_urls['ollama']}/api/tags", timeout=3)
            if response.status_code == 200:
                self.available_backends.append('ollama')
                self.logger.info("✓ Ollama tespit edildi")
        except:
            pass
        
        # GPT4All kontrol
        try:
            response = requests.get(f"{self.backend_urls['gpt4all']}/v1/models", timeout=3)
            if response.status_code == 200:
                self.available_backends.append('gpt4all')
                self.logger.info("✓ GPT4All tespit edildi")
        except:
            # GPT4All kurulu mu?
            gpt4all_paths = [
                "C:/Users/Master/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/GPT4All/GPT4All.lnk",
                "C:/Program Files/GPT4All/gpt4all.exe",
                os.path.expanduser("~/AppData/Local/Programs/GPT4All/gpt4all.exe")
            ]
            for path in gpt4all_paths:
                if Path(path).exists():
                    self.available_backends.append('gpt4all')
                    self.logger.info("✓ GPT4All kurulu")
                    break
        
        # LM Studio kontrol
        try:
            response = requests.get(f"{self.backend_urls['lmstudio']}/v1/models", timeout=3)
            if response.status_code == 200:
                self.available_backends.append('lmstudio')
                self.logger.info("✓ LM Studio tespit edildi")
        except:
            # LM Studio kurulu mu?
            lmstudio_paths = [
                "C:/ProgramData/Microsoft/Windows/Start Menu/Programs/LM Studio/LM Studio.lnk",
                "C:/Program Files/LM Studio/lm-studio.exe",
                os.path.expanduser("~/AppData/Local/Programs/LM Studio/lm-studio.exe")
            ]
            for path in lmstudio_paths:
                if Path(path).exists():
                    self.available_backends.append('lmstudio')
                    self.logger.info("✓ LM Studio kurulu")
                    break
        
        if not self.available_backends:
            self.logger.warning("Hiçbir AI çatısı tespit edilemedi")

    def scan_all_models(self):
        """TÜM model dosyalarını otomatik tara"""
        self.all_models = []
        
        # 1. Ollama Modelleri
        if 'ollama' in self.available_backends:
            try:
                response = requests.get(f"{self.backend_urls['ollama']}/api/tags", timeout=5)
                if response.status_code == 200:
                    ollama_models = response.json().get('models', [])
                    for model in ollama_models:
                        self.all_models.append(f"Ollama - {model['name']}")
            except:
                pass
        
        # 2. TÜM GGUF Dosyalarını Tara (Tüm diskleri ara)
        gguf_extensions = ['.gguf', '.bin', '.model']
        search_paths = [
            "C:/Users/Master/Documents/LLM/",
            "C:/Users/Master/AppData/Local/nomic.ai/GPT4All/",
            "C:/Users/Master/AppData/Local/LM Studio/",
            "C:/Users/Master/Desktop/SystemMasterAI/data/models/",
            "C:/Users/Master/Documents/",  # Tüm Documents klasörü
            "D:/", "E:/", "F:/"  # Diğer sürücüler
        ]
        
        for base_path in search_paths:
            if Path(base_path).exists():
                try:
                    for ext in gguf_extensions:
                        for gguf_file in Path(base_path).rglob(f"*{ext}"):
                            model_name = gguf_file.stem
                            model_path = str(gguf_file)
                            # Benzersiz model ismi oluştur
                            model_id = f"Local - {model_name} [{model_path}]"
                            self.all_models.append(model_id)
                except Exception as e:
                    self.logger.warning(f"{base_path} taranırken hata: {e}")
        
        # 3. Config'deki modeller
        try:
            config_path = Path('config/ai_models.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    for model_name in config.get('local_models', []):
                        model_id = f"Config - {model_name}"
                        if model_id not in self.all_models:
                            self.all_models.append(model_id)
        except Exception as e:
            self.logger.error(f"Config modelleri yükleme hatası: {e}")
        
        self.logger.info(f"Toplam {len(self.all_models)} model tespit edildi")

    def find_gguf_file(self, model_identifier):
        """Model identifier'dan GGUF dosya yolunu bul"""
        # Eğer zaten tam yol içeriyorsa
        if model_identifier.startswith('C:/') and Path(model_identifier).exists():
            return model_identifier
        
        # Model isminden yol oluştur
        model_name = model_identifier.split('[')[0].replace('Config - ', '').replace('Local - ', '').strip()
        
        search_paths = [
            "C:/Users/Master/Documents/LLM/",
            "C:/Users/Master/AppData/Local/nomic.ai/GPT4All/",
            "C:/Users/Master/AppData/Local/LM Studio/",
            "C:/Users/Master/Desktop/SystemMasterAI/data/models/"
        ]
        
        possible_files = [
            f"{model_name}.Q4_0.gguf",
            f"{model_name}.gguf",
            f"{model_name}-Q4_0.gguf",
            f"{model_name}.bin",
            model_name
        ]
        
        for base_path in search_paths:
            for file in possible_files:
                full_path = base_path + file if not file.startswith("C:/") else file
                if Path(full_path).exists():
                    return full_path
        
        return None

    def detect_models(self):
        """Tüm tespit edilen modelleri döndür"""
        return self.all_models
    
    def load_model(self, model_name):
        """Model yükle"""
        try:
            self.current_model = model_name
            
            if model_name.startswith("Ollama - "):
                self.current_backend = 'ollama'
            elif model_name.startswith("Config - "):
                # Config'deki modeller için otomatik backend seç
                if 'ollama' in self.available_backends:
                    self.current_backend = 'ollama'
                elif 'gpt4all' in self.available_backends:
                    self.current_backend = 'gpt4all'
                elif 'lmstudio' in self.available_backends:
                    self.current_backend = 'lmstudio'
                else:
                    self.current_backend = None
            else:
                # Local GGUF dosyaları için
                self.current_backend = 'ollama'  # Ollama GGUF'ları destekler
            
            self.logger.info(f"Model seçildi: {model_name} ({self.current_backend})")
            return True
            
        except Exception as e:
            self.logger.error(f"Model yükleme hatası: {e}")
            return False
    
    @retry_on_timeout()
    def generate_response(self, prompt):
        """Tüm AI çatılarından yanıt oluştur"""
        try:
            if not self.current_model or not self.current_backend:
                return "Lütfen önce bir model ve backend seçin."
            
            # Model ismini temizle
            clean_name = self.current_model.replace("Ollama - ", "").replace("Config - ", "").replace("Local - ", "")
            
            if self.current_backend == 'ollama':
                # GGUF dosya yolunu bul
                if self.current_model.startswith("Local - ") or self.current_model.startswith("Config - "):
                    model_path = self.find_gguf_file(clean_name)
                    if not model_path:
                        return f"GGUF dosyası bulunamadı: {clean_name}"
                    model_param = model_path
                else:
                    model_param = clean_name
                
                payload = {
                    "model": model_param,
                    "prompt": prompt,
                    "stream": False
                }
                
                response = requests.post(
                    f"{self.backend_urls['ollama']}/api/generate",
                    json=payload,
                    timeout=20
                )
                
            elif self.current_backend in ['gpt4all', 'lmstudio']:
                # GPT4All/LM Studio API
                payload = {
                    "model": clean_name,
                    "prompt": prompt,
                    "max_tokens": 500,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    f"{self.backend_urls[self.current_backend]}/v1/completions",
                    json=payload,
                    timeout=20
                )
            
            if response.status_code == 200:
                result = response.json()
                if self.current_backend == 'ollama':
                    return result.get("response", "Yanıt alınamadı")
                else:
                    return result.get("choices", [{}])[0].get("text", "Yanıt alınamadı")
            else:
                return f"Hata: {response.status_code} - {response.text[:100]}..."
                
        except requests.exceptions.Timeout:
            return "AI çatısı yanıt vermedi. Lütfen servisi kontrol edin."
        except requests.exceptions.ConnectionError:
            # Servis çalışmıyor, başlatmayı dene
            if self.start_backend(self.current_backend):
                time.sleep(5)
                return "Servis başlatıldı, lütfen tekrar deneyin."
            else:
                return f"{self.current_backend} başlatılamadı. Lütfen manuel başlatın."
        except Exception as e:
            return f"Hata oluştu: {str(e)[:100]}..."
    
    def start_backend(self, backend_name):
        """AI çatısını başlat"""
        try:
            if backend_name == 'gpt4all':
                gpt4all_paths = [
                    "C:/Program Files/GPT4All/gpt4all.exe",
                    os.path.expanduser("~/AppData/Local/Programs/GPT4All/gpt4all.exe")
                ]
                for path in gpt4all_paths:
                    if Path(path).exists():
                        subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        self.logger.info("GPT4All başlatılıyor...")
                        return True
            
            elif backend_name == 'lmstudio':
                lmstudio_paths = [
                    "C:/Program Files/LM Studio/lm-studio.exe",
                    os.path.expanduser("~/AppData/Local/Programs/LM Studio/lm-studio.exe")
                ]
                for path in lmstudio_paths:
                    if Path(path).exists():
                        subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        self.logger.info("LM Studio başlatılıyor...")
                        return True
            
            elif backend_name == 'ollama':
                return self.start_ollama_service()
            
            return False
            
        except Exception as e:
            self.logger.error(f"{backend_name} başlatma hatası: {e}")
            return False

    def start_ollama_service(self):
        """Ollama servisini başlat"""
        try:
            self.logger.info("Ollama servisi başlatılıyor...")
            if sys.platform == "win32":
                subprocess.Popen(["ollama", "serve"], 
                               creationflags=subprocess.CREATE_NO_WINDOW,
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["ollama", "serve"],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            
            for i in range(5):
                time.sleep(2)
                try:
                    response = requests.get(f"{self.backend_urls['ollama']}/api/tags", timeout=3)
                    if response.status_code == 200:
                        self.logger.info("✓ Ollama servisi başlatıldı")
                        return True
                except:
                    continue
            
            self.logger.error("Ollama servisi başlatılamadı")
            return False
            
        except Exception as e:
            self.logger.error(f"Ollama başlatma hatası: {e}")
            return False

    def get_vosk_models(self):
        """VOSK modellerini listeler"""
        return self.vosk_models
    
    def get_vosk_model_path(self, model_name):
        """Belirtilen VOSK modelinin yolunu döndürür"""
        for model_path in self.vosk_models:
            if model_name in model_path:
                return model_path
        return None
    
    def shutdown(self):
        """Tüm çatıları kapat"""
        self.current_model = None
        self.current_backend = None
