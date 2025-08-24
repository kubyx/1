"""
Windows Kernel Yöneticisi - Windows özel işlevleri
"""
import customtkinter as ctk
from tkinter import ttk
import threading

class WindowsKernelManager:
    def __init__(self, parent_frame, kernel_manager, message_callback):
        self.parent = parent_frame
        self.kernel_manager = kernel_manager
        self.show_message = message_callback
        self.setup_windows_ui()
        
    def setup_windows_ui(self):
        """Windows arayüzünü kur"""
        # Registry Parametreleri
        registry_frame = ctk.CTkFrame(self.parent)
        registry_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        ctk.CTkLabel(registry_frame, text="Windows Kayıt Defteri Ayarları:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5, 0))
        
        # Registry listesi
        self.registry_tree = ttk.Treeview(registry_frame, columns=("setting", "value"), 
                                         show="headings", height=8)
        self.registry_tree.heading("setting", text="Ayar")
        self.registry_tree.heading("value", text="Değer")
        
        self.registry_tree.column("setting", width=400)
        self.registry_tree.column("value", width=200)
        
        self.registry_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(registry_frame, orient="vertical", command=self.registry_tree.yview)
        self.registry_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Servis Durumları
        service_frame = ctk.CTkFrame(self.parent)
        service_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        ctk.CTkLabel(service_frame, text="Windows Servis Durumları:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5, 0))
        
        self.service_tree = ttk.Treeview(service_frame, columns=("service", "status"), 
                                        show="headings", height=6)
        self.service_tree.heading("service", text="Servis")
        self.service_tree.heading("status", text="Durum")
        
        self.service_tree.column("service", width=250)
        self.service_tree.column("status", width=150)
        
        self.service_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Servis Scrollbar
        service_scrollbar = ttk.Scrollbar(service_frame, orient="vertical", command=self.service_tree.yview)
        self.service_tree.configure(yscrollcommand=service_scrollbar.set)
        service_scrollbar.pack(side="right", fill="y")
    
    def list_registry_params(self):
        """Windows registry parametrelerini listeler"""
        self.show_message("📊 Registry ayarları yükleniyor...")
        threading.Thread(target=self._load_registry_params, daemon=True).start()
    
    def _load_registry_params(self):
        """Registry parametrelerini yükler"""
        try:
            params = self.kernel_manager.get_windows_registry_parameters()
            
            # Ana thread'de ağacı temizle
            self.parent.after(0, self.clear_registry_tree)
            
            if isinstance(params, dict) and 'error' not in params:
                for param, value in params.items():
                    self.parent.after(0, lambda p=param, v=value: 
                                  self.registry_tree.insert("", "end", values=(p, v)))
                self.parent.after(0, lambda: self.show_message(f"✅ {len(params)} registry ayarı yüklendi"))
            else:
                error_msg = params.get('error', 'Bilinmeyen hata') if isinstance(params, dict) else 'Bilinmeyen hata'
                self.parent.after(0, lambda: self.show_message(f"❌ Registry ayarları yüklenemedi: {error_msg}"))
                
        except Exception as e:
            self.parent.after(0, lambda: self.show_message(f"❌ Registry yükleme hatası: {str(e)}"))
    
    def clear_registry_tree(self):
        """Registry ağacını temizler"""
        for item in self.registry_tree.get_children():
            self.registry_tree.delete(item)
    
    def list_service_status(self):
        """Windows servis durumlarını listeler"""
        self.show_message("🔧 Servis durumları yükleniyor...")
        threading.Thread(target=self._load_service_status, daemon=True).start()
    
    def _load_service_status(self):
        """Servis durumlarını yükler"""
        try:
            services = self.kernel_manager.manage_windows_services()
            
            # Ana thread'de ağacı temizle
            self.parent.after(0, self.clear_service_tree)
            
            if isinstance(services, dict) and 'error' not in services:
                for service, info in services.items():
                    status = info.get('status', 'Bilinmiyor')
                    self.parent.after(0, lambda s=service, st=status: 
                                  self.service_tree.insert("", "end", values=(s, st)))
                self.parent.after(0, lambda: self.show_message(f"✅ {len(services)} servis durumu yüklendi"))
            else:
                error_msg = services.get('error', 'Bilinmeyen hata') if isinstance(services, dict) else 'Bilinmeyen hata'
                self.parent.after(0, lambda: self.show_message(f"❌ Servis durumları yüklenemedi: {error_msg}"))
                
        except Exception as e:
            self.parent.after(0, lambda: self.show_message(f"❌ Servis durumu yükleme hatası: {str(e)}"))
    
    def clear_service_tree(self):
        """Servis ağacını temizler"""
        for item in self.service_tree.get_children():
            self.service_tree.delete(item)
    
    def windows_performance_mode(self):
        """Windows performans modu"""
        self.show_message("🎯 Windows performans modu uygulanıyor...")
        threading.Thread(target=self._windows_performance_mode, daemon=True).start()
    
    def _windows_performance_mode(self):
        """Windows performans modu işlemi"""
        try:
            result = self.kernel_manager.optimize_windows_performance()
            self.parent.after(0, lambda: self.show_message("✅ Performans modu uygulandı:"))
            for optimization in result:
                self.parent.after(0, lambda opt=optimization: self.show_message(f"   • {opt}"))
        except Exception as e:
            self.parent.after(0, lambda: self.show_message(f"❌ Performans modu hatası: {str(e)}"))
    
    def windows_power_save(self):
        """Windows pil tasarrufu"""
        self.show_message("🔋 Pil tasarruf modu uygulanıyor...")
        threading.Thread(target=self._windows_power_save, daemon=True).start()
    
    def _windows_power_save(self):
        """Windows pil tasarrufu işlemi"""
        try:
            result = self.kernel_manager.optimize_windows_power_saving()
            self.parent.after(0, lambda: self.show_message("✅ Pil tasarruf modu uygulandı:"))
            for optimization in result:
                self.parent.after(0, lambda opt=optimization: self.show_message(f"   • {opt}"))
        except Exception as e:
            self.parent.after(0, lambda: self.show_message(f"❌ Pil tasarruf modu hatası: {str(e)}"))
    
    def windows_security_optimize(self):
        """Windows güvenlik optimizasyonu"""
        self.show_message("🛡️ Windows güvenlik optimizasyonu uygulanıyor...")
        threading.Thread(target=self._windows_security_optimize, daemon=True).start()
    
    def _windows_security_optimize(self):
        """Windows güvenlik optimizasyonu işlemi"""
        try:
            result = self.kernel_manager.optimize_windows_security()
            self.parent.after(0, lambda: self.show_message("✅ Güvenlik optimizasyonları uygulandı:"))
            for optimization in result:
                self.parent.after(0, lambda opt=optimization: self.show_message(f"   • {opt}"))
        except Exception as e:
            self.parent.after(0, lambda: self.show_message(f"❌ Güvenlik optimizasyonu hatası: {str(e)}"))
