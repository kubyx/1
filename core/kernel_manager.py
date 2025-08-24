"""
Kernel Manager - Kernel ayarlarını yönetir (Windows ve Linux)
"""
import os
import re
import subprocess
import platform
import winreg
import psutil
import json
from datetime import datetime
from .error_handler import ErrorHandler

class KernelManager:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.system = platform.system()
        
    def get_kernel_info(self):
        """Kernel bilgilerini getirir"""
        try:
            if self.system == "Linux":
                return self._get_linux_kernel_info()
            elif self.system == "Windows":
                return self._get_windows_kernel_info()
            else:
                return {"error": "Desteklenmeyen işletim sistemi"}
        except Exception as e:
            self.error_handler.log_error(f"Kernel bilgisi alınamadı: {str(e)}")
            return {"error": str(e)}
    
    def _get_linux_kernel_info(self):
        """Linux kernel bilgileri"""
        info = {}
        
        try:
            # Kernel versiyonu
            result = subprocess.run(['uname', '-r'], capture_output=True, text=True)
            info['version'] = result.stdout.strip()
            info['system'] = 'Linux'
            
            # Sistem bilgileri
            result = subprocess.run(['uname', '-a'], capture_output=True, text=True)
            info['full_info'] = result.stdout.strip()
            
            # Dağıtım bilgisi
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            info['distribution'] = line.split('=')[1].strip().strip('"')
                            break
            
            # CPU bilgileri
            if os.path.exists('/proc/cpuinfo'):
                with open('/proc/cpuinfo', 'r') as f:
                    cpu_info = f.read()
                    processor_count = cpu_info.count('processor\t:')
                    info['cpu_cores'] = processor_count
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_windows_kernel_info(self):
        """Windows kernel bilgileri"""
        info = {}
        
        try:
            # Windows versiyon bilgisi
            info['version'] = platform.version()
            info['build'] = platform.release()
            info['system'] = 'Windows'
            info['architecture'] = platform.architecture()[0]
            
            # İşlemci bilgileri
            info['processor'] = platform.processor()
            info['cpu_cores'] = os.cpu_count()
            
            # Bellek bilgisi
            memory = psutil.virtual_memory()
            info['total_memory'] = f"{memory.total // (1024**3)} GB"
            info['available_memory'] = f"{memory.available // (1024**3)} GB"
            
            # Windows özellikleri
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                    product_name = winreg.QueryValueEx(key, "ProductName")[0]
                    info['product_name'] = product_name
                    current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                    info['current_build'] = current_build
            except:
                info['product_name'] = "Bilinmeyen"
                
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_kernel_parameters(self):
        """Linux kernel parametrelerini getirir"""
        parameters = {}
        
        try:
            if self.system != "Linux":
                return {"error": "Sadece Linux destekleniyor"}
                
            # /proc/sys/kernel/ dizinindeki parametreler
            kernel_path = "/proc/sys/kernel/"
            if os.path.exists(kernel_path):
                for item in os.listdir(kernel_path):
                    item_path = os.path.join(kernel_path, item)
                    if os.path.isfile(item_path):
                        try:
                            with open(item_path, 'r') as f:
                                parameters[item] = f.read().strip()
                        except PermissionError:
                            parameters[item] = "İzin reddedildi"
                        except Exception:
                            parameters[item] = "Okunamadı"
            
            return parameters
            
        except Exception as e:
            return {"error": str(e)}
    
    def update_kernel_parameter(self, parameter, value):
        """Linux kernel parametresini günceller"""
        try:
            if self.system != "Linux":
                return {"success": False, "message": "Sadece Linux destekleniyor"}
                
            param_path = f"/proc/sys/kernel/{parameter}"
            if not os.path.exists(param_path):
                return {"success": False, "message": "Parametre bulunamadı"}
            
            # Geçici değişiklik (sudo gerektirebilir)
            cmd = f"echo '{value}' | sudo tee {param_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"success": True, "message": "Parametre güncellendi"}
            else:
                return {"success": False, "message": result.stderr}
                
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_windows_registry_parameters(self):
        """Windows registry parametrelerini getirir"""
        params = {}
        
        try:
            if self.system != "Windows":
                return {"error": "Sadece Windows destekleniyor"}
            
            # Önemli registry yolları ve değerleri
            registry_settings = [
                (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "PagingFiles"),
                (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache"),
                (r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "MaxUserPort"),
                (r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpTimedWaitDelay"),
                (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "EnableLUA"),
                (r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", "AutoAdminLogon"),
            ]
            
            for key_path, value_name in registry_settings:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        value, reg_type = winreg.QueryValueEx(key, value_name)
                        params[f"{key_path}\\{value_name}"] = str(value)
                except FileNotFoundError:
                    params[f"{key_path}\\{value_name}"] = "Bulunamadı"
                except PermissionError:
                    params[f"{key_path}\\{value_name}"] = "İzin reddedildi"
                except Exception:
                    params[f"{key_path}\\{value_name}"] = "Okunamadı"
                    
            return params
            
        except Exception as e:
            return {"error": str(e)}
    
    def update_windows_registry(self, key_path, value_name, value_data, value_type=winreg.REG_DWORD):
        """Windows registry değerini günceller"""
        try:
            if self.system != "Windows":
                return {"success": False, "message": "Sadece Windows destekleniyor"}
                
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, value_name, 0, value_type, value_data)
            return {"success": True, "message": "Registry güncellendi"}
        except PermissionError:
            return {"success": False, "message": "Yönetici izni gerekiyor"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def optimize_windows_performance(self):
        """Windows performans optimizasyonu yapar"""
        optimizations = []
        
        try:
            if self.system != "Windows":
                return ["Sadece Windows destekleniyor"]
            
            # Güç planı ayarı - Yüksek performans
            try:
                result = subprocess.run(
                    ['powercfg', '-setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'],
                    capture_output=True, text=True, shell=True
                )
                if result.returncode == 0:
                    optimizations.append("Güç planı: Yüksek performans")
            except:
                optimizations.append("Güç planı değiştirilemedi")
            
            # Prefetch ayarı
            try:
                self.update_windows_registry(
                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
                    "EnablePrefetcher", 1
                )
                optimizations.append("Prefetch optimize edildi")
            except:
                optimizations.append("Prefetch ayarlanamadı")
            
            # Sistem önbelleği
            try:
                self.update_windows_registry(
                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                    "LargeSystemCache", 1
                )
                optimizations.append("Sistem önbelleği etkinleştirildi")
            except:
                optimizations.append("Sistem önbelleği ayarlanamadı")
            
            return optimizations
            
        except Exception as e:
            return [f"Hata: {str(e)}"]
    
    def windows_power_save(self):
        """Windows pil tasarrufu optimizasyonu"""
        optimizations = []
        
        try:
            if self.system != "Windows":
                return ["Sadece Windows destekleniyor"]
            
            # Güç planı ayarı - Pil tasarrufu
            try:
                result = subprocess.run(
                    ['powercfg', '-setactive', 'a1841308-3541-4fab-bc81-f71556f20b4a'],
                    capture_output=True, text=True, shell=True
                )
                if result.returncode == 0:
                    optimizations.append("Güç planı: Pil tasarrufu")
            except:
                optimizations.append("Güç planı değiştirilemedi")
            
            # Ekran zaman aşımı
            try:
                subprocess.run(['powercfg', '-change', '-monitor-timeout-ac', '5'], shell=True)
                subprocess.run(['powercfg', '-change', '-monitor-timeout-dc', '3'], shell=True)
                optimizations.append("Ekran zaman aşımı ayarlandı")
            except:
                optimizations.append("Ekran zaman aşımı ayarlanamadı")
            
            # Disk zaman aşımı
            try:
                subprocess.run(['powercfg', '-change', '-disk-timeout-ac', '15'], shell=True)
                subprocess.run(['powercfg', '-change', '-disk-timeout-dc', '10'], shell=True)
                optimizations.append("Disk zaman aşımı ayarlandı")
            except:
                optimizations.append("Disk zaman aşımı ayarlanamadı")
            
            return optimizations
            
        except Exception as e:
            return [f"Hata: {str(e)}"]
    
    def windows_security_optimize(self):
        """Windows güvenlik optimizasyonu"""
        optimizations = []
        
        try:
            if self.system != "Windows":
                return ["Sadece Windows destekleniyor"]
            
            # UAC ayarı
            try:
                self.update_windows_registry(
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                    "EnableLUA", 1
                )
                optimizations.append("Kullanıcı Hesabı Denetimi etkin")
            except:
                optimizations.append("UAC ayarlanamadı")
            
            # Otomatik oturum açma kapatma
            try:
                self.update_windows_registry(
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
                    "AutoAdminLogon", 0
                )
                optimizations.append("Otomatik oturum açma devre dışı")
            except:
                optimizations.append("Otomatik oturum açma ayarlanamadı")
            
            # Güvenlik duvarı kontrolü
            try:
                result = subprocess.run(
                    ['netsh', 'advfirewall', 'show', 'allprofiles', 'state'],
                    capture_output=True, text=True, shell=True
                )
                if "Açık" in result.stdout:
                    optimizations.append("Güvenlik duvarı: Açık")
                else:
                    optimizations.append("Güvenlik duvarı: Kapalı")
            except:
                optimizations.append("Güvenlik duvarı kontrol edilemedi")
            
            return optimizations
            
        except Exception as e:
            return [f"Hata: {str(e)}"]
    
    def manage_windows_services(self):
        """Windows servis durumlarını getirir"""
        services = {}
        
        try:
            if self.system != "Windows":
                return {"error": "Sadece Windows destekleniyor"}
            
            # Önemli servisler
            important_services = [
                "WinDefend", "wuauserv", "bits", "Spooler",
                "EventLog", "Dhcp", "Dnscache", "LanmanServer"
            ]
            
            for service in important_services:
                try:
                    result = subprocess.run(
                        ['sc', 'query', service],
                        capture_output=True, text=True, shell=True
                    )
                    if "RUNNING" in result.stdout:
                        services[service] = "Çalışıyor"
                    elif "STOPPED" in result.stdout:
                        services[service] = "Durduruldu"
                    else:
                        services[service] = "Bilinmiyor"
                except:
                    services[service] = "Hata"
            
            return services
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_system_info(self):
        """Detaylı sistem bilgilerini getirir"""
        info = {}
        
        try:
            # İşletim sistemi bilgisi
            info['sistem'] = platform.system()
            info['sürüm'] = platform.version()
            info['mimari'] = platform.architecture()[0]
            info['host_adi'] = platform.node()
            
            # CPU bilgileri
            info['işlemci_çekirdekleri'] = psutil.cpu_count(logical=False)
            info['işlemci_threadleri'] = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            info['işlemci_frekansı'] = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "Bilinmiyor"
            
            # Bellek bilgileri
            memory = psutil.virtual_memory()
            info['toplam_bellek'] = f"{memory.total // (1024**3)} GB"
            info['kullanılabilir_bellek'] = f"{memory.available // (1024**3)} GB"
            info['bellek_kullanımı'] = f"%{memory.percent}"
            
            # Disk bilgileri
            disk = psutil.disk_usage('/')
            info['toplam_disk'] = f"{disk.total // (1024**3)} GB"
            info['boş_disk'] = f"{disk.free // (1024**3)} GB"
            info['disk_kullanımı'] = f"%{disk.percent}"
            
            # Boot zamanı
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            info['açılış_zamanı'] = boot_time.strftime("%d.%m.%Y %H:%M:%S")
            
            # Çalışan prosesler
            info['çalışan_prosesler'] = len(psutil.pids())
            
            return info
            
        except Exception as e:
            return {"hata": str(e)}
