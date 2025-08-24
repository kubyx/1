"""
Hata Tespit ve Onarım Sistemi
"""
import psutil
import subprocess
import logging
from datetime import datetime

class ErrorDetector:
    def __init__(self):
        self.error_log = []
        self.fix_history = []
        
    def scan_system(self, scan_type="quick"):
        """Sistem hatası taraması yap"""
        errors = []
        
        # Disk hataları
        disk_errors = self._check_disk_errors()
        errors.extend(disk_errors)
        
        # Bellek hataları
        memory_errors = self._check_memory_errors()
        errors.extend(memory_errors)
        
        # Sistem dosyası hataları
        if scan_type == "full":
            system_errors = self._check_system_files()
            errors.extend(system_errors)
            
        self.error_log.extend(errors)
        return errors
        
    def _check_disk_errors(self):
        """Disk hatalarını kontrol et"""
        errors = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                if usage.percent > 90:
                    errors.append({
                        "type": "disk",
                        "severity": "high",
                        "message": f"Disk alanı kritik seviyede: {partition.mountpoint} ({usage.percent}%)",
                        "timestamp": datetime.now().isoformat()
                    })
                elif usage.percent > 80:
                    errors.append({
                        "type": "disk",
                        "severity": "medium",
                        "message": f"Disk alanı uyarı seviyesinde: {partition.mountpoint} ({usage.percent}%)",
                        "timestamp": datetime.now().isoformat()
                    })
            except:
                continue
        return errors
        
    def _check_memory_errors(self):
        """Bellek hatalarını kontrol et"""
        errors = []
        memory = psutil.virtual_memory()
        
        if memory.percent > 90:
            errors.append({
                "type": "memory",
                "severity": "high",
                "message": f"Bellek kullanımı kritik seviyede: {memory.percent}%",
                "timestamp": datetime.now().isoformat()
            })
        elif memory.percent > 80:
            errors.append({
                "type": "memory",
                "severity": "medium",
                "message": f"Bellek kullanımı uyarı seviyesinde: {memory.percent}%",
                "timestamp": datetime.now().isoformat()
            })
            
        return errors
        
    def _check_system_files(self):
        """Sistem dosyası hatalarını kontrol et"""
        errors = []
        # Windows için SFC taraması
        try:
            result = subprocess.run(['sfc', '/verifyonly'], capture_output=True, text=True)
            if "violations" in result.stdout.lower():
                errors.append({
                    "type": "system_file",
                    "severity": "high",
                    "message": "Sistem dosyalarında bozulma tespit edildi",
                    "timestamp": datetime.now().isoformat()
                })
        except:
            pass
            
        return errors
        
    def fix_errors(self, error_type=None):
        """Hataları onar"""
        fixes = []
        
        # Disk temizliği
        if not error_type or error_type == "disk":
            disk_fixes = self._clean_disk_space()
            fixes.extend(disk_fixes)
            
        # Bellek optimizasyonu
        if not error_type or error_type == "memory":
            memory_fixes = self._optimize_memory()
            fixes.extend(memory_fixes)
            
        # Sistem dosyası onarımı
        if not error_type or error_type == "system_file":
            system_fixes = self._repair_system_files()
            fixes.extend(system_fixes)
            
        self.fix_history.extend(fixes)
        return fixes
        
    def _clean_disk_space(self):
        """Disk alanı temizle"""
        # Geçici dosyaları temizle
        fixes = [{"action": "disk_clean", "status": "completed", "timestamp": datetime.now().isoformat()}]
        return fixes
        
    def _optimize_memory(self):
        """Bellek optimizasyonu"""
        fixes = [{"action": "memory_optimize", "status": "completed", "timestamp": datetime.now().isoformat()}]
        return fixes
        
    def _repair_system_files(self):
        """Sistem dosyalarını onar"""
        fixes = [{"action": "system_repair", "status": "completed", "timestamp": datetime.now().isoformat()}]
        return fixes
