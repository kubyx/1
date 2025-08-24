"""
Hata Yönetim Sistemi - Sistem hatalarını tespit ve onarım
"""
import logging
import subprocess
import psutil
from datetime import datetime
from .system_controller import SystemController

class ErrorHandler:
    def __init__(self):
        self.system_controller = SystemController()
        self.error_log = []
        self.fix_history = []
        
    def scan_errors(self, scan_type="quick"):
        """Sistem hatalarını tara"""
        errors = []
        
        # Disk hataları
        disk_errors = self._check_disk_errors()
        errors.extend(disk_errors)
        
        # Bellek hataları
        memory_errors = self._check_memory_errors()
        errors.extend(memory_errors)
        
        # İşlem hataları
        process_errors = self._check_process_errors()
        errors.extend(process_errors)
        
        # Sistem dosyası hataları (sadece full scan'de)
        if scan_type == "full":
            system_errors = self._check_system_files()
            errors.extend(system_errors)
            
        self.error_log.extend(errors)
        return errors
        
    def _check_disk_errors(self):
        """Disk hatalarını kontrol et"""
        errors = []
        try:
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    if usage.percent > 90:
                        errors.append({
                            "type": "disk",
                            "severity": "high",
                            "message": f"Disk alanı kritik: {partition.mountpoint} ({usage.percent}%)",
                            "timestamp": datetime.now().isoformat()
                        })
                    elif usage.percent > 80:
                        errors.append({
                            "type": "disk",
                            "severity": "medium", 
                            "message": f"Disk alanı uyarı: {partition.mountpoint} ({usage.percent}%)",
                            "timestamp": datetime.now().isoformat()
                        })
                except:
                    continue
        except Exception as e:
            logging.error(f"Disk kontrol hatası: {e}")
            
        return errors
        
    def _check_memory_errors(self):
        """Bellek hatalarını kontrol et"""
        errors = []
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                errors.append({
                    "type": "memory",
                    "severity": "high",
                    "message": f"Bellek kullanımı kritik: {memory.percent}%",
                    "timestamp": datetime.now().isoformat()
                })
            elif memory.percent > 80:
                errors.append({
                    "type": "memory", 
                    "severity": "medium",
                    "message": f"Bellek kullanımı uyarı: {memory.percent}%",
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logging.error(f"Bellek kontrol hatası: {e}")
            
        return errors
        
    def _check_process_errors(self):
        """İşlem hatalarını kontrol et"""
        errors = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    if proc.info['status'] == psutil.STATUS_ZOMBIE:
                        errors.append({
                            "type": "process",
                            "severity": "medium",
                            "message": f"Zombie process: {proc.info['name']} (PID: {proc.info['pid']})",
                            "timestamp": datetime.now().isoformat()
                        })
                except:
                    continue
        except Exception as e:
            logging.error(f"İşlem kontrol hatası: {e}")
            
        return errors
        
    def _check_system_files(self):
        """Sistem dosyası hatalarını kontrol et"""
        errors = []
        try:
            # Windows için SFC taraması
            if hasattr(self.system_controller, 'run_windows_tool'):
                result = subprocess.run(['sfc', '/verifyonly'], 
                                      capture_output=True, text=True, timeout=30)
                if "violations" in result.stdout.lower() or "corruption" in result.stdout.lower():
                    errors.append({
                        "type": "system_file",
                        "severity": "high",
                        "message": "Sistem dosyalarında bozulma tespit edildi",
                        "timestamp": datetime.now().isoformat()
                    })
        except Exception as e:
            logging.error(f"Sistem dosyası kontrol hatası: {e}")
            
        return errors
        
    def fix_errors(self, error_type=None):
        """Hataları onar"""
        fixes = []
        
        try:
            # Disk hatalarını onar
            if not error_type or error_type == "disk":
                disk_fixes = self._fix_disk_errors()
                fixes.extend(disk_fixes)
                
            # Bellek hatalarını onar
            if not error_type or error_type == "memory":
                memory_fixes = self._fix_memory_errors()
                fixes.extend(memory_fixes)
                
            # İşlem hatalarını onar
            if not error_type or error_type == "process":
                process_fixes = self._fix_process_errors()
                fixes.extend(process_fixes)
                
            self.fix_history.extend(fixes)
            
        except Exception as e:
            logging.error(f"Hata onarım hatası: {e}")
            
        return fixes
        
    def _fix_disk_errors(self):
        """Disk hatalarını onar"""
        fixes = []
        try:
            # Disk temizleme komutunu çalıştır
            if hasattr(self.system_controller, 'execute_command'):
                result = self.system_controller.execute_command("cleanmgr")
                if result:
                    fixes.append({
                        "action": "disk_clean",
                        "status": "completed",
                        "timestamp": datetime.now().isoformat()
                    })
        except Exception as e:
            logging.error(f"Disk onarım hatası: {e}")
            
        return fixes
        
    def _fix_memory_errors(self):
        """Bellek hatalarını onar"""
        fixes = []
        try:
            # Bellek optimizasyonu için gereksiz process'leri kapat
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    if proc.info['memory_percent'] > 5 and proc.info['name'].lower() in [
                        'chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe'
                    ]:
                        proc.terminate()
                        fixes.append({
                            "action": f"process_kill_{proc.info['name']}",
                            "status": "completed",
                            "timestamp": datetime.now().isoformat()
                        })
                except:
                    continue
                    
        except Exception as e:
            logging.error(f"Bellek onarım hatası: {e}")
            
        return fixes
        
    def _fix_process_errors(self):
        """İşlem hatalarını onar"""
        fixes = []
        try:
            # Zombie process'leri temizle
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    if proc.info['status'] == psutil.STATUS_ZOMBIE:
                        proc.terminate()
                        fixes.append({
                            "action": f"zombie_kill_{proc.info['name']}",
                            "status": "completed", 
                            "timestamp": datetime.now().isoformat()
                        })
                except:
                    continue
                    
        except Exception as e:
            logging.error(f"İşlem onarım hatası: {e}")
            
        return fixes
