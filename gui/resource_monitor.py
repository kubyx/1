"""
Resource Monitor - Kaynak izleme arayüzü
"""
import tkinter as tk
import customtkinter as ctk
import psutil

class ResourceMonitor(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.update_metrics()
        
    def setup_ui(self):
        """Arayüzü kur"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(main_frame, text="📊 Gerçek Zamanlı Kaynak İzleyici", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Kaynak göstergeleri
        self.create_resource_bars(main_frame)
        
        # İstatistikler
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(fill="x", pady=10)
        
        self.stats_label = ctk.CTkLabel(stats_frame, text="Sistem yükleniyor...", font=ctk.CTkFont(size=12))
        self.stats_label.pack()
        
    def create_resource_bars(self, parent):
        """Kaynak çubuklarını oluştur"""
        # CPU
        cpu_frame = ctk.CTkFrame(parent)
        cpu_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(cpu_frame, text="CPU:", width=80).pack(side="left")
        self.cpu_bar = ctk.CTkProgressBar(cpu_frame)
        self.cpu_bar.pack(side="left", fill="x", expand=True, padx=5)
        self.cpu_label = ctk.CTkLabel(cpu_frame, text="0%", width=40)
        self.cpu_label.pack(side="right")
        
        # Bellek
        mem_frame = ctk.CTkFrame(parent)
        mem_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(mem_frame, text="Bellek:", width=80).pack(side="left")
        self.mem_bar = ctk.CTkProgressBar(mem_frame)
        self.mem_bar.pack(side="left", fill="x", expand=True, padx=5)
        self.mem_label = ctk.CTkLabel(mem_frame, text="0%", width=40)
        self.mem_label.pack(side="right")
        
        # Disk
        disk_frame = ctk.CTkFrame(parent)
        disk_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(disk_frame, text="Disk:", width=80).pack(side="left")
        self.disk_bar = ctk.CTkProgressBar(disk_frame)
        self.disk_bar.pack(side="left", fill="x", expand=True, padx=5)
        self.disk_label = ctk.CTkLabel(disk_frame, text="0%", width=40)
        self.disk_label.pack(side="right")
        
        # Ağ
        net_frame = ctk.CTkFrame(parent)
        net_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(net_frame, text="Ağ:", width=80).pack(side="left")
        self.net_bar = ctk.CTkProgressBar(net_frame)
        self.net_bar.pack(side="left", fill="x", expand=True, padx=5)
        self.net_label = ctk.CTkLabel(net_frame, text="0 KB/s", width=60)
        self.net_label.pack(side="right")
        
    def update_metrics(self):
        """Metrikleri güncelle"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent()
            self.cpu_bar.set(cpu_percent / 100)
            self.cpu_label.configure(text=f"{cpu_percent}%")
            
            # Bellek
            mem = psutil.virtual_memory()
            self.mem_bar.set(mem.percent / 100)
            self.mem_label.configure(text=f"{mem.percent}%")
            
            # Disk (ilk disk)
            try:
                disk = psutil.disk_usage('/')
                self.disk_bar.set(disk.percent / 100)
                self.disk_label.configure(text=f"{disk.percent}%")
            except:
                for part in psutil.disk_partitions():
                    try:
                        disk = psutil.disk_usage(part.mountpoint)
                        self.disk_bar.set(disk.percent / 100)
                        self.disk_label.configure(text=f"{disk.percent}%")
                        break
                    except:
                        continue
            
            # İstatistikleri güncelle
            self.update_stats()
            
        except Exception as e:
            print(f"Metrik güncelleme hatası: {e}")
        
        # 1 saniye sonra tekrar güncelle
        self.after(1000, self.update_metrics)
        
    def update_stats(self):
        """İstatistikleri güncelle"""
        try:
            stats = []
            stats.append(f"Çalışan Process'ler: {len(list(psutil.process_iter()))}")
            stats.append(f"Toplam Bellek: {psutil.virtual_memory().total // (1024**3)}GB")
            stats.append(f"Boş Disk: {psutil.disk_usage('/').free // (1024**3)}GB")
            
            self.stats_label.configure(text=" | ".join(stats))
            
        except Exception as e:
            print(f"İstatistik güncelleme hatası: {e}")
