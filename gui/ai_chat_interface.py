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
        
        # Butonlar
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(button_frame, text="🎤 Sesli Giriş", command=self.toggle_voice, width=100).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="🔍 Sistem Analiz", command=self.analyze_system, width=100).pack(side="right", padx=5)
        
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
            
            # Ana pencereden backend bilgisini al
            backend = self.parent.backend_var.get()
            is_connected = self.ai_integration.check_backend_connection(backend)
            
            if is_connected:
                self.add_message("System", f"{backend} bağlantısı başarılı.")
            else:
                self.add_message("System", f"{backend} bağlantısı yok. Varsayılan modeller kullanılacak.")
                
        except Exception as e:
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
            # Ana pencereden model bilgisini al
            backend = self.parent.backend_var.get()
            model_name = self.parent.model_var.get()
            full_model_name = f"{backend} - {model_name}"
            
            # Modeli ayarla
            self.ai_integration.set_model(full_model_name)
            
            # Yanıtı oluştur
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
