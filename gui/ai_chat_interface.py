"""
AI Chat Interface - AI sohbet arayüzü
"""
import tkinter as tk
from tkinter import scrolledtext
import customtkinter as ctk
import threading
import time

class AIChatInterface(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.ai_integration = None
        self.setup_ui()
        
    def setup_ui(self):
        """Arayüzü kur"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Model seçimi
        model_frame = ctk.CTkFrame(main_frame)
        model_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(model_frame, text="AI Modeli:").pack(side="left", padx=5)
        
        # Gerçek model listesi
        self.model_var = tk.StringVar(value="Ollama - wizardcoder:7b-python")
        model_options = [
            "Ollama - wizardcoder:7b-python",
            "Ollama - wizardcoder:latest", 
            "Ollama - phi:latest",
            "Local - Llama-3.2-1B",
            "Local - phi-2",
            "Local - mistral-7b",
            "Local - llama-3-8b",
            "Local - gemma-2-2b"
        ]
        
        model_combo = ctk.CTkComboBox(model_frame, 
                                    values=model_options,
                                    variable=self.model_var,
                                    width=250)
        model_combo.pack(side="left", padx=5)
        
        # Model yükleme butonu
        ctk.CTkButton(model_frame, text="🔄 Modeli Yükle", 
                     command=self.load_model, width=120).pack(side="left", padx=5)
        
        # Bağlantı durumu
        self.status_label = ctk.CTkLabel(model_frame, text="🔴 Bağlantı Yok", 
                                       text_color="red")
        self.status_label.pack(side="right", padx=5)
        
        ctk.CTkButton(model_frame, text="🎤 Sesli Giriş", command=self.toggle_voice, width=100).pack(side="right", padx=5)
        ctk.CTkButton(model_frame, text="🔍 Sistem Analiz", command=self.analyze_system, width=100).pack(side="right", padx=5)
        
        # Sohbet alanı
        chat_frame = ctk.CTkFrame(main_frame)
        chat_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.chat_text = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, font=("Arial", 11))
        self.chat_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.chat_text.config(state="disabled")
        
        # İlk mesaj
        self.add_message("System", "Merhaba! SystemMasterAI asistanıyım. Size nasıl yardımcı olabilirim?")
        
        # Giriş alanı
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x")
        
        self.input_entry = ctk.CTkEntry(input_frame, placeholder_text="Mesajınızı yazın...")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.input_entry.bind("<Return>", self.send_message)
        
        ctk.CTkButton(input_frame, text="Gönder", command=self.send_message, width=80).pack(side="right", padx=5)
        ctk.CTkButton(input_frame, text="Temizle", command=self.clear_chat, width=80).pack(side="right", padx=5)
        
        # AI entegrasyonunu başlat
        self.after(1000, self.initialize_ai)
        
    def initialize_ai(self):
        """AI entegrasyonunu başlat"""
        try:
            from core.ai_integration import AIIntegration
            self.ai_integration = AIIntegration()
            models = self.ai_integration.load_models()
            
            if self.ai_integration.is_connected:
                self.status_label.configure(text="🟢 Ollama Bağlı", text_color="green")
            else:
                self.status_label.configure(text="🟡 Yerel Modeller", text_color="orange")
                
            self.add_message("System", f"AI sistemi hazır. {len(models)} model tespit edildi.")
            
        except Exception as e:
            self.status_label.configure(text="🔴 AI Hatası", text_color="red")
            self.add_message("System", f"AI başlatma hatası: {str(e)}")
        
    def add_message(self, sender, message):
        """Mesaj ekle"""
        self.chat_text.config(state="normal")
        self.chat_text.insert("end", f"\n{sender}: {message}\n")
        self.chat_text.config(state="disabled")
        self.chat_text.see("end")
        
    def send_message(self, event=None):
        """Mesaj gönder"""
        message = self.input_entry.get().strip()
        if not message:
            return
            
        self.add_message("Siz", message)
        self.input_entry.delete(0, "end")
        
        # AI yanıtını thread'de oluştur
        threading.Thread(target=self.generate_ai_response, args=(message,), daemon=True).start()
        
    def generate_ai_response(self, user_message):
        """AI yanıtı oluştur (thread'de)"""
        if not self.ai_integration:
            self.add_message("AI", "AI sistemi hazır değil. Lütfen bekleyin...")
            return
            
        # Yanıtın gelmekte olduğunu göster
        self.add_message("AI", "🤔 Düşünüyorum...")
        
        try:
            response = self.ai_integration.generate_response(user_message)
            self.after(0, lambda: self.show_ai_response(response))
        except Exception as e:
            self.after(0, lambda: self.show_ai_response(f"Hata: {str(e)}"))
        
    def show_ai_response(self, response):
        """AI yanıtını göster"""
        # "Düşünüyorum" mesajını sil
        self.chat_text.config(state="normal")
        self.chat_text.delete("end-2l", "end")
        self.chat_text.config(state="disabled")
        
        self.add_message("AI", response)
        
    def load_model(self):
        """Model yükle"""
        model_name = self.model_var.get()
        if not self.ai_integration:
            self.add_message("System", "AI sistemi hazır değil.")
            return
            
        self.add_message("System", f"Model yükleniyor: {model_name}")
        
        success = self.ai_integration.set_model(model_name)
        if success:
            self.add_message("System", f"✅ Model başarıyla yüklendi: {model_name}")
        else:
            self.add_message("System", f"❌ Model yüklenemedi: {model_name}")
        
    def clear_chat(self):
        """Sohbeti temizle"""
        self.chat_text.config(state="normal")
        self.chat_text.delete("1.0", "end")
        self.chat_text.config(state="disabled")
        self.add_message("System", "Sohbet temizlendi. Size nasıl yardımcı olabilirim?")
        
    def toggle_voice(self):
        """Sesli girişi aç/kapat"""
        self.add_message("System", "Sesli giriş özelliği aktif edilecek...")
        
    def analyze_system(self):
        """Sistem analizi yap"""
        if not self.ai_integration:
            self.add_message("System", "AI sistemi hazır değil.")
            return
            
        self.add_message("System", "🔍 Sistem analizi yapılıyor...")
        
        # Analizi thread'de yap
        threading.Thread(target=self.perform_system_analysis, daemon=True).start()
        
    def perform_system_analysis(self):
        """Sistem analizi yap (thread'de)"""
        try:
            analysis = self.ai_integration.analyze_system()
            self.after(0, lambda: self.add_message("AI", analysis))
        except Exception as e:
            self.after(0, lambda: self.add_message("AI", f"Analiz hatası: {str(e)}"))
