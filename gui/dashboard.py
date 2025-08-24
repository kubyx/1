# gui/dashboard.py
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import psutil
import datetime

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.create_widgets()
        self.update_dashboard()
        
    def create_widgets(self):
        """Dashboard bileşenlerini oluştur"""
        # Ana başlık
        self.title_label = ctk.CTkLabel(self, text="SystemMasterAI Dashboard", 
                                      font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(10, 15))  # Alt boşluğu azalt

        # İki sütunlu grid
        self.main_grid = ctk.CTkFrame(self)
        self.main_grid.pack(fill="both", expand=True, padx=20, pady=(0, 15))  # Alt boşluğu azalt

        # Sol sütun - Sistem bilgileri (3 cm daha kısa)
        self.left_column = ctk.CTkFrame(self.main_grid, height=250)  # Yüksekliği azalt
        self.left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_column.grid_propagate(False)  # Yüksekliği koru

        # Sağ sütun - Hızlı eylemler
        self.right_column = ctk.CTkFrame(self.main_grid)
        self.right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.main_grid.columnconfigure(0, weight=1)
        self.main_grid.columnconfigure(1, weight=1)
        self.main_grid.rowconfigure(0, weight=1)

        # Sistem bilgileri (daha kompakt)
        self.create_system_info()

        # Hızlı eylemler
        self.create_quick_actions()

        # Alt kısım - Kaynak kullanımı
        self.create_resource_usage()

    def create_system_info(self):
        """Sistem bilgileri bölümünü oluştur (3 cm daha kısa)"""
        info_frame = ctk.CTkFrame(self.left_column)
        info_frame.pack(fill="both", expand=True, pady=5)  # Dikey boşluğu azalt

        ctk.CTkLabel(info_frame, text="Sistem Bilgileri", 
                   font=ctk.CTkFont(weight="bold")).pack(pady=5)  # Boşluğu azalt

        # Sistem bilgileri grid - Daha kompakt
        self.info_grid = ctk.CTkFrame(info_frame)
        self.info_grid.pack(fill="both", expand=True, padx=8, pady=5)  # Boşlukları azalt

        labels = ["İşletim Sistemi:", "İşlemci:", "Bellek:", "Disk:", "Ağ:", "Çalışma Süresi:"]
        self.info_labels = {}

        for i, label in enumerate(labels):
            # Daha kompakt satırlar
            row_frame = ctk.CTkFrame(self.info_grid, height=22)  # Satır yüksekliğini azalt
            row_frame.grid(row=i, column=0, sticky="ew", pady=1)  # Dikey boşluğu azalt
            row_frame.columnconfigure(1, weight=1)

            ctk.CTkLabel(row_frame, text=label, anchor="w", font=ctk.CTkFont(size=12)).grid(
                row=0, column=0, sticky="w", padx=2)
            
            value_label = ctk.CTkLabel(row_frame, text="Yükleniyor...", 
                                     font=ctk.CTkFont(size=11))
            value_label.grid(row=0, column=1, sticky="w", padx=2)
            self.info_labels[label] = value_label

        self.info_grid.columnconfigure(1, weight=1)

    def create_quick_actions(self):
        """Hızlı eylemler bölümünü oluştur"""
        actions_frame = ctk.CTkFrame(self.right_column)
        actions_frame.pack(fill="both", expand=True, pady=(0, 10))

        ctk.CTkLabel(actions_frame, text="Hızlı Eylemler", 
                   font=ctk.CTkFont(weight="bold")).pack(pady=10)

        # Eylem butonları
        actions = [
            ("🔄 Sistem Taraması", self.run_system_scan),
            ("🧹 Temizlik", self.run_cleanup),
            ("📊 Performans", self.show_performance),
            ("🔒 Güvenlik", self.run_security_check),
            ("💾 Yedekle", self.run_backup),
            ("🔄 Güncelle", self.check_updates)
        ]

        for i, (text, command) in enumerate(actions):
            btn = ctk.CTkButton(actions_frame, text=text, command=command,
                              height=35)
            btn.pack(fill="x", pady=2, padx=10)

    def create_resource_usage(self):
        """Kaynak kullanımı bölümünü oluştur"""
        usage_frame = ctk.CTkFrame(self.main_grid)
        usage_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))

        ctk.CTkLabel(usage_frame, text="Kaynak Kullanımı", 
                   font=ctk.CTkFont(weight="bold")).pack(pady=10)

        # İlerleme çubukları grid
        self.usage_grid = ctk.CTkFrame(usage_frame)
        self.usage_grid.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        resources = [
            ("CPU Kullanımı:", "cpu_bar"),
            ("Bellek Kullanımı:", "memory_bar"),
            ("Disk Kullanımı:", "disk_bar")
        ]

        self.usage_bars = {}

        for i, (label, key) in enumerate(resources):
            # Label ve yüzde
            row_frame = ctk.CTkFrame(self.usage_grid, height=25)
            row_frame.grid(row=i, column=0, sticky="ew", pady=1)
            row_frame.columnconfigure(1, weight=1)

            ctk.CTkLabel(row_frame, text=label, width=120).grid(row=0, column=0, sticky="w")

            percent_label = ctk.CTkLabel(row_frame, text="0%", width=40)
            percent_label.grid(row=0, column=1, sticky="e", padx=(0, 10))

            # İlerleme çubuğu
            progress_frame = ctk.CTkFrame(self.usage_grid, height=20)
            progress_frame.grid(row=i, column=1, sticky="ew", pady=1)

            progress_bar = ctk.CTkProgressBar(progress_frame, height=12)
            progress_bar.pack(fill="x", padx=(0, 10))
            progress_bar.set(0)

            self.usage_bars[key] = {
                "bar": progress_bar,
                "label": percent_label
            }

        self.usage_grid.columnconfigure(1, weight=2)

    def update_dashboard(self):
        """Dashboard'u güncelle"""
        try:
            # Sistem bilgileri
            system_info = self.get_system_info()
            self.info_labels["İşletim Sistemi:"].configure(text=system_info["os"])
            self.info_labels["İşlemci:"].configure(text=system_info["cpu"])
            self.info_labels["Bellek:"].configure(text=system_info["memory"])
            self.info_labels["Disk:"].configure(text=system_info["disk"])
            self.info_labels["Ağ:"].configure(text=system_info["network"])
            self.info_labels["Çalışma Süresi:"].configure(text=system_info["uptime"])

            # Kaynak kullanımı
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            self.usage_bars["cpu_bar"]["bar"].set(cpu_percent / 100)
            self.usage_bars["cpu_bar"]["label"].configure(text=f"{cpu_percent}%")

            self.usage_bars["memory_bar"]["bar"].set(memory.percent / 100)
            self.usage_bars["memory_bar"]["label"].configure(text=f"{memory.percent}%")

            self.usage_bars["disk_bar"]["bar"].set(disk.percent / 100)
            self.usage_bars["disk_bar"]["label"].configure(text=f"{disk.percent}%")

        except Exception as e:
            print(f"Dashboard güncelleme hatası: {e}")

        # 2 saniye sonra tekrar güncelle
        self.after(2000, self.update_dashboard)

    def get_system_info(self):
        """Sistem bilgilerini al"""
        try:
            # İşletim sistemi
            import platform
            os_info = f"{platform.system()} {platform.release()}"

            # İşlemci
            cpu_info = f"{psutil.cpu_count()} çekirdek"

            # Bellek
            memory = psutil.virtual_memory()
            memory_info = f"{memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB"

            # Disk
            disk = psutil.disk_usage('/')
            disk_info = f"{disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB"

            # Ağ
            network_info = "Bağlı" if psutil.net_if_stats() else "Bağlı değil"

            # Çalışma süresi
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            hours, remainder = divmod(uptime.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_info = f"{int(hours)}s {int(minutes)}d"

            return {
                "os": os_info,
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "network": network_info,
                "uptime": uptime_info
            }

        except Exception as e:
            return {"error": str(e)}

    def run_system_scan(self):
        """Sistem taraması çalıştır"""
        print("Sistem taraması başlatılıyor...")

    def run_cleanup(self):
        """Temizlik çalıştır"""
        print("Sistem temizliği başlatılıyor...")

    def show_performance(self):
        """Performans bilgilerini göster"""
        print("Performans bilgileri gösteriliyor...")

    def run_security_check(self):
        """Güvenlik kontrolü çalıştır"""
        print("Güvenlik kontrolü başlatılıyor...")

    def run_backup(self):
        """Yedekleme çalıştır"""
        print("Yedekleme başlatılıyor...")

    def check_updates(self):
        """Güncellemeleri kontrol et"""
        print("Güncellemeler kontrol ediliyor...")
