import os
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES

from ui.widgets import LogTextBox
from core.processor import BatchProcessor
from core.scanner import scan_for_images
from utils.logger import set_ui_callback
from utils.paths import get_output_folder

# Wrapper to enable drag and drop in CustomTkinter
class TkDnDWrapper(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class App(TkDnDWrapper):
    def __init__(self):
        super().__init__()
        
        self.title("PNG Background Remover")
        self.geometry("1000x650")
        ctk.set_appearance_mode("dark")
        
        self.selected_folder = None
        self.processor = BatchProcessor(self.update_progress, self.on_process_complete)
        
        self.setup_ui()
        
        # Route logger output to UI
        def log_to_ui(msg):
            # Must run in main thread
            self.after(0, self.log_box.append_log, msg)
        set_ui_callback(log_to_ui)
        
    def setup_ui(self):
        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # Log box takes remaining space
        
        # 1. Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        ctk.CTkLabel(header_frame, text="PNG Background Remover", font=ctk.CTkFont(size=24, weight="bold")).pack()
        ctk.CTkLabel(header_frame, text="AI Offline Batch Processor", font=ctk.CTkFont(size=14)).pack()
        
        # File count label
        self.file_count_label = ctk.CTkLabel(header_frame, text="", text_color="orange", font=ctk.CTkFont(size=12))
        self.file_count_label.pack()
        
        # 2. Folder Section
        folder_frame = ctk.CTkFrame(self)
        folder_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        folder_frame.grid_columnconfigure(0, weight=1)
        
        self.dnd_label = ctk.CTkLabel(folder_frame, text="Drag Folder Here\nor", height=80, fg_color="#333333", corner_radius=8)
        self.dnd_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Enable DND on the label
        self.dnd_label.drop_target_register(DND_FILES)
        self.dnd_label.dnd_bind('<<Drop>>', self.on_drop)
        
        btn_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(0, 20))
        self.select_btn = ctk.CTkButton(btn_frame, text="Pilih Folder", command=self.select_folder)
        self.select_btn.pack(side="left", padx=10)
        
        self.folder_path_label = ctk.CTkLabel(folder_frame, text="Belum ada folder yang dipilih", text_color="gray")
        self.folder_path_label.grid(row=2, column=0, pady=(0, 10))
        
        # 3. Process Section
        process_frame = ctk.CTkFrame(self, fg_color="transparent")
        process_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        process_frame.grid_columnconfigure(2, weight=1)
        
        self.start_btn = ctk.CTkButton(process_frame, text="Mulai Proses", command=self.start_process, state="disabled")
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.cancel_btn = ctk.CTkButton(process_frame, text="Berhenti", command=self.cancel_process, state="disabled", fg_color="#cc3333")
        self.cancel_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.progress_bar = ctk.CTkProgressBar(process_frame)
        self.progress_bar.grid(row=0, column=2, sticky="ew", padx=(0, 10))
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(process_frame, text="0%")
        self.progress_label.grid(row=0, column=3)
        
        # 4. Log Section
        self.log_box = LogTextBox(self, height=200)
        self.log_box.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        
        # 5. Footer
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        self.clear_log_btn = ctk.CTkButton(footer_frame, text="Hapus Log", command=self.clear_logs, width=100)
        self.clear_log_btn.pack(side="left", padx=(0, 10))
        
        self.open_folder_btn = ctk.CTkButton(footer_frame, text="Buka Folder Hasil", command=self.open_output_folder, state="disabled")
        self.open_folder_btn.pack(side="right")

    def on_drop(self, event):
        # tkinterdnd2 wraps paths in curly braces if they contain spaces
        path = event.data
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
            
        if os.path.isdir(path):
            self.set_folder(path)
        else:
            self.log_box.append_log("[ERROR] Yang didrop bukan folder!")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.set_folder(folder)
            
    def set_folder(self, path):
        self.selected_folder = path
        self.folder_path_label.configure(text=path, text_color="white")
        self.start_btn.configure(state="normal")
        self.log_box.append_log(f"[INFO] Folder dipilih: {path}")
        
        # Preview file count
        try:
            image_files = scan_for_images(path)
            file_count = len(image_files)
            if file_count > 0:
                self.file_count_label.configure(text=f"📁 Ditemukan {file_count} gambar (siap diproses)")
            else:
                self.file_count_label.configure(text="⚠️  Tidak ada gambar dalam folder")
                self.start_btn.configure(state="disabled")
        except Exception as e:
            self.log_box.append_log(f"[ERROR] Gagal menghitung file: {e}")
        
    def start_process(self):
        if not self.selected_folder:
            return
            
        self.start_btn.configure(state="disabled")
        self.select_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.open_folder_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        
        self.processor.start(self.selected_folder)
    
    def cancel_process(self):
        """Cancel the ongoing process."""
        self.processor.stop()
        self.cancel_btn.configure(state="disabled")
        
    def update_progress(self, val):
        # Must run in main thread
        self.after(0, self._update_progress_ui, val)
        
    def _update_progress_ui(self, val):
        self.progress_bar.set(val)
        percent = int(val * 100)
        self.progress_label.configure(text=f"{percent}%")
        
    def on_process_complete(self):
        # Must run in main thread
        self.after(0, self._on_process_complete_ui)
        
    def _on_process_complete_ui(self):
        self.start_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.open_folder_btn.configure(state="normal")
        
        # Show summary
        stats = self.processor.stats
        total = stats["success"] + stats["failed"]
        self.log_box.append_log("\n" + "="*50)
        self.log_box.append_log(f"[INFO] ✅ RINGKASAN PROSES")
        self.log_box.append_log(f"[INFO] Total: {total} | Sukses: {stats['success']} | Gagal: {stats['failed']}")
        if stats["success"] == total:
            self.log_box.append_log("[INFO] 🎉 Semua gambar berhasil diproses!")
        elif stats["success"] > 0:
            self.log_box.append_log(f"[INFO] ⚠️  {stats['failed']} gambar gagal diproses")
        self.log_box.append_log("="*50 + "\n")
    
    def clear_logs(self):
        """Clear log content."""
        self.log_box.clear_log()
        
    def open_output_folder(self):
        if self.selected_folder:
            out_folder = get_output_folder(self.selected_folder)
            if os.path.exists(out_folder):
                try:
                    # Linux only as per PRD
                    subprocess.Popen(['xdg-open', out_folder])
                except Exception as e:
                    self.log_box.append_log(f"[ERROR] Gagal membuka folder: {e}")
            else:
                self.log_box.append_log("[ERROR] Folder output belum ada!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
