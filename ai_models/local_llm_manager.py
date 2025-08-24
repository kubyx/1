"""
Yerel AI Model Yöneticisi
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
            with open('config/ai_models.json', 'r') as f:
                return json.load(f)
        except:
            return {"ollama_models": [], "local_models": [], "vosk_models": []}
            
    def detect_models(self):
        """Mevcut modelleri tespit et"""
        self.available_models = []
        
        # Ollama modelleri
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            for line in result.stdout.split('\n')[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        self.available_models.append({
                            "type": "ollama",
                            "name": parts[0],
                            "size": parts[2] if len(parts) > 2 else "N/A"
                        })
        except:
            pass
            
        # Yerel GGUF modelleri
        for model_path in self.model_config.get("local_models", []):
            if Path(model_path).exists():
                self.available_models.append({
                    "type": "local",
                    "name": Path(model_path).name,
                    "path": model_path,
                    "size": f"{Path(model_path).stat().st_size / 1024**3:.1f}GB"
                })
                
        return self.available_models
        
    def load_model(self, model_name):
        """Model yükle"""
        for model in self.available_models:
            if model["name"] == model_name:
                self.current_model = model
                logging.info(f"Model loaded: {model_name}")
                return True
        return False
        
    def generate_response(self, prompt, max_tokens=500):
        """Yanıt oluştur"""
        if not self.current_model:
            return "No model loaded. Please select a model first."
            
        if self.current_model["type"] == "ollama":
            return self._generate_ollama_response(prompt, max_tokens)
        else:
            return self._generate_local_response(prompt)
            
    def _generate_ollama_response(self, prompt, max_tokens):
        """Ollama modeli ile yanıt oluştur"""
        try:
            result = subprocess.run([
                'ollama', 'run', self.current_model["name"],
                prompt[:2000]  # Prompt'u sınırla
            ], capture_output=True, text=True, timeout=30)
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"
            
    def _generate_local_response(self, prompt):
        """Yerel model ile yanıt oluştur"""
        # Basit yerel yanıt mekanizması
        responses = {
            "system": "Sistem durumu normal. Performans iyi seviyede.",
            "error": "Sistem hatası tespit edildi. Detaylı analiz önerilir.",
            "help": "Size nasıl yardımcı olabilirim? Sistem yönetimi, optimizasyon veya sorun giderme için destek sunabilirim."
        }
        
        prompt_lower = prompt.lower()
        for key in responses:
            if key in prompt_lower:
                return responses[key]
                
        return "Anladım. İstediğiniz işlemi gerçekleştirebilirim. Detaylı bilgi verebilir misiniz?"
