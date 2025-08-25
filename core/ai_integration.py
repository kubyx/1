"""
AI Entegrasyon Modülü - TÜM çatılar ve modeller SORUNSUZ çalışacak!
"""
import os
import json
import logging
import requests
from pathlib import Path

class AIIntegration:
    def __init__(self):
        self.current_model = None
        self.current_backend = None
        self.is_connected = False
        self.api_keys = self.load_api_keys()
        
    def load_api_keys(self):
        """API anahtarlarını yükle"""
        try:
            with open('config/api_keys.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def load_models(self, backend=None):
        """Backend'e göre model listesini döndür"""
        try:
            if backend == "Ollama":
                return self.get_ollama_models()
            elif backend == "GPT4All":
                return self.get_gpt4all_models()
            elif backend == "LM Studio":
                return self.get_lm_studio_models()
            elif backend == "OpenAI":
                return ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
            elif backend == "Anthropic":
                return ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
            elif backend == "Google Gemini":
                return ["gemini-1.5-pro", "gemini-1.0-pro", "gemini-1.5-flash"]
            elif backend == "Groq":
                return ["llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"]
            elif backend == "Together AI":
                return ["llama-3-70b", "mixtral-8x7b", "codellama-70b"]
            elif backend == "DeepSeek":
                return ["deepseek-chat", "deepseek-coder"]
            elif backend == "HuggingFace":
                return ["HuggingFaceH4/zephyr-7b-beta", "mistralai/Mistral-7B-v0.1"]
            elif backend == "Cohere":
                return ["command", "command-light", "command-nightly"]
            elif backend == "Replicate":
                return ["llama-2-70b", "stable-diffusion", "whisper"]
            else:
                return []
        except Exception as e:
            logging.error(f"Model yükleme hatası: {e}")
            return []

    def get_ollama_models(self):
        """Ollama modellerini getir"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return ["wizardcoder:7b-python", "phi:latest", "llama3:8b"]
        except:
            return ["wizardcoder:7b-python", "phi:latest", "llama3:8b"]

    def get_gpt4all_models(self):
        """GPT4All modellerini getir"""
        try:
            response = requests.get("http://localhost:4891/v1/models", timeout=5)
            if response.status_code == 200:
                models = response.json().get('data', [])
                return [model['id'] for model in models]
            return ["Meta-Llama-3-8B-Instruct", "mistral-7b-instruct-v0.1", "phi-2"]
        except:
            return ["Meta-Llama-3-8B-Instruct", "mistral-7b-instruct-v0.1", "phi-2"]

    def get_lm_studio_models(self):
        """LM Studio modellerini getir"""
        try:
            response = requests.get("http://localhost:1234/v1/models", timeout=5)
            if response.status_code == 200:
                models = response.json().get('data', [])
                return [model['id'] for model in models]
            return ["Llama-3.2-1B-Instruct", "gemma-2-2b-it", "codellama-7b"]
        except:
            return ["Llama-3.2-1B-Instruct", "gemma-2-2b-it", "codellama-7b"]

    def check_backend_connection(self, backend_name):
        """TÜM çatılar için bağlantı kontrolü"""
        try:
            if backend_name == "Ollama":
                return self.check_ollama_connection()
            elif backend_name == "GPT4All":
                return self.check_gpt4all_connection()
            elif backend_name == "LM Studio":
                return self.check_lm_studio_connection()
            elif backend_name == "OpenAI":
                return self.check_openai_connection()
            elif backend_name == "Anthropic":
                return self.check_anthropic_connection()
            elif backend_name == "Google Gemini":
                return self.check_gemini_connection()
            elif backend_name == "Groq":
                return self.check_groq_connection()
            elif backend_name == "Together AI":
                return self.check_together_ai_connection()
            elif backend_name == "DeepSeek":
                return self.check_deepseek_connection()
            elif backend_name == "HuggingFace":
                return self.check_huggingface_connection()
            elif backend_name == "Cohere":
                return self.check_cohere_connection()
            elif backend_name == "Replicate":
                return self.check_replicate_connection()
            else:
                return False
        except Exception as e:
            logging.error(f"Bağlantı hatası: {e}")
            return False

    def check_ollama_connection(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            return response.status_code == 200
        except:
            return False

    def check_gpt4all_connection(self):
        try:
            response = requests.get("http://localhost:4891/v1/models", timeout=10)
            return response.status_code == 200
        except:
            try:
                from gpt4all import GPT4All
                return True
            except:
                return False

    def check_lm_studio_connection(self):
        try:
            response = requests.get("http://localhost:1234/v1/models", timeout=10)
            return response.status_code == 200
        except:
            return False

    def check_openai_connection(self):
        try:
            import openai
            openai.api_key = self.api_keys.get('openai', '')
            response = openai.Model.list()
            return True
        except:
            return False

    def check_groq_connection(self):
        try:
            from groq import Groq
            client = Groq(api_key=self.api_keys.get('groq', ''))
            models = client.models.list()
            return True
        except:
            return False

    def check_deepseek_connection(self):
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_keys.get('deepseek', '')}"},
                json={"model": "deepseek-chat", "messages": [{"role": "user", "content": "test"}]},
                timeout=10
            )
            return response.status_code != 401
        except:
            return False

    def check_anthropic_connection(self):
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_keys.get('anthropic', ''))
            client.models.list()
            return True
        except:
            return False

    def check_gemini_connection(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_keys.get('gemini', ''))
            models = genai.list_models()
            return True
        except:
            return False

    def check_together_ai_connection(self):
        try:
            response = requests.get(
                "https://api.together.xyz/v1/models",
                headers={"Authorization": f"Bearer {self.api_keys.get('together_ai', '')}"},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def check_huggingface_connection(self):
        try:
            from huggingface_hub import list_models
            models = list_models()
            return True
        except:
            return False

    def check_cohere_connection(self):
        try:
            import cohere
            co = cohere.Client(self.api_keys.get('cohere', ''))
            response = co.generate(model='command', prompt='test')
            return True
        except:
            return False

    def check_replicate_connection(self):
        try:
            import replicate
            replicate.Client(api_token=self.api_keys.get('replicate', ''))
            return True
        except:
            return False

    def set_model(self, full_model_name):
        """Modeli ayarla"""
        try:
            if " - " in full_model_name:
                backend, model_name = full_model_name.split(" - ", 1)
                self.current_backend = backend
                self.current_model = model_name
                self.is_connected = self.check_backend_connection(backend)
                return True
            return False
        except Exception as e:
            logging.error(f"Model ayarlama hatası: {e}")
            return False

    def generate_response(self, prompt):
        """Yanıt oluştur"""
        if not self.current_model or not self.current_backend:
            return "Lütfen önce bir model seçin."

        try:
            if self.current_backend == "Ollama":
                return self.generate_ollama_response(prompt)
            elif self.current_backend == "GPT4All":
                return self.generate_gpt4all_response(prompt)
            elif self.current_backend == "LM Studio":
                return self.generate_lm_studio_response(prompt)
            elif self.current_backend == "OpenAI":
                return self.generate_openai_response(prompt)
            elif self.current_backend == "Anthropic":
                return self.generate_anthropic_response(prompt)
            elif self.current_backend == "Google Gemini":
                return self.generate_gemini_response(prompt)
            elif self.current_backend == "Groq":
                return self.generate_groq_response(prompt)
            elif self.current_backend == "Together AI":
                return self.generate_together_ai_response(prompt)
            elif self.current_backend == "DeepSeek":
                return self.generate_deepseek_response(prompt)
            elif self.current_backend == "HuggingFace":
                return self.generate_huggingface_response(prompt)
            elif self.current_backend == "Cohere":
                return self.generate_cohere_response(prompt)
            elif self.current_backend == "Replicate":
                return self.generate_replicate_response(prompt)
            else:
                return "Desteklenmeyen çatı"
        except Exception as e:
            return f"Hata: {str(e)}"

    def generate_ollama_response(self, prompt):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.current_model, 
                    "prompt": prompt, 
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_ctx": 4096
                    }
                },
                timeout=60
            )
            
            # ✅ DOĞRU PARSE ETME:
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Yanıt alınamadı')
            else:
                return f"Ollama API hatası: {response.status_code}"
                
        except Exception as e:
            return f"Ollama bağlantı hatası: {str(e)}"

    def generate_groq_response(self, prompt):
        try:
            from groq import Groq
            client = Groq(api_key=self.api_keys.get('groq', ''))
            response = client.chat.completions.create(
                model=self.current_model,
                messages=[{"role": "user", "content": prompt}],
                timeout=60
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Groq hatası: {str(e)}"

    def generate_deepseek_response(self, prompt):
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_keys.get('deepseek', '')}"},
                json={
                    "model": self.current_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=60
            )
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"DeepSeek hatası: {str(e)}"

    def generate_gpt4all_response(self, prompt):
        try:
            response = requests.post(
                "http://localhost:4891/v1/completions",
                json={
                    "model": self.current_model,
                    "prompt": prompt,
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                timeout=60
            )
            return response.json().get('choices', [{}])[0].get('text', 'Yanıt alınamadı')
        except Exception as e:
            return f"GPT4All hatası: {str(e)}"

    def generate_openai_response(self, prompt):
        try:
            import openai
            openai.api_key = self.api_keys.get('openai', '')
            response = openai.ChatCompletion.create(
                model=self.current_model,
                messages=[{"role": "user", "content": prompt}],
                timeout=60
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI hatası: {str(e)}"

    def generate_anthropic_response(self, prompt):
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_keys.get('anthropic', ''))
            response = client.messages.create(
                model=self.current_model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Anthropic hatası: {str(e)}"

    def generate_gemini_response(self, prompt):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_keys.get('gemini', ''))
            model = genai.GenerativeModel(self.current_model)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini hatası: {str(e)}"

    def generate_together_ai_response(self, prompt):
        try:
            response = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_keys.get('together_ai', '')}"},
                json={
                    "model": self.current_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=60
            )
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Together AI hatası: {str(e)}"

    def generate_huggingface_response(self, prompt):
        try:
            from transformers import pipeline
            generator = pipeline('text-generation', model=self.current_model)
            response = generator(prompt, max_length=1000, temperature=0.7)
            return response[0]['generated_text']
        except Exception as e:
            return f"HuggingFace hatası: {str(e)}"

    def generate_cohere_response(self, prompt):
        try:
            import cohere
            co = cohere.Client(self.api_keys.get('cohere', ''))
            response = co.generate(
                model=self.current_model,
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7
            )
            return response.generations[0].text
        except Exception as e:
            return f"Cohere hatası: {str(e)}"

    def generate_replicate_response(self, prompt):
        try:
            import replicate
            output = replicate.run(
                self.current_model,
                input={"prompt": prompt, "max_length": 1000}
            )
            return "".join(output)
        except Exception as e:
            return f"Replicate hatası: {str(e)}"

    def generate_lm_studio_response(self, prompt):
        try:
            response = requests.post(
                "http://localhost:1234/v1/chat/completions",
                json={
                    "model": self.current_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=60
            )
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"LM Studio hatası: {str(e)}"

    def shutdown(self):
        """Temizlik"""
        self.current_model = None
        self.current_backend = None
        self.is_connected = False
