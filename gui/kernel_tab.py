"""
Kernel Tab - Ana pencere (Windows ve Linux)
"""
import customtkinter as ctk
import threading
import platform
import psutil
from datetime import datetime
from core.kernel_manager import KernelManager

class SystemInfoComponent:
    def __init__(self, parent_frame, kernel_manager, message_callback):
        self.parent = parent_frame
        self.kernel_manager = kernel_manager
        self.show_message = message_callback
        self.setup_ui()
        
    def setup_ui(self):
        """Sistem bilgisi arayüzünü kur"""
        info_frame = ctk.CTkFrame(self.parent)
        info_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(info_frame, text="Sistem Bilgileri:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5, 0))
        
        self.info_text = ctk.CTkTextbox(info_frame, height=120)
        self.info_text.pack(fill="x", padx=5, pady=5)
        self.info_text.insert("1.0", "Sistem bilgileri hazırlanıyor...")
        self.info_text.configure(state="disabled")
    
    def refresh_system_info(self):
        """Sistem bilgilerini yeniler"""
        self.show_message("🔄 Sistem bilgileri yükleniyor...")
        
        try:
            info = self.kernel_manager.get_system_info()
            
            info_text = "=== SİSTEM BİLGİLERİ ===\n\n"
            for key, value in info.items():
                info_text += f"{key.replace('_', ' ').title()}: {value}\n"
            
            self.info_text.configure(state="normal")
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", info_text)
            self.info_text.configure(state="disabled")
            self.show_message("✅ Sistem bilgileri yüklendi")
            
        except Exception as e:
            self.show_message(f"❌ Hata: {str(e)}")

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
        self.system_info = SystemInfoComponent(main_frame, self.kernel_manager, self.show_message)
        
        # OS'A ÖZEL BÖLÜMLER
        if self.current_os == "Linux":
            from gui.kernel_linux import LinuxKernelManager
            self.os_manager = LinuxKernelManager(main_frame, self.kernel_manager, self.show_message)
        elif self.current_os == "Windows":
            from gui.kernel_windows import WindowsKernelManager
            self.os_manager = WindowsKernelManager(main_frame, self.kernel_manager, self.show_message)
        else:
            self.setup_other_os_ui(main_frame)
        
        # Ortak Butonlar
        self.setup_common_buttons(main_frame)
        
        # Başlangıçta sistem bilgilerini yükle
        self.after(100, self.system_info.refresh_system_info)
    
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
                     command=self.system_info.refresh_system_info, width=180).pack(side="left", padx=5)
        
        # OS'a özel butonlar
        if self.current_os == "Linux":
            ctk.CTkButton(button_frame, text="📋 Parametreleri Listele", 
                         command=self.os_manager.list_parameters, width=180).pack(side="left", padx=5)
            
            ctk.CTkButton(button_frame, text="⚡ Performans Optimizasyonu", 
                         command=self.os_manager.linux_optimize, width=180).pack(side="left", padx=5)
            
        elif self.current_os == "Windows":
            ctk.CTkButton(button_frame, text="📊 Registry Ayarlarını Getir", 
                         command=self.os_manager.list_registry_params, width=180).pack(side="left", padx=5)
            
            ctk.CTkButton(button_frame, text="🔧 Servis Durumlarını Getir", 
                         command=self.os_manager.list_service_status, width=180).pack(side="left", padx=5)
            
            ctk.CTkButton(button_frame, text="🎯 Performans Modu", 
                         command=self.os_manager.windows_performance_mode, width=180).pack(side="left", padx=5)
            
            ctk.CTkButton(button_frame, text="🔋 Pil Tasarrufu", 
                         command=self.os_manager.windows_power_save, width=180).pack(side="left", padx=5)
            
            ctk.CTkButton(button_frame, text="🛡️ Güvenlik Optimizasyonu", 
                         command=self.os_manager.windows_security_optimize, width=180).pack(side="left", padx=5)
        
        # Sistem durumu butonu
        ctk.CTkButton(button_frame, text="📊 Detaylı Sistem Durumu", 
                     command=self.detailed_system_status, width=180).pack(side="left", padx=5)
    
    def detailed_system_status(self):
        """Detaylı sistem durumunu göster"""
        self.show_message("📊 Detaylı sistem durumu analiz ediliyor...")
        threading.Thread(target=self._check_detailed_system_status, daemon=True).start()
    
    def _check_detailed_system_status(self):
        """Detaylı sistem durumunu kontrol eder"""
        try:
            status = self._get_comprehensive_system_status()
            
            message = "✅ DETAYLI SİSTEM DURUMU\n\n"
            message += "=== PERFORMANS ===\n"
            message += f"• CPU Kullanımı: {status['performance']['cpu_usage']}%\n"
            message += f"• Bellek Kullanımı: {status['performance']['memory_usage']}%\n"
            message += f"• Disk Kullanımı: {status['performance']['disk_usage']}%\n"
            message += f"• Ağ Gönderim: {status['performance']['network_sent_mb']} MB\n"
            message += f"• Ağ Alım: {status['performance']['network_recv_mb']} MB\n\n"
            
            message += "=== SİSTEM SAĞLIĞI ===\n"
            message += f"• Çalışma Süresi: {status['health']['uptime']}\n"
            message += f"• Disk Boş Alan: {status['health']['disk_free_gb']} GB\n"
            message += f"• Kullanılabilir Bellek: {status['health']['memory_available_gb']} GB\n"
            message += f"• Sistem Sıcaklığı: {status['health']['temperature']}\n\n"
            
            message += "=== KRİTİK SERVİSLER ===\n"
            for service, info in status['critical_services'].items():
                message += f"• {service}: {info['status']} ({info['start_mode']})\n"
            
            self.after(0, lambda: self.show_message(message))
            
        except Exception as e:
            self.after(0, lambda: self.show_message(f"❌ Sistem durumu analiz edilemedi: {str(e)}"))
    
    def _get_comprehensive_system_status(self):
        """Kapsamlı sistem durumu bilgilerini toplar"""
        # Performans verileri
        perf_data = self.kernel_manager.get_windows_performance_data() if hasattr(self.kernel_manager, 'get_windows_performance_data') else {}
        
        # Sistem sağlığı
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = f"{uptime.days}g {uptime.seconds//3600}sa {(uptime.seconds%3600)//60}dak"
        
        # Disk bilgileri
        try:
            disk = psutil.disk_usage('/')
            disk_free_gb = round(disk.free / (1024**3), 2)
        except:
            disk_free_gb = "N/A"
        
        # Bellek bilgileri
        memory = psutil.virtual_memory()
        memory_available_gb = round(memory.available / (1024**3), 2)
        
        # Sıcaklık bilgisi (Linux için)
        temperature = self._get_system_temperature()
        
        # Kritik servisler
        critical_services = self._get_critical_services_status()
        
        return {
            'performance': {
                'cpu_usage': perf_data.get('cpu_usage', psutil.cpu_percent(interval=1)),
                'memory_usage': perf_data.get('memory_usage', memory.percent),
                'disk_usage': perf_data.get('disk_usage', "N/A"),
                'network_sent_mb': perf_data.get('network_sent_mb', "N/A"),
                'network_recv_mb': perf_data.get('network_recv_mb', "N/A")
            },
            'health': {
                'uptime': uptime_str,
                'disk_free_gb': disk_free_gb,
                'memory_available_gb': memory_available_gb,
                'temperature': temperature
            },
            'critical_services': critical_services
        }
    
    def _get_system_temperature(self):
        """Sistem sıcaklığını al"""
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current:
                                return f"{entry.current}°C"
            return "N/A"
        except:
            return "N/A"
    
    def _get_critical_services_status(self):
        """Kritik servislerin durumunu al"""
        try:
            if self.current_os == "Windows" and hasattr(self.kernel_manager, 'manage_windows_services'):
                services = self.kernel_manager.manage_windows_services()
                return {k: {'status': v.get('status', 'Bilinmiyor'), 
                           'start_mode': v.get('start_mode', 'Bilinmiyor')} 
                       for k, v in services.items()}
            else:
                return {"Servis Bilgisi": {"status": "Sadece Windows", "start_mode": "N/A"}}
        except:
            return {"Servis Bilgisi": {"status": "Alınamadı", "start_mode": "N/A"}}
    
    def show_message(self, message):
        """Durum mesajını göster"""
        if hasattr(self.parent, 'status_bar'):
            self.parent.status_bar.set_status(message)
        else:
            print(f"Status: {message}")

# Test için
if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Kernel Tab Test")
    root.geometry("900x700")
    
    tab = KernelTab(root)
    tab.pack(fill="both", expand=True)
    
    root.mainloop()
