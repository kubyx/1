import psutil
import platform
import socket
from datetime import datetime

class KernelManager:
    def get_system_info(self):
        """Sistem bilgilerini toplar ve sözlük olarak döndürür"""
        try:
            # CPU Bilgileri
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_cores = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)
            
            # Bellek Bilgileri
            memory = psutil.virtual_memory()
            memory_total_gb = round(memory.total / (1024 ** 3), 2)
            memory_used_gb = round(memory.used / (1024 ** 3), 2)
            memory_percent = memory.percent
            
            # Disk Bilgileri (C: sürücüsü)
            try:
                disk = psutil.disk_usage('C:/')
                disk_total_gb = round(disk.total / (1024 ** 3), 2)
                disk_used_gb = round(disk.used / (1024 ** 3), 2)
                disk_percent = disk.percent
            except:
                disk_total_gb = disk_used_gb = disk_percent = "N/A"
            
            # Ağ Bilgileri
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            # Sistem Bilgileri
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            info = {
                "işletim_sistemi": f"{platform.system()} {platform.release()}",
                "sistem_sürümü": platform.version(),
                "işlemci": f"{cpu_percent}% Kullanım",
                "işlemci_frekansı": f"{cpu_freq.current if cpu_freq else 'N/A'} MHz" if cpu_freq else "N/A",
                "çekirdek_sayısı": f"{cpu_cores} Çekirdek, {cpu_threads} Thread",
                "bellek": f"{memory_used_gb}GB / {memory_total_gb}GB ({memory_percent}%)",
                "disk_c": f"{disk_used_gb}GB / {disk_total_gb}GB ({disk_percent}%)" if disk_total_gb != "N/A" else "N/A",
                "ağ_adı": hostname,
                "ip_adresi": ip_address,
                "açılış_zamanı": boot_time.strftime("%d.%m.%Y %H:%M:%S"),
                "çalışma_süresi": f"{uptime.days} gün, {uptime.seconds // 3600} saat"
            }
            
            return info
            
        except Exception as e:
            return {"hata": f"Sistem bilgileri alınamadı: {str(e)}"}
