"""
Ana Pencere - Temel GUI yapısı
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from .dashboard import Dashboard
from .system_tabs import SystemTabs
from .ai_chat_interface import AIChatInterface
from .plugin_manager_ui import PluginManagerUI
from .error_fix_ui import ErrorFixUI
from .resource_monitor import ResourceMonitor
from .programs_tab import ProgramsTab
from .kernel_tab import KernelTab  # YENİ EKLENDİ

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
        self.root.minsize(1000, 600)  # Minimum yüksekliği azalt
        self.root.maxsize(screen_width, screen_height)
        self.root.resizable(True, True)
        
        # Pencereyi ekran ortasına al
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
        # Ana çerçeve - daha iyi boyutlandırma için
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Sekme kontrolü - daha kompakt
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Sekmeleri oluştur
        self.create_tabs()
        
        # Durum çubuğu - daha kompakt
        self.create_status_bar()
        
    def create_tabs(self):
        """Sekmeleri oluştur"""
        # Dashboard
        self.dashboard_tab = Dashboard(self.notebook)
        self.notebook.add(self.dashboard_tab, text="🏠 Dashboard")
        
        # System Control
        self.system_tab = SystemTabs(self.notebook)
        self.notebook.add(self.system_tab, text="⚙️ System Control")
        
        # Kernel Yöneticisi - YENİ EKLENDİ
        self.kernel_tab = KernelTab(self.notebook)
        self.notebook.add(self.kernel_tab, text="🐧 Kernel")
        
        # AI Assistant
        self.ai_tab = AIChatInterface(self.notebook)
        self.notebook.add(self.ai_tab, text="🤖 AI Assistant")
        
        # Error Fix
        self.error_tab = ErrorFixUI(self.notebook)
        self.notebook.add(self.error_tab, text="🔧 Error Fix")
        
        # Plugin Manager
        self.plugin_tab = PluginManagerUI(self.notebook)
        self.notebook.add(self.plugin_tab, text="🧩 Plugins")
        
        # Programs sekmesi
        self.programs_tab = ProgramsTab(self.notebook, self.app.program_launcher)
        self.notebook.add(self.programs_tab, text="🚀 Programs")
        
    def create_status_bar(self):
        """Durum çubuğu oluştur - daha kompakt"""
        self.status_frame = ctk.CTkFrame(self.root, height=24)  # Daha kısa çerçeve
        self.status_frame.pack(fill="x", side="bottom", pady=(0, 2))  # Alt boşluk ekle
        
        # Durum çubuğu içeriği
        status_content = ctk.CTkFrame(self.status_frame, height=22, fg_color="transparent")
        status_content.pack(fill="x", padx=5, pady=1)
        
        self.status_label = ctk.CTkLabel(status_content, text="System Ready | AI: Disconnected", 
                                       font=ctk.CTkFont(size=11))  # Daha küçük font
        self.status_label.pack(side="left", padx=5)
        
        # Sistem metrikleri - daha kompakt
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
        """Programs sekmesini ekle (yeniden)"""
        # Önce mevcut sekme varsa kaldır
        for i in range(self.notebook.index("end")):
            if "🚀 Programs" in self.notebook.tab(i, "text"):
                self.notebook.forget(i)
                break
                
        # Yeni sekme ekle
        self.programs_tab = ProgramsTab(self.notebook, program_launcher)
        self.notebook.add(self.programs_tab, text="🚀 Programs")
        
    def run(self):
        """Uygulamayı çalıştır"""
        self.root.mainloop()
        
    def shutdown(self):
        """Uygulamayı kapat"""
        self.root.quit()
        self.root.destroy()
