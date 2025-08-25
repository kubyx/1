"""
Kernel Tab - Ana pencere (Windows ve Linux)
Güncellendi: KernelInterface ile entegre, tam işlevsel
"""
import customtkinter as ctk
import threading
import platform
import psutil
from datetime import datetime
from .kernel_interface import KernelInterface  # Güncellendi: Core'dan gui'ye taşındı

class SystemInfoComponent:
    def __init__(self, parent_frame, kernel_interface, message_callback):  # kernel_manager -> kernel_interface
        self.parent = parent_frame
        self.kernel_interface = kernel_interface  # Güncellendi
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
            # KernelInterface kullanarak sistem bilgilerini al
            success, stdout, stderr = self.kernel_interface.execute_command("systeminfo" if platform.system() == "Windows" else "uname -a")
            
            if success:
                info_text = "=== SİSTEM BİLGİLERİ ===\n\n"
                info_text += f"İşletim Sistemi: {platform.system()} {platform.release()}\n"
                info_text += f"Platform: {platform.platform()}\n"
                info_text += f"İşlemci: {platform.processor()}\n"
                
                # Bellek bilgisi
                mem = psutil.virtual_memory()
                info_text += f"Toplam RAM: {round(mem.total / (1024**3), 2)} GB\n"
                info_text += f"Kullanılabilir RAM: {round(mem.available / (1024**3), 2)} GB\n"
                
                # Disk bilgisi
                try:
                    disk = psutil.disk_usage('/')
                    info_text += f"Disk Kullanımı: {disk.percent}%\n"
                except:
                    info_text += "Disk Bilgisi: Alınamadı\n"
                
                info_text += f"\nSysteminfo Çıktısı:\n{stdout}\n"
                
                self.info_text.configure(state="normal")
                self.info_text.delete("1.0", "end")
                self.info_text.insert("1.0", info_text)
                self.info_text.configure(state="disabled")
                self.show_message("✅ Sistem bilgileri yüklendi")
            else:
                self.show_message(f"❌ Sistem bilgileri alınamadı: {stderr}")
            
        except Exception as e:
            self.show_message(f"❌ Hata: {str(e)}")

class KernelTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.kernel_interface = KernelInterface()  # Güncellendi: KernelManager yerine
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
        self.system_info = SystemInfoComponent(main_frame, self.kernel_interface, self.show_message)
        
        # Komut Çalıştırma Bölümü - Tüm OS'lar için ORTAK
        self.setup_command_section(main_frame)
        
        # OS'A ÖZEL BÖLÜMLER
        if self.current_os == "Linux":
            self.setup_linux_specific_ui(main_frame)
        elif self.current_os == "Windows":
            self.setup_windows_specific_ui(main_frame)
        else:
            self.setup_other_os_ui(main_frame)
        
        # Ortak Butonlar
        self.setup_common_buttons(main_frame)
        
        # Başlangıçta sistem bilgilerini yükle
        self.after(100, self.system_info.refresh_system_info)
    
    def setup_command_section(self, main_frame):
        """Komut çalıştırma bölümünü kur (Tüm OS'lar için)"""
        command_frame = ctk.CTkFrame(main_frame)
        command_frame.pack(fill="x", pady=(10, 5))
        
        ctk.CTkLabel(command_frame, text="Komut Çalıştır:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5)
        
        # Komut girişi ve çalıştırma butonu
        input_frame = ctk.CTkFrame(command_frame)
        input_frame.pack(fill="x", padx=5, pady=5)
        
        self.command_entry = ctk.CTkEntry(input_frame, placeholder_text="Komutu girin...")
        self.command_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.command_entry.bind("<Return>", lambda e: self.execute_single_command())
        
        ctk.CTkButton(input_frame, text="Çalıştır", 
                     command=self.execute_single_command, width=80).pack(side="right")
        
        # Komut çıktısı
        output_frame = ctk.CTkFrame(command_frame)
        output_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        ctk.CTkLabel(output_frame, text="Çıktı:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.output_text = ctk.CTkTextbox(output_frame, height=100)
        self.output_text.pack(fill="x", pady=5)
        self.output_text.configure(state="disabled")
    
    def setup_linux_specific_ui(self, main_frame):
        """Linux'a özel arayüz bileşenleri"""
        linux_frame = ctk.CTkFrame(main_frame)
        linux_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(linux_frame, text="Linux Özellikleri:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5)
        
        button_frame = ctk.CTkFrame(linux_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(button_frame, text="📋 Çekirdek Parametreleri", 
                     command=self.list_kernel_parameters, width=180).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="📊 Sistem Yükü", 
                     command=self.check_system_load, width=180).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="⚡ Performans Optimizasyonu", 
                     command=self.linux_optimize, width=180).pack(side="left", padx=5)
    
    def setup_windows_specific_ui(self, main_frame):
        """Windows'a özel arayüz bileşenleri"""
        windows_frame = ctk.CTkFrame(main_frame)
        windows_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(windows_frame, text="Windows Özellikleri:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5)
        
        button_frame = ctk.CTkFrame(windows_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(button_frame, text="📊 Servis Durumları", 
                     command=self.list_service_status, width=180).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="🎯 Performans Modu", 
                     command=self.windows_performance_mode, width=180).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="🛡️ Güvenlik Optimizasyonu", 
                     command=self.windows_security_optimize, width=180).pack(side="left", padx=5)
    
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
        button_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(button_frame, text="🔄 Sistem Bilgilerini Yenile", 
                     command=self.system_info.refresh_system_info, width=180).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="📊 Detaylı Sistem Durumu", 
                     command=self.detailed_system_status, width=180).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="🧹 Bellek Temizleme", 
                     command=self.clean_memory, width=180).pack(side="left", padx=5)
    
    def execute_single_command(self):
        """Tek komut çalıştır"""
        command = self.command_entry.get().strip()
        if not command:
            self.show_message("❌ Lütfen bir komut girin")
            return
            
        self.show_message(f"🔄 Komut çalıştırılıyor: {command}")
        threading.Thread(target=self._execute_command_thread, args=(command,), daemon=True).start()
    
    def _execute_command_thread(self, command):
        """Komut çalıştırma thread'i"""
        try:
            success, stdout, stderr = self.kernel_interface.execute_command(command, timeout=30)
            
            if success:
                result = f"✅ KOMUT BAŞARILI:\n{stdout}"
                if stderr:
                    result += f"\n⚠️ Uyarılar:\n{stderr}"
            else:
                result = f"❌ KOMUT HATASI:\n{stderr}"
                if stdout:
                    result += f"\nÇıktı:\n{stdout}"
            
            self.after(0, lambda: self._show_command_result(result))
            self.after(0, lambda: self.show_message(f"✅ Komut tamamlandı: {command}"))
            
        except Exception as e:
            error_msg = f"❌ Komut çalıştırma hatası: {str(e)}"
            self.after(0, lambda: self._show_command_result(error_msg))
            self.after(0, lambda: self.show_message(error_msg))
    
    def _show_command_result(self, result):
        """Komut sonucunu göster"""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", result)
        self.output_text.configure(state="disabled")
    
    # Linux metodları
    def list_kernel_parameters(self):
        """Linux kernel parametrelerini listeler"""
        self.show_message("🔄 Kernel parametreleri listeleniyor...")
        threading.Thread(target=self._list_kernel_params_thread, daemon=True).start()
    
    def _list_kernel_params_thread(self):
        """Kernel parametrelerini listeleyen thread"""
        try:
            success, stdout, stderr = self.kernel_interface.execute_command("sysctl -a | head -50", timeout=20)
            
            if success:
                result = f"🐧 İLK 50 KERNEL PARAMETRESİ:\n{stdout}"
                if stderr:
                    result += f"\n⚠️ Uyarılar:\n{stderr}"
            else:
                result = f"❌ Hata: {stderr}"
            
            self.after(0, lambda: self._show_command_result(result))
            self.after(0, lambda: self.show_message("✅ Kernel parametreleri listelendi"))
            
        except Exception as e:
            error_msg = f"❌ Kernel parametreleri alınamadı: {str(e)}"
            self.after(0, lambda: self._show_command_result(error_msg))
            self.after(0, lambda: self.show_message(error_msg))
    
    def check_system_load(self):
        """Sistem yükünü kontrol eder"""
        self.show_message("🔄 Sistem yükü kontrol ediliyor...")
        threading.Thread(target=self._check_system_load_thread, daemon=True).start()
    
    def _check_system_load_thread(self):
        """Sistem yükünü kontrol eden thread"""
        try:
            success, stdout, stderr = self.kernel_interface.execute_command("uptime && free -h", timeout=10)
            
            if success:
                result = f"📊 SİSTEM YÜKÜ ve BELLEK:\n{stdout}"
            else:
                result = f"❌ Hata: {stderr}"
            
            self.after(0, lambda: self._show_command_result(result))
            self.after(0, lambda: self.show_message("✅ Sistem yükü bilgileri alındı"))
            
        except Exception as e:
            error_msg = f"❌ Sistem yükü alınamadı: {str(e)}"
            self.after(0, lambda: self._show_command_result(error_msg))
            self.after(0, lambda: self.show_message(error_msg))
    
    def linux_optimize(self):
        """Linux performans optimizasyonu"""
        self.show_message("⚡ Linux optimizasyonu yapılıyor...")
        threading.Thread(target=self._linux_optimize_thread, daemon=True).start()
    
    def _linux_optimize_thread(self):
        """Linux optimizasyon thread'i"""
        try:
            commands = [
                "echo 3 | sudo tee /proc/sys/vm/drop_caches",
                "sudo sync",
                "sudo sysctl -w vm.swappiness=10"
            ]
            
            results = []
            for cmd in commands:
                success, stdout, stderr = self.kernel_interface.execute_command(cmd, timeout=15)
                results.append(f"Komut: {cmd}\nSonuç: {'Başarılı' if success else 'Hatalı'}\nÇıktı: {stdout}\nHata: {stderr}\n")
            
            result = "⚡ LİNUX OPTİMİZASYON SONUÇLARI:\n" + "\n".join(results)
            self.after(0, lambda: self._show_command_result(result))
            self.after(0, lambda: self.show_message("✅ Linux optimizasyonu tamamlandı"))
            
        except Exception as e:
            error_msg = f"❌ Optimizasyon hatası: {str(e)}"
            self.after(0, lambda: self._show_command_result(error_msg))
            self.after(0, lambda: self.show_message(error_msg))
    
    # Windows metodları
    def list_service_status(self):
        """Windows servis durumlarını listeler"""
        self.show_message("🔄 Windows servis durumları listeleniyor...")
        threading.Thread(target=self._list_service_status_thread, daemon=True).start()
    
    def _list_service_status_thread(self):
        """Servis durumlarını listeleyen thread"""
        try:
            success, stdout, stderr = self.kernel_interface.execute_command("sc query state= all | find \"SERVICE_NAME:\" | head -20", timeout=20)
            
            if success:
                result = f"🪟 İLK 20 WINDOWS SERVİSİ:\n{stdout}"
                if stderr:
                    result += f"\n⚠️ Uyarılar:\n{stderr}"
            else:
                result = f"❌ Hata: {stderr}"
            
            self.after(0, lambda: self._show_command_result(result))
            self.after(0, lambda: self.show_message("✅ Servis durumları listelendi"))
            
        except Exception as e:
            error_msg = f"❌ Servis durumları alınamadı: {str(e)}"
            self.after(0, lambda: self._show_command_result(error_msg))
            self.after(0, lambda: self.show_message(error_msg))
    
    def windows_performance_mode(self):
        """Windows performans modu"""
        self.show_message("🎯 Windows performans modu ayarlanıyor...")
        threading.Thread(target=self._windows_performance_thread, daemon=True).start()
    
    def _windows_performance_thread(self):
        """Windows performans thread'i"""
        try:
            commands = [
                "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",  # High performance
                "powercfg /h off"  # Hibernation off
            ]
            
            results = []
            for cmd in commands:
                success, stdout, stderr = self.kernel_interface.execute_command(cmd, timeout=15)
                results.append(f"Komut: {cmd}\nSonuç: {'Başarılı' if success else 'Hatalı'}\nÇıktı: {stdout}\nHata: {stderr}\n")
            
            result = "🎯 WINDOWS PERFORMANS AYARLARI:\n" + "\n".join(results)
            self.after(0, lambda: self._show_command_result(result))
            self.after(0, lambda: self.show_message("✅ Windows performans modu ayarlandı"))
            
        except Exception as e:
            error_msg = f"❌ Performans ayarı hatası: {str(e)}"
            self.after(0, lambda: self._show_command_result(error_msg))
            self.after(0, lambda: self.show_message(error_msg))
    
    def windows_security_optimize(self):
        """Windows güvenlik optimizasyonu"""
        self.show_message("🛡️ Windows güvenlik optimizasyonu yapılıyor...")
        threading.Thread(target=self._windows_security_thread, daemon=True).start()
    
    def _windows_security_thread(self):
        """Windows güvenlik thread'i"""
        try:
            commands = [
                "netsh advfirewall set allprofiles state on",  # Firewall'u aç
                "netsh advfirewall set allprofiles firewallpolicy blockinbound,allowoutbound"  # Gelenleri engelle, gidenlere izin ver
            ]
            
            results = []
            for cmd in commands:
                success, stdout, stderr = self.kernel_interface.execute_command(cmd, timeout=15)
                results.append(f"Komut: {cmd}\nSonuç: {'Başarılı' if success else 'Hatalı'}\nÇıktı: {stdout}\nHata: {stderr}\n")
            
            result = "🛡️ WINDOWS GÜVENLİK AYARLARI:\n" + "\n".join(results)
            self.after(0, lambda: self._show_command_result(result))
            self.after(0, lambda: self.show_message("✅ Windows güvenlik optimizasyonu tamamlandı"))
            
        except Exception as e:
            error_msg = f"❌ Güvenlik optimizasyonu hatası: {str(e)}"
            self.after(0, lambda: self._show_command_result(error_msg))
            self.after(0, lambda: self.show_message(error_msg))
    
    def clean_memory(self):
        """Bellek temizleme"""
        self.show_message("🧹 Bellek temizleniyor...")
        threading.Thread(target=self._clean_memory_thread, daemon=True).start()
    
    def _clean_memory_thread(self):
        """Bellek temizleme thread'i"""
        try:
            if self.current_os == "Windows":
                command = "echo EmptyWorkingSet > %temp%\\cleanmem.vbs && cscript %temp%\\cleanmem.vbs"
            else:
                command = "sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches"
            
            success, stdout, stderr = self.kernel_interface.execute_command(command, timeout=15)
            
            if success:
                result = "🧹 BELLEK TEMİZLEME TAMAMLANDI\n"
                result += f"Çıktı: {stdout}\n"
                if stderr:
                    result += f"Uyarı: {stderr}"
            else:
                result = f"❌ Bellek temizleme hatası: {stderr}"
            
            self.after(0, lambda: self._show_command_result(result))
            self.after(0, lambda: self.show_message("✅ Bellek temizlendi"))
            
        except Exception as e:
            error_msg = f"❌ Bellek temizleme hatası: {str(e)}"
            self.after(0, lambda: self._show_command_result(error_msg))
            self.after(0, lambda: self.show_message(error_msg))
    
    def detailed_system_status(self):
        """Detaylı sistem durumunu göster"""
        self.show_message("📊 Detaylı sistem durumu analiz ediliyor...")
        threading.Thread(target=self._check_detailed_system_status, daemon=True).start()
    
    def _check_detailed_system_status(self):
        """Detaylı sistem durumunu kontrol eder"""
        try:
            # CPU kullanımı
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Bellek bilgileri
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_available_gb = round(memory.available / (1024**3), 2)
            
            # Disk bilgileri
            try:
                disk = psutil.disk_usage('/')
                disk_usage = disk.percent
                disk_free_gb = round(disk.free / (1024**3), 2)
            except:
                disk_usage = "N/A"
                disk_free_gb = "N/A"
            
            # Ağ bilgileri
            net_io = psutil.net_io_counters()
            network_sent_mb = round(net_io.bytes_sent / (1024**2), 2)
            network_recv_mb = round(net_io.bytes_recv / (1024**2), 2)
            
            # Çalışma süresi
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            uptime_str = f"{uptime.days}g {uptime.seconds//3600}sa {(uptime.seconds%3600)//60}dak"
            
            message = "✅ DETAYLI SİSTEM DURUMU\n\n"
            message += "=== PERFORMANS ===\n"
            message += f"• CPU Kullanımı: {cpu_usage}%\n"
            message += f"• Bellek Kullanımı: {memory_usage}%\n"
            message += f"• Disk Kullanımı: {disk_usage}%\n"
            message += f"• Ağ Gönderim: {network_sent_mb} MB\n"
            message += f"• Ağ Alım: {network_recv_mb} MB\n\n"
            
            message += "=== SİSTEM SAĞLIĞI ===\n"
            message += f"• Çalışma Süresi: {uptime_str}\n"
            message += f"• Disk Boş Alan: {disk_free_gb} GB\n"
            message += f"• Kullanılabilir Bellek: {memory_available_gb} GB\n\n"
            
            message += "=== İŞLETİM SİSTEMİ ===\n"
            message += f"• OS: {platform.system()} {platform.release()}\n"
            message += f"• Mimari: {platform.architecture()[0]}\n"
            message += f"• İşlemci: {platform.processor()}\n"
            
            self.after(0, lambda: self._show_command_result(message))
            self.after(0, lambda: self.show_message("✅ Detaylı sistem durumu hazır"))
            
        except Exception as e:
            error_msg = f"❌ Sistem durumu analiz edilemedi: {str(e)}"
            self.after(0, lambda: self._show_command_result(error_msg))
            self.after(0, lambda: self.show_message(error_msg))
    
    def show_message(self, message):
        """Durum mesajını göster"""
        # MainWindow'daki status bar'ı kullanabilir veya konsola yazdırabilir
        print(f"Status: {message}")

# Test için
if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Kernel Tab Test")
    root.geometry("900x700")
    
    tab = KernelTab(root)
    tab.pack(fill="both", expand=True)
    
    root.mainloop()
