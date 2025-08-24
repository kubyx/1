"""
Error Fix UI - Hata giderme arayüzü
"""
import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
import customtkinter as ctk
import os
import glob
import threading
from core.ai_integration import AIIntegration

class ErrorFixUI(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.ai_integration = None
        self.setup_ui()
        self.initialize_ai()
        
    def setup_ui(self):
        """Arayüzü kur"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        title_frame = ctk.CTkFrame(main_frame)
        title_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(title_frame, text="🔧 Advanced Error Fixer", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        # Tarama butonları
        scan_frame = ctk.CTkFrame(main_frame)
        scan_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(scan_frame, text="📁 Tüm Projeyi Tara", 
                     command=self.scan_entire_project, width=150).pack(side="left", padx=5)
        
        ctk.CTkButton(scan_frame, text="🐍 Python Dosyalarını Tara", 
                     command=self.scan_python_files, width=150).pack(side="left", padx=5)
        
        ctk.CTkButton(scan_frame, text="⚙️ Config Dosyalarını Tara", 
                     command=self.scan_config_files, width=150).pack(side="left", padx=5)
        
        ctk.CTkButton(scan_frame, text="📊 Özel Klasör Seç", 
                     command=self.select_custom_folder, width=150).pack(side="left", padx=5)
        
        # Sonuçlar alanı
        results_frame = ctk.CTkFrame(main_frame)
        results_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Hata listesi
        ctk.CTkLabel(results_frame, text="Tespit Edilen Hatalar:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5, 0))
        
        self.error_tree = ttk.Treeview(results_frame, columns=("file", "line", "error", "severity"), 
                                      show="headings", height=8)
        self.error_tree.heading("file", text="Dosya")
        self.error_tree.heading("line", text="Satır")
        self.error_tree.heading("error", text="Hata")
        self.error_tree.heading("severity", text="Önem")
        
        self.error_tree.column("file", width=200)
        self.error_tree.column("line", width=60)
        self.error_tree.column("error", width=300)
        self.error_tree.column("severity", width=80)
        
        self.error_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.error_tree.yview)
        self.error_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Hata detayları ve AI çözümü
        detail_frame = ctk.CTkFrame(main_frame)
        detail_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(detail_frame, text="Hata Detayları ve AI Çözümü:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5, 0))
        
        self.detail_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, 
                                                   font=("Consolas", 10), height=8)
        self.detail_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.detail_text.config(state="disabled")
        
        # Çözüm butonları
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill="x")
        
        ctk.CTkButton(action_frame, text="🔄 Seçili Hatayı Onar", 
                     command=self.fix_selected_error, width=150).pack(side="left", padx=5)
        
        ctk.CTkButton(action_frame, text="🧠 AI ile Çözüm Üret", 
                     command=self.ai_solution, width=150).pack(side="left", padx=5)
        
        ctk.CTkButton(action_frame, text="💾 Rapor Oluştur", 
                     command=self.generate_report, width=150).pack(side="left", padx=5)
        
        ctk.CTkButton(action_frame, text="🗑️ Tümünü Temizle", 
                     command=self.clear_all, width=150).pack(side="left", padx=5)
        
        # Hata ağacı tıklama olayı
        self.error_tree.bind("<ButtonRelease-1>", self.on_error_select)
        
    def initialize_ai(self):
        """AI entegrasyonunu başlat"""
        try:
            self.ai_integration = AIIntegration()
            self.ai_integration.load_models()
        except Exception as e:
            self.add_message("AI başlatma hatası: " + str(e))
    
    def scan_entire_project(self):
        """Tüm projeyi tarar"""
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.scan_folder(project_path)
    
    def scan_python_files(self):
        """Python dosyalarını tarar"""
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        python_files = glob.glob(os.path.join(project_path, "**/*.py"), recursive=True)
        self.scan_files(python_files)
    
    def scan_config_files(self):
        """Config dosyalarını tarar"""
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_files = glob.glob(os.path.join(project_path, "**/*.json"), recursive=True)
        config_files += glob.glob(os.path.join(project_path, "**/*.ini"), recursive=True)
        config_files += glob.glob(os.path.join(project_path, "**/*.cfg"), recursive=True)
        self.scan_files(config_files)
    
    def select_custom_folder(self):
        """Özel klasör seçer"""
        folder_path = filedialog.askdirectory(title="Taranacak Klasörü Seçin")
        if folder_path:
            self.scan_folder(folder_path)
    
    def scan_folder(self, folder_path):
        """Klasörü tarar"""
        all_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(('.py', '.json', '.ini', '.cfg', '.txt', '.md')):
                    all_files.append(os.path.join(root, file))
        self.scan_files(all_files)
    
    def scan_files(self, file_list):
        """Dosya listesini tarar"""
        self.clear_all()
        self.add_message(f"{len(file_list)} dosya taranıyor...")
        
        # Taramayı thread'de yap
        threading.Thread(target=self.perform_scan, args=(file_list,), daemon=True).start()
    
    def perform_scan(self, file_list):
        """Dosya tarama işlemini yapar"""
        errors_found = 0
        
        for file_path in file_list:
            try:
                errors = self.analyze_file(file_path)
                for error in errors:
                    self.add_error_to_tree(file_path, error)
                    errors_found += 1
            except Exception as e:
                self.add_error_to_tree(file_path, {
                    "line": 0,
                    "error": f"Tarama hatası: {str(e)}",
                    "severity": "Yüksek"
                })
                errors_found += 1
        
        self.add_message(f"Tarama tamamlandı. {errors_found} hata bulundu.")
    
    def analyze_file(self, file_path):
        """Dosyayı analiz eder ve hataları bulur"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Python dosyaları için syntax kontrolü
                if file_path.endswith('.py'):
                    errors.extend(self.check_python_syntax(file_path, content, lines))
                
                # JSON dosyaları için syntax kontrolü
                elif file_path.endswith('.json'):
                    errors.extend(self.check_json_syntax(file_path, content))
                
                # Genel hatalar
                errors.extend(self.check_general_errors(file_path, content, lines))
                
        except UnicodeDecodeError:
            # Binary dosyaları atla
            pass
        except Exception as e:
            errors.append({
                "line": 0,
                "error": f"Dosya okuma hatası: {str(e)}",
                "severity": "Yüksek"
            })
        
        return errors
    
    def check_python_syntax(self, file_path, content, lines):
        """Python syntax hatalarını kontrol eder"""
        errors = []
        
        try:
            # Basit syntax kontrolü
            compile(content, file_path, 'exec')
        except SyntaxError as e:
            errors.append({
                "line": e.lineno,
                "error": f"Syntax hatası: {e.msg}",
                "severity": "Yüksek"
            })
        
        # Import hataları
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                if '# noqa' not in line and '# pylint: disable' not in line:
                    # Basit import kontrolü
                    pass
        
        # TODO ve FIXME yorumları
        for i, line in enumerate(lines, 1):
            if any(marker in line for marker in ['# TODO', '# FIXME', '# BUG', '# HACK']):
                errors.append({
                    "line": i,
                    "error": f"Yorumda işaretlenmiş sorun: {line.strip()}",
                    "severity": "Orta"
                })
        
        return errors
    
    def check_json_syntax(self, file_path, content):
        """JSON syntax hatalarını kontrol eder"""
        errors = []
        
        try:
            import json
            json.loads(content)
        except json.JSONDecodeError as e:
            errors.append({
                "line": e.lineno,
                "error": f"JSON syntax hatası: {e.msg}",
                "severity": "Yüksek"
            })
        
        return errors
    
    def check_general_errors(self, file_path, content, lines):
        """Genel hataları kontrol eder"""
        errors = []
        
        # Boş dosya kontrolü
        if not content.strip():
            errors.append({
                "line": 0,
                "error": "Boş dosya",
                "severity": "Düşük"
            })
        
        # UTF-8 BOM kontrolü
        if content.startswith('\ufeff'):
            errors.append({
                "line": 1,
                "error": "UTF-8 BOM tespit edildi",
                "severity": "Orta"
            })
        
        # Satır sonu karakterleri
        for i, line in enumerate(lines, 1):
            if '\r' in line:
                errors.append({
                    "line": i,
                    "error": "CR (\\r) karakteri tespit edildi",
                    "severity": "Düşük"
                })
        
        return errors
    
    def add_error_to_tree(self, file_path, error_info):
        """Hata bilgisini ağaca ekler"""
        filename = os.path.basename(file_path)
        self.after(0, lambda: self.error_tree.insert("", "end", values=(
            filename,
            error_info.get("line", 0),
            error_info.get("error", "Bilinmeyen hata"),
            error_info.get("severity", "Orta")
        )))
    
    def on_error_select(self, event):
        """Hata seçildiğinde detayları gösterir"""
        selection = self.error_tree.selection()
        if selection:
            item = self.error_tree.item(selection[0])
            error_details = f"Dosya: {item['values'][0]}\n"
            error_details += f"Satır: {item['values'][1]}\n"
            error_details += f"Hata: {item['values'][2]}\n"
            error_details += f"Önem: {item['values'][3]}\n\n"
            
            self.detail_text.config(state="normal")
            self.detail_text.delete("1.0", "end")
            self.detail_text.insert("1.0", error_details)
            self.detail_text.config(state="disabled")
    
    def fix_selected_error(self):
        """Seçili hatayı onarır"""
        selection = self.error_tree.selection()
        if not selection:
            self.add_message("Lütfen onarılacak bir hata seçin.")
            return
        
        item = self.error_tree.item(selection[0])
        self.add_message(f"'{item['values'][2]}' hatası onarılıyor...")
    
    def ai_solution(self):
        """AI ile çözüm üretir"""
        selection = self.error_tree.selection()
        if not selection:
            self.add_message("Lütfen çözüm üretilecek bir hata seçin.")
            return
        
        if not self.ai_integration:
            self.add_message("AI sistemi hazır değil.")
            return
        
        item = self.error_tree.item(selection[0])
        error_info = f"Dosya: {item['values'][0]}, Satır: {item['values'][1]}, Hata: {item['values'][2]}"
        
        prompt = f"""
        Aşağıdaki Python hatasını analiz et ve çözüm öner:
        {error_info}
        
        Lütfen Türkçe olarak:
        1. Hatayı açıkla
        2. Olası nedenleri sırala  
        3. Adım adım çözüm öner
        4. Örnek kod göster
        """
        
        self.add_message("🤖 AI çözümü oluşturuluyor...")
        
        # AI yanıtını thread'de al
        threading.Thread(target=self.get_ai_solution, args=(prompt,), daemon=True).start()
    
    def get_ai_solution(self, prompt):
        """AI çözümünü alır"""
        try:
            solution = self.ai_integration.generate_response(prompt)
            self.after(0, lambda: self.show_ai_solution(solution))
        except Exception as e:
            self.after(0, lambda: self.add_message(f"AI hatası: {str(e)}"))
    
    def show_ai_solution(self, solution):
        """AI çözümünü gösterir"""
        self.detail_text.config(state="normal")
        self.detail_text.insert("end", "\n\n🤖 AI ÇÖZÜM ÖNERİSİ:\n")
        self.detail_text.insert("end", solution)
        self.detail_text.config(state="disabled")
        self.add_message("AI çözümü eklendi.")
    
    def generate_report(self):
        """Rapor oluşturur"""
        errors = []
        for item in self.error_tree.get_children():
            errors.append(self.error_tree.item(item)['values'])
        
        if not errors:
            self.add_message("Rapor oluşturulacak hata bulunamadı.")
            return
        
        report = "SystemMasterAI Hata Raporu\n"
        report += "========================\n\n"
        
        for error in errors:
            report += f"Dosya: {error[0]}\n"
            report += f"Satır: {error[1]}\n"
            report += f"Hata: {error[2]}\n"
            report += f"Önem: {error[3]}\n"
            report += "-" * 50 + "\n"
        
        # Raporu dosyaya kaydet
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"error_report_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.add_message(f"Rapor oluşturuldu: {report_file}")
        except Exception as e:
            self.add_message(f"Rapor oluşturma hatası: {str(e)}")
    
    def clear_all(self):
        """Tüm hataları temizler"""
        for item in self.error_tree.get_children():
            self.error_tree.delete(item)
        
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.config(state="disabled")
        
        self.add_message("Tüm hatalar temizlendi.")
    
    def add_message(self, message):
        """Mesaj ekler"""
        self.detail_text.config(state="normal")
        self.detail_text.insert("end", f"\n{message}")
        self.detail_text.config(state="disabled")
        self.detail_text.see("end")
