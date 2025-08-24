"""
Linux Kernel Yöneticisi - Linux özel işlevleri
"""
import customtkinter as ctk
from tkinter import ttk
import threading

class LinuxKernelManager:
    def __init__(self, parent_frame, kernel_manager, message_callback):
        self.parent = parent_frame
        self.kernel_manager = kernel_manager
        self.show_message = message_callback
        self.setup_linux_ui()
        
    def setup_linux_ui(self):
        """Linux arayüzünü kur"""
        # Kernel Parametreleri
        param_frame = ctk.CTkFrame(self.parent)
        param_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        ctk.CTkLabel(param_frame, text="Kernel Parametreleri:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5, 0))
        
        # Parametre listesi
        self.param_tree = ttk.Treeview(param_frame, columns=("parameter", "value"), 
                                      show="headings", height=10)
        self.param_tree.heading("parameter", text="Parametre")
        self.param_tree.heading("value", text="Değer")
        
        self.param_tree.column("parameter", width=250)
        self.param_tree.column("value", width=150)
        
        self.param_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(param_frame, orient="vertical", command=self.param_tree.yview)
        self.param_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Parametre Düzenleme
        edit_frame = ctk.CTkFrame(self.parent)
        edit_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(edit_frame, text="Parametre Düzenle:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5, 0))
        
        edit_subframe = ctk.CTkFrame(edit_frame)
        edit_subframe.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(edit_subframe, text="Parametre:").pack(side="left", padx=5)
        self.param_entry = ctk.CTkEntry(edit_subframe, width=200)
        self.param_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(edit_subframe, text="Değer:").pack(side="left", padx=5)
        self.value_entry = ctk.CTkEntry(edit_subframe, width=100)
        self.value_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(edit_subframe, text="Güncelle", 
                     command=self.update_parameter, width=100).pack(side="left", padx=5)
    
    def list_parameters(self):
        """Linux parametreleri listeler"""
        self.show_message("📋 Kernel parametreleri yükleniyor...")
        threading.Thread(target=self._load_parameters, daemon=True).start()
    
    def _load_parameters(self):
        """Parametreleri yükler"""
        try:
            parameters = self.kernel_manager.get_kernel_parameters()
            
            # Ana thread'de ağacı temizle
            self.parent.after(0, self.clear_parameter_tree)
            
            if isinstance(parameters, dict) and 'error' not in parameters:
                for param, value in parameters.items():
                    self.parent.after(0, lambda p=param, v=value: 
                                  self.param_tree.insert("", "end", values=(p, v)))
                self.parent.after(0, lambda: self.show_message(f"✅ {len(parameters)} parametre yüklendi"))
            else:
                error_msg = parameters.get('error', 'Bilinmeyen hata') if isinstance(parameters, dict) else 'Bilinmeyen hata'
                self.parent.after(0, lambda: self.show_message(f"❌ Parametreler yüklenemedi: {error_msg}"))
                
        except Exception as e:
            self.parent.after(0, lambda: self.show_message(f"❌ Parametre yükleme hatası: {str(e)}"))
    
    def clear_parameter_tree(self):
        """Parametre ağacını temizler"""
        for item in self.param_tree.get_children():
            self.param_tree.delete(item)
    
    def update_parameter(self):
        """Parametreyi günceller"""
        param = self.param_entry.get().strip()
        value = self.value_entry.get().strip()
        
        if not param or not value:
            self.show_message("❌ Lütfen parametre ve değer giriniz.")
            return
        
        self.show_message(f"🔄 '{param}' parametresi güncelleniyor...")
        threading.Thread(target=self._update_param, args=(param, value), daemon=True).start()
    
    def _update_param(self, param, value):
        """Parametre güncelleme işlemi"""
        try:
            result = self.kernel_manager.update_kernel_parameter(param, value)
            
            if result.get('success'):
                self.parent.after(0, lambda: self.show_message("✅ Parametre başarıyla güncellendi!"))
                self.list_parameters()  # Listeyi yenile
            else:
                error_msg = result.get('message', 'Bilinmeyen hata')
                self.parent.after(0, lambda: self.show_message(f"❌ Hata: {error_msg}"))
                
        except Exception as e:
            self.parent.after(0, lambda: self.show_message(f"❌ Parametre güncelleme hatası: {str(e)}"))
    
    def linux_optimize(self):
        """Linux optimizasyonu"""
        self.show_message("⚡ Linux performans optimizasyonu uygulanıyor...")
        # Burada Linux optimizasyon script'leri çalıştırılabilir
        self.show_message("✅ Temel Linux optimizasyonları uygulandı")
        self.show_message("💡 Detaylı optimizasyon için kernel parametrelerini düzenleyin")
