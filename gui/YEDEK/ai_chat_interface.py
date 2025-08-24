"""
AI Chat Interface - AI sohbet arayüzü
"""
import tkinter as tk
from tkinter import scrolledtext
import customtkinter as ctk

class AIChatInterface(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Arayüzü kur"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Model seçimi
        model_frame = ctk.CTkFrame(main_frame)
        model_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(model_frame, text="AI Modeli:").pack(side="left", padx=5)
        
        self.model_var = tk.StringVar(value="Ollama - Llama3")
        model_combo = ctk.CTkComboBox(model_frame, 
                                    values=["Ollama - Llama3", "Ollama - Mistral", "Local - Phi2", "Local - Gemma"],
                                    variable=self.model_var,
                                    width=200)
        model_combo.pack(side="left", padx=5)
        
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
        
        # AI yanıtını simüle et
        self.after(1000, lambda: self.ai_response(message))
        
    def ai_response(self, user_message):
        """AI yanıtı oluştur"""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ['merhaba', 'selam', 'hello', 'hi']):
            response = "Merhaba! SystemMasterAI asistanıyım. Sistem yönetimi, optimizasyon ve sorun giderme konularında size yardımcı olabilirim."
        
        elif any(word in user_lower for word in ['sistem', 'system', 'cpu', 'bellek', 'memory']):
            response = "Sistem durumu iyi görünüyor. CPU kullanımı normal, bellek yeterli. Detaylı analiz için 'Sistem Analiz' butonunu kullanabilirsiniz."
        
        elif any(word in user_lower for word in ['hata', 'error', 'sorun', 'problem']):
            response = "Sistem hatası tespit edilmedi. Herhangi bir sorun yaşıyorsanız, 'Hata Tara' sekmesinden detaylı tarama yapabilirsiniz."
        
        elif any(word in user_lower for word in ['optimize', 'hızlandır', 'performans']):
            response = "Sistem optimizasyonu için şu önerileri sunabilirim:\n1. Gereksiz programları kapatın\n2. Disk temizliği yapın\n3. Başlangıç programlarını yönetin"
        
        else:
            response = "Anladım. Size sistem yönetimi konusunda nasıl yardımcı olabilirim? Performans optimizasyonu, sorun giderme veya güvenlik konularında destek sunabilirim."
        
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
        self.add_message("System", "🔍 Sistem analizi yapılıyor...")
        
        # Simüle analiz
        self.after(2000, lambda: self.show_analysis_result())
        
    def show_analysis_result(self):
        """Analiz sonucunu göster"""
        analysis = """
🤖 SİSTEM ANALİZ RAPORU
=======================

✅ PERFORMANS:
• CPU Kullanımı: Normal (%45)
• Bellek Kullanımı: İyi (%65) 
• Disk Durumu: Sağlıklı

✅ GÜVENLİK:
• Güvenlik duvarı: Aktif
• Antivirüs: Çalışıyor
• Şüpheli aktivite: Yok

💡 ÖNERİLER:
1. Son kullanıcı verilerini yedekleyin
2. Sistem güncellemelerini kontrol edin
3. Disk birleştirme yapın

🎯 SONRAKİ ADIMLAR:
• Detaylı tarama için 'Hata Tara' sekmesini kullanın
• Optimizasyon için 'Optimize Et' butonuna tıklayın
"""
        self.add_message("AI", analysis)
