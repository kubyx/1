"""
Plugin Manager UI - Plugin yönetim arayüzü
"""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

class PluginManagerUI(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Arayüzü kur"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, text="🧩 Plugin Yöneticisi", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        
        ctk.CTkButton(header_frame, text="🔄 Yenile", command=self.refresh_plugins, width=80).pack(side="right", padx=5)
        ctk.CTkButton(header_frame, text="🌐 Market", command=self.open_market, width=80).pack(side="right", padx=5)
        
        # İki sütunlu layout
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # Sol sütun - Plugin listesi
        left_column = ctk.CTkFrame(content_frame)
        left_column.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(left_column, text="Yüklü Plugin'ler", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=5)
        
        # Plugin listesi
        list_frame = ctk.CTkFrame(left_column)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        columns = ("Plugin", "Versiyon", "Durum")
        self.plugin_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.plugin_tree.heading(col, text=col)
            self.plugin_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.plugin_tree.yview)
        self.plugin_tree.configure(yscrollcommand=scrollbar.set)
        
        self.plugin_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Plugin kontrolleri
        control_frame = ctk.CTkFrame(left_column)
        control_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(control_frame, text="Yükle", command=self.load_plugin, width=80).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Kaldır", command=self.unload_plugin, width=80).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Ayarlar", command=self.plugin_settings, width=80).pack(side="left", padx=5)
        
        # Sağ sütun - Plugin detayları
        right_column = ctk.CTkFrame(content_frame)
        right_column.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(right_column, text="Plugin Detayları", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=5)
        
        # Plugin detayları
        details_frame = ctk.CTkFrame(right_column)
        details_frame.pack(fill="both", expand=True, pady=5)
        
        self.details_text = tk.Text(details_frame, wrap=tk.WORD, height=15, font=("Arial", 10))
        details_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.pack(side="left", fill="both", expand=True)
        details_scrollbar.pack(side="right", fill="y")
        self.details_text.config(state="disabled")
        
        # Yeni plugin yükleme
        install_frame = ctk.CTkFrame(right_column)
        install_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(install_frame, text="📦 Yeni Plugin Yükle", 
                     command=self.install_plugin, width=150).pack(pady=5)
        
        # Örnek plugin'leri yükle
        self.load_example_plugins()
        
    def load_example_plugins(self):
        """Örnek plugin'leri yükle"""
        example_plugins = [
            ("System Monitor", "1.2.0", "Aktif"),
            ("Security Scanner", "2.1.0", "Aktif"),
            ("Network Analyzer", "1.0.5", "Pasif"),
            ("Backup Manager", "3.0.1", "Aktif"),
            ("Performance Optimizer", "2.3.0", "Pasif")
        ]
        
        for plugin in example_plugins:
            self.plugin_tree.insert("", "end", values=plugin)
            
        self.details_text.config(state="normal")
        self.details_text.insert("1.0", "Plugin detayları burada gösterilecek...\n\nBir plugin seçiniz.")
        self.details_text.config(state="disabled")
        
    def refresh_plugins(self):
        """Plugin'leri yenile"""
        # Mevcut listeyi temizle
        for item in self.plugin_tree.get_children():
            self.plugin_tree.delete(item)
            
        # Yeniden yükle
        self.load_example_plugins()
        
    def load_plugin(self):
        """Plugin yükle"""
        selection = self.plugin_tree.selection()
        if not selection:
            self.show_message("Lütfen bir plugin seçin")
            return
            
        item = self.plugin_tree.item(selection[0])
        plugin_name = item['values'][0]
        self.show_message(f"'{plugin_name}' plugin'i yükleniyor...")
        
    def unload_plugin(self):
        """Plugin kaldır"""
        selection = self.plugin_tree.selection()
        if not selection:
            self.show_message("Lütfen bir plugin seçin")
            return
            
        item = self.plugin_tree.item(selection[0])
        plugin_name = item['values'][0]
        self.show_message(f"'{plugin_name}' plugin'i kaldırılıyor...")
        
    def plugin_settings(self):
        """Plugin ayarları"""
        selection = self.plugin_tree.selection()
        if not selection:
            self.show_message("Lütfen bir plugin seçin")
            return
            
        item = self.plugin_tree.item(selection[0])
        plugin_name = item['values'][0]
        self.show_message(f"'{plugin_name}' ayarları açılıyor...")
        
    def open_market(self):
        """Plugin marketini aç"""
        self.show_message("🌐 Plugin Marketi açılıyor...\n\nÇevrimiçi plugin deposuna bağlanılıyor.")
        
    def install_plugin(self):
        """Yeni plugin yükle"""
        self.show_message("📦 Yeni Plugin Yükleme\n\nLütfen plugin dosyasını seçin veya marketten indirin.")
        
    def show_message(self, message):
        """Mesaj göster"""
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", message)
        self.details_text.config(state="disabled")
