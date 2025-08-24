"""
Programs Tab - Program başlatma arayüzü
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import os

class ProgramsTab(ctk.CTkFrame):
    def __init__(self, parent, program_launcher):
        super().__init__(parent)
        self.parent = parent
        self.program_launcher = program_launcher
        self.setup_ui()
        
    def setup_ui(self):
        """Arayüzü kur"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık ve arama
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, text="🚀 Program Yöneticisi", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        
        # Arama çubuğu
        search_frame = ctk.CTkFrame(header_frame)
        search_frame.pack(side="right", padx=10)
        
        ctk.CTkLabel(search_frame, text="Ara:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=200)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", self.filter_programs)
        
        ctk.CTkButton(search_frame, text="Yenile", command=self.refresh_programs, width=80).pack(side="right", padx=5)
        
        # Program listesi
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        columns = ("Program", "Yol", "Tür")
        self.program_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.program_tree.heading(col, text=col)
            self.program_tree.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.program_tree.yview)
        self.program_tree.configure(yscrollcommand=scrollbar.set)
        
        self.program_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Kontrol butonları
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(control_frame, text="▶️ Başlat", command=self.launch_program, width=100).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="📋 Detaylar", command=self.show_details, width=100).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="⭐ Sık Kullanılan", command=self.add_favorite, width=100).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="➕ Yeni", command=self.new_program, width=100).pack(side="right", padx=5)
        
        # Kategori filtreleri
        category_frame = ctk.CTkFrame(main_frame)
        category_frame.pack(fill="x", pady=5)
        
        categories = ["Tümü", "Office", "Medya", "Geliştirme", "Oyun", "Sistem"]
        for i, category in enumerate(categories):
            btn = ctk.CTkButton(category_frame, text=category, 
                               command=lambda c=category: self.filter_by_category(c),
                               width=80)
            btn.pack(side="left", padx=2)
        
        # Programları yükle
        self.refresh_programs()
        
    def refresh_programs(self):
        """Program listesini yenile"""
        for item in self.program_tree.get_children():
            self.program_tree.delete(item)
            
        programs = self.program_launcher.get_program_list()
        
        for name, path in programs.items():
            program_type = "📁 Kısayol" if path.endswith('.lnk') else "⚙️ Program"
            self.program_tree.insert("", "end", values=(name, path, program_type))
            
    def filter_programs(self, event=None):
        """Programları filtrele"""
        search_term = self.search_var.get().lower()
        for item in self.program_tree.get_children():
            values = self.program_tree.item(item)['values']
            if search_term in str(values).lower():
                self.program_tree.item(item, tags=('match',))
            else:
                self.program_tree.item(item, tags=('no_match',))
    
    def filter_by_category(self, category):
        """Kategoriye göre filtrele"""
        if category == "Tümü":
            self.refresh_programs()
        else:
            for item in self.program_tree.get_children():
                values = self.program_tree.item(item)['values']
                program_name = values[0].lower()
                
                if category.lower() in program_name:
                    self.program_tree.item(item, tags=('match',))
                else:
                    self.program_tree.item(item, tags=('no_match',))
    
    def launch_program(self):
        """Programı başlat"""
        selection = self.program_tree.selection()
        if not selection:
            self.show_message("Lütfen bir program seçin")
            return
            
        item = self.program_tree.item(selection[0])
        program_name = item['values'][0]
        program_path = item['values'][1]
        
        success = self.program_launcher.launch_program(program_name)
        if success:
            self.show_message(f"✅ '{program_name}' başlatıldı")
        else:
            self.show_message(f"❌ '{program_name}' başlatılamadı")
    
    def show_details(self):
        """Program detaylarını göster"""
        selection = self.program_tree.selection()
        if not selection:
            self.show_message("Lütfen bir program seçin")
            return
            
        item = self.program_tree.item(selection[0])
        program_name = item['values'][0]
        program_path = item['values'][1]
        
        details = f"""
📋 Program Detayları:
-------------------
İsim: {program_name}
Yol: {program_path}
Tür: {'Kısayol (.lnk)' if program_path.endswith('.lnk') else 'Uygulama'}

💡 İşlemler:
• Programı başlatmak için 'Başlat' butonunu kullanın
• Yolunu kopyalamak için sağ tıklayın
"""
        self.show_message(details)
    
    def add_favorite(self):
        """Sık kullanılanlara ekle"""
        selection = self.program_tree.selection()
        if not selection:
            self.show_message("Lütfen bir program seçin")
            return
            
        item = self.program_tree.item(selection[0])
        program_name = item['values'][0]
        self.show_message(f"⭐ '{program_name}' sık kullanılanlara eklendi")
    
    def new_program(self):
        """Yeni program ekle"""
        program_path = tk.filedialog.askopenfilename(
            title="Program Seçin",
            filetypes=[("Programlar", "*.exe;*.lnk;*.bat"), ("Tüm Dosyalar", "*.*")]
        )
        
        if program_path:
            program_name = os.path.basename(program_path)
            success = self.program_launcher.launch_by_path(program_path)
            if success:
                self.show_message(f"✅ Yeni program başlatıldı: {program_name}")
                self.refresh_programs()
            else:
                self.show_message(f"❌ Program başlatılamadı: {program_name}")
    
    def show_message(self, message):
        """Mesaj göster"""
        messagebox.showinfo("Bilgi", message)
