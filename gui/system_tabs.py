"""
System Tabs - Sistem kontrol sekmeleri
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import psutil
import subprocess

class SystemTabs(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Arayüzü kur"""
        # Notebook (iç sekmeler)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Process Manager sekmesi
        self.tab_process = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_process, text="📊 Process Manager")
        
        # System Tools sekmesi
        self.tab_tools = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_tools, text="🛠️ System Tools")
        
        # Services sekmesi
        self.tab_services = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_services, text="🔧 Services")
        
        # Sekmeleri oluştur
        self.create_process_tab()
        self.create_tools_tab()
        self.create_services_tab()
        
    def create_process_tab(self):
        """Process Manager sekmesi"""
        # Arama çubuğu
        search_frame = ctk.CTkFrame(self.tab_process)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(search_frame, text="Ara:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_entry.bind("<KeyRelease>", self.filter_processes)
        
        ctk.CTkButton(search_frame, text="Yenile", command=self.refresh_processes, width=80).pack(side="right", padx=5)
        
        # Process listesi
        list_frame = ctk.CTkFrame(self.tab_process)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Treeview
        columns = ("PID", "İsim", "CPU%", "Bellek%", "Durum")
        self.process_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Kontrol butonları
        control_frame = ctk.CTkFrame(self.tab_process)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(control_frame, text="Sonlandır", command=self.kill_process, width=100).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Zorla Kapat", command=self.force_kill, width=100).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Detaylar", command=self.show_details, width=100).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Yeni Process", command=self.new_process, width=100).pack(side="right", padx=5)
        
        # İlk verileri yükle
        self.refresh_processes()
        
    def create_tools_tab(self):
        """System Tools sekmesi"""
        tools_frame = ctk.CTkFrame(self.tab_tools)
        tools_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sistem araçları
        tools = [
            ("🎯 Görev Yöneticisi", "taskmgr.exe"),
            ("🔧 Aygıt Yöneticisi", "devmgmt.msc"),
            ("💾 Disk Yönetimi", "diskmgmt.msc"),
            ("🔄 Hizmetler", "services.msc"),
            ("📊 Olay Görüntüleyici", "eventvwr.msc"),
            ("🔐 Kayıt Defteri", "regedit.exe"),
            ("⚙️ Sistem Yapılandırma", "msconfig.exe"),
            ("🌐 Ağ Bağlantıları", "ncpa.cpl"),
            ("🛡️ Güvenlik Duvarı", "firewall.cpl"),
            ("📋 Programlar", "appwiz.cpl")
        ]
        
        for i, (name, cmd) in enumerate(tools):
            row, col = divmod(i, 2)
            btn = ctk.CTkButton(tools_frame, text=name, command=lambda c=cmd: self.run_tool(c),
                               height=40, font=ctk.CTkFont(size=12))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Grid ayarları
        for i in range(2):
            tools_frame.columnconfigure(i, weight=1)
        for i in range((len(tools) + 1) // 2):
            tools_frame.rowconfigure(i, weight=1)
            
    def create_services_tab(self):
        """Services sekmesi"""
        services_frame = ctk.CTkFrame(self.tab_services)
        services_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(services_frame, text="Sistem Hizmetleri", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Services listesi
        list_frame = ctk.CTkFrame(services_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("Hizmet", "Durum", "Tür", "Başlangıç")
        self.services_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.services_tree.heading(col, text=col)
            self.services_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=scrollbar.set)
        
        self.services_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Kontrol butonları
        control_frame = ctk.CTkFrame(services_frame)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(control_frame, text="Başlat", command=self.start_service, width=80).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Durdur", command=self.stop_service, width=80).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="Yenile", command=self.refresh_services, width=80).pack(side="right", padx=5)
        
        # Servisleri yükle
        self.refresh_services()
        
    def refresh_processes(self):
        """Process listesini yenile"""
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
            
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # CPU kullanımına göre sırala
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        for proc in processes[:100]:  # İlk 100 process
            self.process_tree.insert("", "end", values=(
                proc['pid'],
                proc['name'][:30],
                f"{proc['cpu_percent']:.1f}" if proc['cpu_percent'] is not None else "N/A",
                f"{proc['memory_percent']:.1f}" if proc['memory_percent'] is not None else "N/A",
                proc['status']
            ))
    
    def filter_processes(self, event=None):
        """Process'leri filtrele"""
        search_term = self.search_var.get().lower()
        for item in self.process_tree.get_children():
            values = self.process_tree.item(item)['values']
            if search_term in str(values).lower():
                self.process_tree.item(item, tags=('match',))
                self.process_tree.selection_set(item)
            else:
                self.process_tree.item(item, tags=('no_match',))
    
    def kill_process(self):
        """Process'i sonlandır"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen bir process seçin")
            return
            
        item = self.process_tree.item(selection[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            messagebox.showinfo("Başarılı", f"Process sonlandırıldı: {name}")
            self.refresh_processes()
        except Exception as e:
            messagebox.showerror("Hata", f"Process sonlandırılamadı: {e}")
    
    def force_kill(self):
        """Process'i zorla kapat"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen bir process seçin")
            return
            
        item = self.process_tree.item(selection[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        try:
            proc = psutil.Process(pid)
            proc.kill()
            messagebox.showinfo("Başarılı", f"Process zorla kapatıldı: {name}")
            self.refresh_processes()
        except Exception as e:
            messagebox.showerror("Hata", f"Process kapatılamadı: {e}")
    
    def show_details(self):
        """Process detaylarını göster"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen bir process seçin")
            return
            
        item = self.process_tree.item(selection[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        try:
            proc = psutil.Process(pid)
            details = f"""
Process Detayları:
-----------------
PID: {pid}
İsim: {name}
Durum: {proc.status()}
CPU: {proc.cpu_percent()}%
Bellek: {proc.memory_percent():.1f}%
Çalıştırılabilir: {proc.exe()}
Çalışma Dizini: {proc.cwd()}
Komut Satırı: {' '.join(proc.cmdline())}
"""
            messagebox.showinfo("Process Detayları", details)
        except Exception as e:
            messagebox.showerror("Hata", f"Detaylar alınamadı: {e}")
    
    def new_process(self):
        """Yeni process başlat"""
        command = tk.simpledialog.askstring("Yeni Process", "Çalıştırılacak komutu girin:")
        if command:
            try:
                subprocess.Popen(command, shell=True)
                messagebox.showinfo("Başarılı", f"Process başlatıldı: {command}")
                self.refresh_processes()
            except Exception as e:
                messagebox.showerror("Hata", f"Process başlatılamadı: {e}")
    
    def run_tool(self, command):
        """Sistem aracını çalıştır"""
        try:
            subprocess.Popen(command, shell=True)
        except Exception as e:
            messagebox.showerror("Hata", f"Araç çalıştırılamadı: {e}")
    
    def refresh_services(self):
        """Servis listesini yenile"""
        for item in self.services_tree.get_children():
            self.services_tree.delete(item)
            
        # Basit servis listesi (gerçek implementasyon için win32service modülü gerekli)
        services = [
            ("Winmgmt", "Çalışıyor", "Otomatik", "Yerel Sistem"),
            ("EventLog", "Çalışıyor", "Otomatik", "Yerel Sistem"),
            ("Dhcp", "Çalışıyor", "Otomatik", "Yerel Sistem"),
            ("Dnscache", "Çalışıyor", "Otomatik", "Yerel Sistem"),
            ("Spooler", "Çalışıyor", "Otomatik", "Yerel Sistem"),
            ("TermService", "Çalışıyor", "Otomatik", "Yerel Sistem"),
        ]
        
        for service in services:
            self.services_tree.insert("", "end", values=service)
    
    def start_service(self):
        """Servisi başlat"""
        messagebox.showinfo("Bilgi", "Servis başlatma özelliği aktif edilecek")
    
    def stop_service(self):
        """Servisi durdur"""
        messagebox.showinfo("Bilgi", "Servis durdurma özelliği aktif edilecek")
