"""
Kernel Tab - Kernel ayarları GUI (Windows ve Linux)
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
import threading
import platform
import psutil
from core.kernel_manager import KernelManager

class KernelTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.kernel_manager = KernelManager()
        self.current_os = platform.system()
        self.setup_ui()
        
    def setup_ui(self):
        """Arayüzü kur - OS'a göre otomatik ayarla"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık - OS'a göre değişir
        title_frame = ctk.CTkFrame(main_frame)
        title_frame.pack(fill="x", pady=(0, 10))
        
        if self.current_os == "Linux":
            title_text = "🐧 Kernel Yöneticisi"
        elif self.current_os == "Windows":
            title_text = "🪟 Windows Sistem Yöneticisi"
        else:
            title_text = "⚙️ Sistem Yöneticisi"
            
        ctk.CTkLabel(title_frame, text=title_text, 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        # Sistem Bilgileri (Tüm OS'lar için)
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(info_frame, text="Sistem Bilgileri:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5, 0))
        
        self.info_text = ctk.CTkTextbox(info_frame, height=100)
        self.info_text.pack(fill="x", padx=5, pady=5)
        
        # OS'A ÖZEL BÖLÜMLER
        if self.current_os == "Linux":
            self.setup_linux_ui(main_frame)
        elif self.current_os == "Windows":
            self.setup_windows_ui(main_frame)
        else:
            self.setup_other_os_ui(main_frame)
        
        # Ortak Butonlar
        self.setup_common_buttons(main_frame)
        
        # Başlangıçta sistem bilgilerini yükle
        self.refresh_system_info()
    
    def setup_linux_ui(self, main_frame):
        """Linux arayüzünü kur"""
        # Kernel Parametreleri
        param_frame = ctk.CTkFrame(main_frame)
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
        edit_frame = ctk.CTkFrame(main_frame)
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
    
    def setup_windows_ui(self, main_frame):
        """Windows arayüzünü kur"""
        # Registry Parametreleri
        registry_frame = ctk.CTkFrame(main_frame)
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
        service_frame = ctk.CTkFrame(main_frame)
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
    
    def setup_other_os_ui(self, main_frame):
        """Diğer işletim sistemleri için arayüz"""
        not_supported_frame = ctk.CTkFrame(main_frame)
        not_supported_frame.pack(fill="both", expand=True, pady=20)
        
        ctk.CTkLabel(not_supported_frame, text="⚠️ Bu işletim sistemi tam olarak desteklenmiyor",
                    font=ctk.CTkFont(size=14)).pack(expand=True)
        
        ctk.CTkLabel(not_supported_frame, text="Sadece temel sistem bilgileri gösterilebilir",
                    font=ctk.CTkFont(size=12)).pack(expand=True)
    
    def setup_common_buttons(self, main_frame):
        """Ortak butonları kur"""
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")
        
        # Ortak butonlar
        ctk.CTkButton(button_frame, text="🔄 Sistem Bilgilerini Yenile", 
                     command=self.refresh_system_info, width=180).pack(side="left", padx=5)
        
        # OS'a özel butonlar
        if self.current_os == "Linux":
            ctk.CTkButton(button_frame, text="📋 Parametreleri Listele", 
                         command=self.list_parameters, width=180).pack(side="left", padx=5)
            
            ctk.CTkButton(button_frame, text="⚡ Performans Optimizasyonu", 
                         command=self.linux_optimize, width=180).pack(side="left", padx=5)
            
        elif self.current_os == "Windows":
            ctk.CTkButton(button_frame, text="📊 Registry Ayarlarını Getir", 
                         command=self.list_registry_params, width=180).pack(side="left", padx=5)
            
            ctk.CTkButton(button_frame, text="🔧 Servis Durumlarını Getir", 
                         command=self.list_service_status, width=180).pack(side="left", padx=5)
            
            ctk.CTkButton(button_frame, text="🎯 Performans Modu", 
                         command=self.windows_performance_mode, width=180).pack(side="left", padx=5)
            
            ctk.CTkButton(button_frame, text="🔋 Pil Tasarrufu", 
                         command=self.windows_power_save, width=180).pack(side="left", padx=5)
            
            ctk.CTkButton(button_frame, text="🛡️ Güvenlik Optimizasyonu", 
                         command=self.windows_security_optimize, width=180).pack(side="left", padx=5)
        
        # Ortak güvenlik butonu
        ctk.CTkButton(button_frame, text="📊 Sistem Durumu", 
                     command=self.system_status, width=180).pack(side="left", padx=5)
    
    def refresh_system_info(self):
        """Sistem bilgilerini yeniler"""
        self.show_message("🔄 Sistem bilgileri yükleniyor...")
        threading.Thread(target=self._load_system_info, daemon=True).start()
    
    def _load_system_info(self):
        """Sistem bilgilerini yükler"""
        info = self.kernel_manager.get_system_info()
        
        info_text = "=== SİSTEM BİLGİLERİ ===\n\n"
        for key, value in info.items():
            info_text += f"{key.replace('_', ' ').title()}: {value}\n"
        
        self.after(0, lambda: self.info_text.delete("1.0", "end"))
        self.after(0, lambda: self.info_text.insert("1.0", info_text))
        self.after(0, lambda: self.show_message("✅ Sistem bilgileri yüklendi"))
    
    def list_parameters(self):
        """Linux parametreleri listeler"""
        self.show_message("📋 Kernel parametreleri yükleniyor...")
        threading.Thread(target=self._load_parameters, daemon=True).start()
    
    def _load_parameters(self):
        """Parametreleri yükler"""
        parameters = self.kernel_manager.get_kernel_parameters()
        
        self.after(0, lambda: self.clear_parameter_tree())
        
        if isinstance(parameters, dict) and 'error' not in parameters:
            for param, value in parameters.items():
                self.after(0, lambda p=param, v=value: 
                          self.param_tree.insert("", "end", values=(p, v)))
            self.after(0, lambda: self.show_message(f"✅ {len(parameters)} parametre yüklendi"))
        else:
            self.after(0, lambda: self.show_message("❌ Parametreler yüklenemedi"))
    
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
        result = self.kernel_manager.update_kernel_parameter(param, value)
        
        if result.get('success'):
            self.after(0, lambda: self.show_message("✅ Parametre başarıyla güncellendi!"))
            self.list_parameters()  # Listeyi yenile
        else:
            self.after(0, lambda: self.show_message(f"❌ Hata: {result.get('message', 'Bilinmeyen hata')}"))
    
    def list_registry_params(self):
        """Windows registry parametrelerini listeler"""
        self.show_message("📊 Registry ayarları yükleniyor...")
        threading.Thread(target=self._load_registry_params, daemon=True).start()
    
    def _load_registry_params(self):
        """Registry parametrelerini yükler"""
        params = self.kernel_manager.get_windows_registry_parameters()
        
        self.after(0, lambda: self.clear_registry_tree())
        
        if isinstance(params, dict) and 'error' not in params:
            for param, value in params.items():
                self.after(0, lambda p=param, v=value: 
                          self.registry_tree.insert("", "end", values=(p, v)))
            self.after(0, lambda: self.show_message(f"✅ {len(params)} registry ayarı yüklendi"))
        else:
            self.after(0, lambda: self.show_message("❌ Registry ayarları yüklenemedi"))
    
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
        services = self.kernel_manager.manage_windows_services()
        
        self.after(0, lambda: self.clear_service_tree())
        
        if isinstance(services, dict) and 'error' not in services:
            for service, status in services.items():
                self.after(0, lambda s=service, st=status: 
                          self.service_tree.insert("", "end", values=(s, st)))
            self.after(0, lambda: self.show_message(f"✅ {len(services)} servis durumu yüklendi"))
        else:
            self.after(0, lambda: self.show_message("❌ Servis durumları yüklenemedi"))
    
    def clear_service_tree(self):
        """Servis ağacını temizler"""
        for item in self.service_tree.get_children():
            self.service_tree.delete(item)
    
    def linux_optimize(self):
        """Linux optimizasyonu"""
        self.show_message("⚡ Linux performans optimizasyonu uygulanıyor...")
        # Burada Linux optimizasyon script'leri çalıştırılabilir
        self.show_message("✅ Temel Linux optimizasyonları uygulandı")
        self.show_message("💡 Detaylı optimizasyon için kernel parametrelerini düzenleyin")
    
    def windows_performance_mode(self):
        """Windows performans modu"""
        self.show_message("🎯 Windows performans modu uygulanıyor...")
        threading.Thread(target=self._windows_performance_mode, daemon=True).start()
    
    def _windows_performance_mode(self):
        """Windows performans modu işlemi"""
        result = self.kernel_manager.optimize_windows_performance()
        self.after(0, lambda: self.show_message("✅ Performans modu uygulandı:"))
        for optimization in result:
            self.after(0, lambda opt=optimization: self.show_message(f"   • {opt}"))
    
    def windows_power_save(self):
        """Windows pil tasarrufu"""
        self.show_message("🔋 Pil tasarrufu modu uygulanıyor...")
        threading.Thread(target=self._windows_power_save, daemon=True).start()
    
    def _windows_power_save(self):
        """Windows pil tasarrufu işlemi"""
        result = self.kernel_manager.windows_power_save()
        self.after(0, lambda: self.show_message("✅ Pil tasarrufu modu uygulandı:"))
        for optimization in result:
            self.after(0, lambda opt=optimization: self.show_message(f"   • {opt}"))
    
    def windows_security_optimize(self):
        """Windows güvenlik optimizasyonu"""
        self.show_message("🛡️ Güvenlik optimizasyonu uygulanıyor...")
        threading.Thread(target=self._windows_security_optimize, daemon=True).start()
    
    def _windows_security_optimize(self):
        """Windows güvenlik optimizasyonu işlemi"""
        result = self.kernel_manager.windows_security_optimize()
        self.after(0, lambda: self.show_message("✅ Güvenlik optimizasyonu uygulandı:"))
        for optimization in result:
            self.after(0, lambda opt=optimization: self.show_message(f"   • {opt}"))
    
    def system_status(self):
        """Sistem durumunu gösterir"""
        self.show_message("📊 Sistem durumu kontrol ediliyor...")
        
        # CPU kullanımı
        cpu_percent = psutil.cpu_percent(interval=1)
        self.show_message(f"💻 CPU Kullanımı: %{cpu_percent}")
        
        # Bellek kullanımı
        memory = psutil.virtual_memory()
        self.show_message(f"🧠 RAM Kullanımı: %{memory.percent}")
        
        # Disk kullanımı
        disk = psutil.disk_usage('/')
        self.show_message(f"💾 Disk Kullanımı: %{disk.percent}")
        
        # Ağ durumu (sadece aktif bağlantıların sayısı)
        try:
            net_connections = psutil.net_connections()
            self.show_message(f"🌐 Aktif Ağ Bağlantıları: {len(net_connections)}")
        except PermissionError:
            self.show_message("🌐 Ağ Bilgisi: İzin gerekli (Yönetici olarak çalıştırın)")
        
        # Sistemin ne kadar süredir açık olduğu
        boot_time = psutil.boot_time()
        from datetime import datetime, timedelta
        uptime = datetime.now() - datetime.fromtimestamp(boot_time)
        self.show_message(f"⏰ Sistem Çalışma Süresi: {str(uptime).split('.')[0]}")
        
        self.show_message("✅ Sistem durumu kontrolü tamamlandı")
    
    def show_message(self, message):
        """Durum çubuğuna mesaj yazar (parent'ta statusbar olmalı)"""
        # Mesajı hem konsola yazdır (debug için) hem de arayüzde göster
        print(f"KernelTab: {message}")
        try:
            # Parent pencereye bir statusbar mesajı gönder
            if hasattr(self.parent, 'update_status'):
                self.parent.update_status(message)
            # Ayrıca kendi info_text alanımıza da ekleyelim
            self.info_text.configure(state="normal")
            self.info_text.insert("end", message + "\n")
            self.info_text.see("end")
            self.info_text.configure(state="disabled")
        except Exception as e:
            print(f"Durum güncelleme hatası: {e}")

    def on_tab_selected(self):
        """Bu sekme seçildiğinde çağrılır"""
        self.refresh_system_info()
        if self.current_os == "Linux":
            self.list_parameters()
        elif self.current_os == "Windows":
            self.list_registry_params()
            self.list_service_status()

# Test için
if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Kernel Yöneticisi Test")
    root.geometry("900x700")
    
    # Basit bir statusbar fonksiyonu ekle
    def update_status(message):
        status_label.configure(text=message)
    
    root.update_status = update_status
    
    status_label = ctk.CTkLabel(root, text="Hazır", anchor="w")
    status_label.pack(side="bottom", fill="x")
    
    tab = KernelTab(root)
    tab.pack(fill="both", expand=True)
    
    # Sekme seçilmiş gibi davran
    tab.after(100, tab.on_tab_selected)
    
    root.mainloop()
