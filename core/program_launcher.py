"""
Program Launcher - .lnk ve diğer programları açma modülü
"""
import os
import subprocess
import logging
from pathlib import Path

class ProgramLauncher:
    def __init__(self):
        self.installed_programs = {}
        self.scan_installed_programs()
        
    def scan_installed_programs(self):
        """Yüklü programları ve .lnk dosyalarını tara"""
        self.installed_programs = {}
        
        # Windows başlangıç menüsü yolları
        start_menu_paths = [
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            os.path.join(os.environ['USERPROFILE'], 
                        r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs")
        ]
        
        for path in start_menu_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.lnk'):
                            full_path = os.path.join(root, file)
                            program_name = os.path.splitext(file)[0]
                            self.installed_programs[program_name] = full_path
        
        # Özel programları elle ekle (sizin listeye göre)
        special_programs = {
            "Acronis True Image": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Acronis True Image.lnk",
            "Adobe Acrobat": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Adobe Acrobat.lnk",
            "Ashampoo Driver Updater": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Ashampoo Driver Updater.lnk",
            "GPT4All": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\GPT4All\GPT4All.lnk",
            "J.A.V.I.S": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\J.A.V.I.S\Jarvis.lnk",
            "Media Player Classic": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\K-Lite Codec Pack\Media Player Classic.lnk",
            "LM Studio": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\LM Studio.lnk",
            "Microsoft Office Word 2007": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Office\Microsoft Office Word 2007.lnk",
            "Ollama": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Ollama.lnk",
            "Opera Browser": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Opera Browser.lnk",
            "PowerISO": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerISO\PowerISO.lnk",
            "PowerShell 7": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerShell\PowerShell 7 (x64).lnk",
            "PyCharm": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\JetBrains\PyCharm 2025.1.1.1.lnk",
            "Python IDLE": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Python 3.10\IDLE (Python 3.10 64-bit).lnk",
            "Qt Creator": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Qt\Qt Creator 16.0.2 (Enterprise).lnk",
            "Rainmeter": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Rainmeter.lnk",
            "Age2HD": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\by.xatab\Run Age2HD.lnk",
            "SRS9": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\SRS9\Subliminal Recording System 9.0.lnk",
            "VLC": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\VideoLAN\VLC media player.lnk",
            "Visual Studio 2022": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Visual Studio 2022.lnk",
            "Visual Studio Code": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code\Visual Studio Code.lnk",
            "VMware Workstation": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\VMware\VMware Workstation Pro.lnk",
            "WinRAR": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\WinRAR\WinRAR.lnk"
        }
        
        self.installed_programs.update(special_programs)
        
        logging.info(f"{len(self.installed_programs)} program tespit edildi")
        return self.installed_programs
    
    def launch_program(self, program_name):
        """Programı başlat"""
        if program_name in self.installed_programs:
            try:
                program_path = self.installed_programs[program_name]
                # .lnk dosyasını aç
                if program_path.endswith('.lnk'):
                    # Windows'ta .lnk dosyalarını açmak için
                    os.startfile(program_path)
                else:
                    # Diğer executable'ları aç
                    subprocess.Popen(program_path, shell=True)
                
                logging.info(f"Program başlatıldı: {program_name}")
                return True
                
            except Exception as e:
                logging.error(f"Program başlatma hatası ({program_name}): {e}")
                return False
        else:
            logging.warning(f"Program bulunamadı: {program_name}")
            return False
    
    def launch_by_path(self, program_path):
        """Doğrudan yol ile program başlat"""
        try:
            if os.path.exists(program_path):
                if program_path.endswith('.lnk'):
                    os.startfile(program_path)
                else:
                    subprocess.Popen(program_path, shell=True)
                logging.info(f"Program başlatıldı: {program_path}")
                return True
            else:
                logging.warning(f"Dosya bulunamadı: {program_path}")
                return False
        except Exception as e:
            logging.error(f"Program başlatma hatası ({program_path}): {e}")
            return False
    
    def get_program_list(self, category=None):
        """Program listesini getir"""
        if category:
            return {k: v for k, v in self.installed_programs.items() if category.lower() in k.lower()}
        return self.installed_programs
    
    def search_programs(self, search_term):
        """Programları ara"""
        results = {}
        search_term = search_term.lower()
        
        for name, path in self.installed_programs.items():
            if search_term in name.lower() or search_term in path.lower():
                results[name] = path
        
        return results
