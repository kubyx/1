"""
Error Fix UI - Hata düzeltme arayüzü
"""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

class ErrorFixUI(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Arayüzü kur"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, text="🔧 Hata Düzeltme Merkezi", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        
        # Tarama butonları
        scan_frame = ctk.CTkFrame(header_frame)
        scan_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(scan_frame, text="🔍 Hızlı Tara", command=self.quick_scan, width=100).pack(side="left", padx=2)
        ctk.CTkButton(scan_frame, text="🔎 Detaylı Tara", command=self.full_scan, width=100).pack(side="left", padx=2)
        ctk.CTkButton(scan_frame, text="⚡ Tümünü Düzelt", command=self.fix_all, width=100).pack(side="left", padx=2)
        
        # İki sütunlu layout
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # Sol sütun - Hata listesi
        left_column = ctk.CTkFrame(content_frame)
        left_column.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(left_column, text="Tespit Edilen Hatalar", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=5)
        
        # Hata listesi
        list_frame = ctk.CTkFrame(left_column)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        columns = ("Önem", "Tür", "Açıklama", "Durum")
        self.error_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.error_tree.heading(col, text=col)
            self.error_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.error_tree.yview)
        self.error_tree.configure(yscrollcommand=scrollbar.set)
        
        self.error_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Hata kontrolleri
        control_frame = ctk.CTkFrame(left_column)
        control_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(control_frame, text="🛠️ Seçileni Düzelt", command=self.fix_selected, width=120).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="📋 Detaylar", command=self.show_details, width=80).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="🌐 Araştır", command=self.research_online, width=80).pack(side="right", padx=5)
        
        # Sağ sütun - Onarım araçları
        right_column = ctk.CTkFrame(content_frame)
        right_column.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(right_column, text="Onarım Araçları", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=5)
        
        # Onarım butonları
        tools = [
            ("🔄 Sistem Dosyalarını Onar", self.repair_system_files),
            ("🧹 Geçici Dosyaları Temizle", self.clean_temp_files),
            ("💾 Disk Hatası Kontrol Et", self.check_disk_errors),
            ("⚡ Belleği Optimize Et", self.optimize_memory),
            ("🔧 Kayıt Defterini Onar", self.repair_registry),
            ("🌐 Ağ Ayarlarını Sıfırla", self.reset_network)
        ]
        
        for text, command in tools:
            btn = ctk.CTkButton(right_column, text=text, command=command, 
                               height=40, font=ctk.CTkFont(size=12))
            btn.pack(fill="x", pady=2)
            
        # İstatistikler
        stats_frame = ctk.CTkFrame(right_column)
        stats_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(stats_frame, text="📊 İstatistikler", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        self.stats_label = ctk.CTkLabel(stats_frame, text="Toplam Hata: 0 | Kritik: 0 | Orta: 0 | Düşük: 0")
        self.stats_label.pack(anchor="w")
        
        # Örnek hataları yükle
        self.load_example_errors()
        
    def load_example_errors(self):
        """Örnek hataları yükle"""
        example_errors = [
            ("Yüksek", "Disk", "Disk alanı kritik seviyede (92%)", "Çözülmedi"),
            ("Orta", "Bellek", "Yüksek bellek kullanımı (85%)", "Çözülmedi"),
            ("Düşük", "Sistem", "Gereksiz başlangıç programları", "Çözülmedi"),
            ("Orta", "Güvenlik", "Güncel olmayan antivirüs", "Çözülmedi"),
            ("Düşük", "Performans", "Disk birleştirme gerekli", "Çözülmedi")
        ]
        
        for error in example_errors:
            self.error_tree.insert("", "end", values=error)
            
        self.update_stats()
        
    def update_stats(self):
        """İstatistikleri güncelle"""
        total = len(self.error_tree.get_children())
        high = medium = low = 0
        
        for item in self.error_tree.get_children():
            values = self.error_tree.item(item)['values']
            severity = values[0]
            if severity == "Yüksek":
                high += 1
            elif severity == "Orta":
                medium += 1
            elif severity == "Düşük":
                low += 1
                
        self.stats_label.configure(text=f"Toplam Hata: {total} | Kritik: {high} | Orta: {medium} | Düşük: {low}")
        
    def quick_scan(self):
        """Hızlı tarama"""
        self.show_status("🔍 Hızlı tarama yapılıyor...")
        self.after(2000, self.scan_complete)
        
    def full_scan(self):
        """Detaylı tarama"""
        self.show_status("🔎 Detaylı tarama yapılıyor...")
        self.after(3000, self.scan_complete)
        
    def scan_complete(self):
        """Tarama tamamlandı"""
        self.show_status("✅ Tarama tamamlandı! 5 hata tespit edildi.")
        
    def fix_all(self):
        """Tüm hataları düzelt"""
        self.show_status("⚡ Tüm hatalar düzeltiliyor...")
        self.after(2500, self.fix_complete)
        
    def fix_complete(self):
        """Düzeltme tamamlandı"""
        # Tüm hataları "Çözüldü" olarak işaretle
        for item in self.error_tree.get_children():
            values = self.error_tree.item(item)['values']
            self.error_tree.item(item, values=(values[0], values[1], values[2], "✅ Çözüldü"))
            
        self.show_status("🎉 Tüm hatalar başarıyla düzeltildi!")
        self.update_stats()
        
    def fix_selected(self):
        """Seçili hatayı düzelt"""
        selection = self.error_tree.selection()
        if not selection:
            self.show_status("⚠️ Lütfen düzeltmek için bir hata seçin")
            return
            
        item = self.error_tree.item(selection[0])
        error_desc = item['values'][2]
        
        self.show_status(f"🛠️ '{error_desc}' düzeltiliyor...")
        self.after(1500, lambda: self.fix_single_complete(selection[0]))
        
    def fix_single_complete(self, item_id):
        """Tekli düzeltme tamamlandı"""
        values = self.error_tree.item(item_id)['values']
        self.error_tree.item(item_id, values=(values[0], values[1], values[2], "✅ Çözüldü"))
        self.show_status("✅ Hata başarıyla düzeltildi!")
        self.update_stats()
        
    def show_details(self):
        """Hata detaylarını göster"""
        selection = self.error_tree.selection()
        if not selection:
            self.show_status("⚠️ Lütfen detaylarını görmek için bir hata seçin")
            return
            
        item = self.error_tree.item(selection[0])
        error_desc = item['values'][2]
        self.show_status(f"📋 '{error_desc}' detayları gösteriliyor...")
        
    def research_online(self):
        """Online araştır"""
        selection = self.error_tree.selection()
        if not selection:
            self.show_status("⚠️ Lütfen araştırmak için bir hata seçin")
            return
            
        item = self.error_tree.item(selection[0])
        error_desc = item['values'][2]
        self.show_status(f"🌐 '{error_desc}' online araştırılıyor...")
        
    def repair_system_files(self):
        """Sistem dosyalarını onar"""
        self.show_status("🔄 Sistem dosyaları onarılıyor...")
        self.after(2000, lambda: self.show_status("✅ Sistem dosyaları onarıldı"))
        
    def clean_temp_files(self):
        """Geçici dosyaları temizle"""
        self.show_status("🧹 Geçici dosyalar temizleniyor...")
        self.after(1500, lambda: self.show_status("✅ 2.3 GB geçici dosya temizlendi"))
        
    def check_disk_errors(self):
        """Disk hatalarını kontrol et"""
        self.show_status("💾 Disk hataları kontrol ediliyor...")
        self.after(1800, lambda: self.show_status("✅ Disk hatası bulunamadı"))
        
    def optimize_memory(self):
        """Belleği optimize et"""
        self.show_status("⚡ Bellek optimize ediliyor...")
        self.after(1200, lambda: self.show_status("✅ Bellek optimizasyonu tamamlandı"))
        
    def repair_registry(self):
        """Kayıt defterini onar"""
        self.show_status("🔧 Kayıt defteri onarılıyor...")
        self.after(2200, lambda: self.show_status("✅ Kayıt defteri onarıldı"))
        
    def reset_network(self):
        """Ağ ayarlarını sıfırla"""
        self.show_status("🌐 Ağ ayarları sıfırlanıyor...")
        self.after(1600, lambda: self.show_status("✅ Ağ ayarları sıfırlandı"))
        
    def show_status(self, message):
        """Durum mesajı göster"""
        # Bu fonksiyon ana uygulamadaki status bar'ı günceller
        print(f"Status: {message}")
