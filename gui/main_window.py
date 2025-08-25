"""
Ana Pencere - Temel GUI yapısı
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import threading  # ✅ EKLENDİ
from .dashboard import Dashboard
from .system_tabs import SystemTabs
from .ai_chat_interface import AIChatInterface
from .plugin_manager_ui import PluginManagerUI
from .error_fix_ui import ErrorFixUI
from .resource_monitor import ResourceMonitor
from .programs_tab import ProgramsTab
from .kernel_tab import KernelTab

class MainWindow:
    def __init__(self, app):
        self.app = app
        self.root = ctk.CTk()
        self.root.title("SystemMasterAI - Ultimate Control Center")
        
        # Ekran çözünürlüğünü al
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Pencere boyutunu ekrana göre optimize et
        window_width = min(1200, screen_width - 100)
        window_height = min(800, screen_height - 100)
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(1000, 600)
        self.root.maxsize(screen_width, screen_height)
        self.root.resizable(True, True)
        
        self.center_window()
        self.setup_theme()
        self.create_widgets()
        
    def center_window(self):
        """Pencereyi ekran ortasına al"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_theme(self):
        """Tema ayarlarını yap"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
    def create_widgets(self):
        """Arayüz bileşenlerini oluştur"""
        # Ana çerçeve
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 📍 ÜST SOL KONTROL ÇERÇEVESİ
        self.create_ai_control_frame()
        
        # Sekme kontrolü
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Sekmeleri oluştur
        self.create_tabs()
        self.create_status_bar()
        
    def create_ai_control_frame(self):
        """📍 ÜST SOL TARAFTA AI KONTROL ÇERÇEVESİ"""
        control_frame = ctk.CTkFrame(self.main_frame, height=40)
        control_frame.pack(fill="x", padx=10, pady=5, anchor="nw")
        control_frame.pack_propagate(False)
        
        # Çatı seçimi
        ctk.CTkLabel(control_frame, text="Çatı:").pack(side="left", padx=5)
        self.backend_var = tk.StringVar(value="Ollama")
        
        # 🌟 ÜCRETSİZ BULUT AI'LER
        backend_options = [
            "Ollama", "GPT4All", "LM Studio", 
            "OpenAI", "Anthropic", "Google Gemini", 
            "Groq", "Together AI", "HuggingFace",
            "Cohere", "Replicate", "DeepSeek"
        ]
        
        backend_combo = ctk.CTkComboBox(control_frame, 
                                      values=backend_options,
                                      variable=self.backend_var,
                                      width=120,
                                      command=self.on_backend_change)
        backend_combo.pack(side="left", padx=5)
        
        # Model seçimi
        ctk.CTkLabel(control_frame, text="Model:").pack(side="left", padx=5)
        self.model_var = tk.StringVar(value="wizardcoder:7b-python")
        self.model_dropdown = ctk.CTkComboBox(control_frame, 
                                            values=self.get_models_for_backend("Ollama"),
                                            variable=self.model_var,
                                            width=180)
        self.model_dropdown.pack(side="left", padx=5)
        
        # Model yükleme butonu
        ctk.CTkButton(control_frame, text="🔄 Yükle", 
                     command=self.load_model, width=80).pack(side="left", padx=5)
        
        # Bağlantı kontrol butonu
        ctk.CTkButton(control_frame, text="🔗 Bağlantı", 
                     command=self.check_connection, width=80).pack(side="left", padx=5)
        
        # Durum göstergesi
        self.ai_status_label = ctk.CTkLabel(control_frame, text="🟢 Hazır", 
                                         text_color="green", font=ctk.CTkFont(size=11))
        self.ai_status_label.pack(side="left", padx=10)
        
    def get_models_for_backend(self, backend_name):
        """Backend'e göre model listesi"""
        models = {
            "Ollama": ["wizardcoder:7b-python", "wizardcoder:latest", "phi:latest", "llama3:8b"],
            "GPT4All": ["Meta-Llama-3-8B-Instruct", "mistral-7b-instruct-v0.1", "phi-2"],
            "LM Studio": ["Llama-3.2-1B-Instruct", "gemma-2-2b-it", "codellama-7b"],
            "OpenAI": ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            "Anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "Google Gemini": ["gemini-1.5-pro", "gemini-1.0-pro", "gemini-1.5-flash"],
            "Groq": ["llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
            "Together AI": ["llama-3-70b", "mixtral-8x7b", "codellama-70b"],
            "HuggingFace": ["HuggingFaceH4/zephyr-7b-beta", "mistralai/Mistral-7B-v0.1"],
            "Cohere": ["command", "command-light", "command-nightly"],
            "Replicate": ["llama-2-70b", "stable-diffusion", "whisper"],
            "DeepSeek": ["deepseek-chat", "deepseek-coder"]
        }
        return models.get(backend_name, [])
        
    def on_backend_change(self, choice):
        """Çatı değişince modelleri güncelle"""
        models = self.get_models_for_backend(choice)
        self.model_dropdown.configure(values=models)
        if models:
            self.model_var.set(models[0])
            
    def load_model(self):
        """Modeli yükle - ASENKRON"""
        backend = self.backend_var.get()
        model = self.model_var.get()
        self.ai_status_label.configure(text=f"⏳ {model} yükleniyor...", text_color="orange")
        
        # ✅ THREAD'DE ÇALIŞTIR (UI donmasın)
        threading.Thread(target=self._perform_model_load, args=(backend, model), daemon=True).start()

    def _perform_model_load(self, backend, model):
        """Model yükleme işlemini thread'de yap"""
        try:
            from core.ai_integration import AIIntegration
            ai = AIIntegration()
            
            full_model_name = f"{backend} - {model}"
            success = ai.set_model(full_model_name)
            
            # ✅ UI güncellemesi ana thread'de
            self.after(0, lambda: self._update_model_status(model, success))
            
        except Exception as e:
            self.after(0, lambda: self.ai_status_label.configure(
                text=f"❌ Hata: {str(e)}", text_color="red"))

    def _update_model_status(self, model, success):
        """Model durumunu güncelle"""
        if success:
            self.ai_status_label.configure(text=f"✅ {model} yüklendi!", text_color="green")
        else:
            self.ai_status_label.configure(text=f"❌ {model} yüklenemedi!", text_color="red")
            
    def check_connection(self):
        """Bağlantıyı kontrol et - ASENKRON"""
        backend = self.backend_var.get()
        self.ai_status_label.configure(text=f"🔍 {backend} bağlantısı kontrol ediliyor...", text_color="blue")
        
        # ✅ THREAD'DE ÇALIŞTIR (UI donmasın)
        threading.Thread(target=self._perform_connection_check, args=(backend,), daemon=True).start()

    def _perform_connection_check(self, backend):
        """Bağlantı kontrolünü thread'de yap"""
        try:
            from core.ai_integration import AIIntegration
            ai = AIIntegration()
            is_connected = ai.check_backend_connection(backend)
            
            # ✅ UI güncellemesi ana thread'de
            self.after(0, lambda: self._update_connection_status(backend, is_connected))
            
        except Exception as e:
            self.after(0, lambda: self.ai_status_label.configure(
                text=f"❌ Hata: {str(e)}", text_color="red"))

    def _update_connection_status(self, backend, is_connected):
        """Bağlantı durumunu güncelle"""
        if is_connected:
            self.ai_status_label.configure(text=f"✅ {backend} bağlantısı var!", text_color="green")
        else:
            self.ai_status_label.configure(text=f"❌ {backend} bağlantısı yok!", text_color="red")
        
    def create_tabs(self):
        """Sekmeleri oluştur"""
        # Dashboard
        self.dashboard_tab = Dashboard(self.notebook)
        self.notebook.add(self.dashboard_tab, text="🏠 Dashboard")
        
        # System Control
        self.system_tab = SystemTabs(self.notebook)
        self.notebook.add(self.system_tab, text="⚙️ System Control")
        
        # Kernel Yöneticisi
        self.kernel_tab = KernelTab(self.notebook)
        self.notebook.add(self.kernel_tab, text="🐧 Kernel")
        
        # AI Assistant
        self.ai_tab = AIChatInterface(self.notebook)
        self.notebook.add(self.ai_tab, text="🤖 AI Assistant")
        
        # Diğer sekmeler
        self.error_tab = ErrorFixUI(self.notebook)
        self.notebook.add(self.error_tab, text="🔧 Error Fix")
        
        self.plugin_tab = PluginManagerUI(self.notebook)
        self.notebook.add(self.plugin_tab, text="🧩 Plugins")
        
        self.programs_tab = ProgramsTab(self.notebook, self.app.program_launcher)
        self.notebook.add(self.programs_tab, text="🚀 Programs")
        
    def create_status_bar(self):
        """Durum çubuğu oluştur"""
        self.status_frame = ctk.CTkFrame(self.root, height=24)
        self.status_frame.pack(fill="x", side="bottom", pady=(0, 2))
        
        status_content = ctk.CTkFrame(self.status_frame, height=22, fg_color="transparent")
        status_content.pack(fill="x", padx=5, pady=1)
        
        self.status_label = ctk.CTkLabel(status_content, text="System Ready | AI: Disconnected", 
                                       font=ctk.CTkFont(size=11))
        self.status_label.pack(side="left", padx=5)
        
        metrics_frame = ctk.CTkFrame(status_content, fg_color="transparent")
        metrics_frame.pack(side="right", padx=5)
        
        self.cpu_label = ctk.CTkLabel(metrics_frame, text="CPU: 0%", font=ctk.CTkFont(size=11))
        self.cpu_label.pack(side="right", padx=8)
        
        self.mem_label = ctk.CTkLabel(metrics_frame, text="RAM: 0%", font=ctk.CTkFont(size=11))
        self.mem_label.pack(side="right", padx=8)
        
        self.disk_label = ctk.CTkLabel(metrics_frame, text="Disk: 0%", font=ctk.CTkFont(size=11))
        self.disk_label.pack(side="right", padx=8)
        
    def update_status(self, message):
        """Durum çubuğunu güncelle"""
        self.status_label.configure(text=message)
        
    def update_metrics(self, cpu, memory, disk):
        """Sistem metriklerini güncelle"""
        self.cpu_label.configure(text=f"CPU: {cpu}%")
        self.mem_label.configure(text=f"RAM: {memory}%")
        self.disk_label.configure(text=f"Disk: {disk}%")
        
    def add_programs_tab(self, program_launcher):
        """Programs sekmesini ekle"""
        for i in range(self.notebook.index("end")):
            if "🚀 Programs" in self.notebook.tab(i, "text"):
                self.notebook.forget(i)
                break
                
        self.programs_tab = ProgramsTab(self.notebook, program_launcher)
        self.notebook.add(self.programs_tab, text="🚀 Programs")
        
    def run(self):
        """Uygulamayı çalıştır"""
        self.root.mainloop()
        
    def shutdown(self):
        """Uygulamayı kapat"""
        self.root.quit()
        self.root.destroy()
