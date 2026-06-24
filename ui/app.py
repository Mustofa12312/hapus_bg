import os
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES

from ui.widgets import LogTextBox
from core.processor import BatchProcessor
from core.scanner import scan_for_images
from utils.logger import set_ui_callback, get_log_directory
from utils.paths import get_output_folder, validate_input_folder

# Wrapper to enable drag and drop in CustomTkinter
class TkDnDWrapper(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class App(TkDnDWrapper):
    def __init__(self):
        super().__init__()
        
        self.title("PNG Background Remover v1.1")
        self.geometry("1100x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.selected_folder = None
        self.processor = BatchProcessor(self.update_progress, self.on_process_complete)
        
        # Set main background color
        self.configure(fg_color="#0f0f0f")
        
        self.setup_ui()
        
        # Route logger output to UI
        def log_to_ui(msg):
            # Must run in main thread
            self.after(0, self.log_box.append_log, msg)
        set_ui_callback(log_to_ui)
        
        # Center window on screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Log box takes remaining space
        
        # 1. Header with gradient-like effect
        header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=12)
        header_frame.grid(row=0, column=0, padx=15, pady=(15, 8), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🖼️  PNG Background Remover", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#00d4ff"
        )
        title_label.pack(pady=(12, 4), padx=20)
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="✨ AI Offline Batch Processor | Hapus background ratusan gambar sekaligus",
            font=ctk.CTkFont(size=12),
            text_color="#a0a0a0"
        )
        subtitle_label.pack(pady=(0, 4), padx=20)
        
        # File count label with better styling
        self.file_count_label = ctk.CTkLabel(
            header_frame, 
            text="", 
            text_color="#00ff88", 
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.file_count_label.pack(pady=(0, 12), padx=20)
        
        # 2. Folder Selection Section
        folder_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=12)
        folder_frame.grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        folder_frame.grid_columnconfigure(0, weight=1)
        
        folder_label = ctk.CTkLabel(
            folder_frame,
            text="📂 Pilih Folder Sumber",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00d4ff"
        )
        folder_label.pack(pady=(12, 8), padx=20, anchor="w")
        
        self.dnd_label = ctk.CTkLabel(
            folder_frame, 
            text="🎯 Drag & Drop Folder di Sini\nATAU", 
            height=70, 
            fg_color="#0f3460", 
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.dnd_label.pack(padx=20, pady=8, fill="x", expand=False)
        
        # Enable DND on the label
        self.dnd_label.drop_target_register(DND_FILES)
        self.dnd_label.dnd_bind('<<Drop>>', self.on_drop)
        
        btn_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        btn_frame.pack(padx=20, pady=8, anchor="center")
        
        self.select_btn = ctk.CTkButton(
            btn_frame, 
            text="📁 Pilih Folder", 
            command=self.select_folder,
            fg_color="#0084d4",
            hover_color="#0066b3",
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=180,
            height=36
        )
        self.select_btn.pack(side="left", padx=8)
        
        self.folder_path_label = ctk.CTkLabel(
            folder_frame, 
            text="📍 Belum ada folder yang dipilih", 
            text_color="#666666",
            font=ctk.CTkFont(size=10)
        )
        self.folder_path_label.pack(pady=(0, 12), padx=20, anchor="w")
        
        # 3. Process Controls Section
        control_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=12)
        control_frame.grid(row=2, column=0, padx=15, pady=8, sticky="ew")
        control_frame.grid_columnconfigure(2, weight=1)
        
        process_label = ctk.CTkLabel(
            control_frame,
            text="⚙️  Kontrol Proses",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00d4ff"
        )
        process_label.grid(row=0, column=0, columnspan=4, pady=(10, 8), padx=20, sticky="w")
        
        self.start_btn = ctk.CTkButton(
            control_frame, 
            text="▶️  Mulai Proses", 
            command=self.start_process, 
            state="disabled",
            fg_color="#00aa44",
            hover_color="#008833",
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            height=34
        )
        self.start_btn.grid(row=1, column=0, padx=(20, 8), pady=(0, 12))
        
        self.cancel_btn = ctk.CTkButton(
            control_frame, 
            text="⏹️  Berhenti", 
            command=self.cancel_process, 
            state="disabled", 
            fg_color="#d41f1f",
            hover_color="#b31818",
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            height=34
        )
        self.cancel_btn.grid(row=1, column=1, padx=8, pady=(0, 12))
        
        # Progress section
        self.progress_bar = ctk.CTkProgressBar(control_frame, height=24)
        self.progress_bar.grid(row=1, column=2, sticky="ew", padx=8, pady=(0, 12))
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            control_frame, 
            text="0%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00ff88",
            width=50
        )
        self.progress_label.grid(row=1, column=3, padx=(8, 20), pady=(0, 12))
        
        # 4. Log Section
        log_label = ctk.CTkLabel(
            self,
            text="📋 Activity Log",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00d4ff"
        )
        log_label.grid(row=3, column=0, padx=20, pady=(8, 2), sticky="w")
        
        self.log_box = LogTextBox(self, height=180, fg_color="#0f1419", border_color="#1a3a4d", border_width=2)
        self.log_box.grid(row=4, column=0, padx=15, pady=(0, 8), sticky="nsew")
        
        # 5. Footer with action buttons
        footer_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=12)
        footer_frame.grid(row=5, column=0, padx=15, pady=(8, 15), sticky="ew")
        footer_frame.grid_columnconfigure(1, weight=1)
        
        self.clear_log_btn = ctk.CTkButton(
            footer_frame, 
            text="🗑️  Clear Log", 
            command=self.clear_logs, 
            width=100,
            fg_color="#666666",
            hover_color="#777777",
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.clear_log_btn.pack(side="left", padx=(15, 8), pady=10)
        
        self.open_logs_btn = ctk.CTkButton(
            footer_frame,
            text="📝 Open Logs",
            command=self.open_logs,
            fg_color="#555555",
            hover_color="#666666",
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.open_logs_btn.pack(side="left", padx=8, pady=10)
        
        self.open_folder_btn = ctk.CTkButton(
            footer_frame, 
            text="📂 Buka Folder Hasil", 
            command=self.open_output_folder, 
            state="disabled",
            fg_color="#0084d4",
            hover_color="#0066b3",
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.open_folder_btn.pack(side="right", padx=(8, 15), pady=10)

    def on_drop(self, event):
        """Handle drag and drop folder event."""
        # tkinterdnd2 wraps paths in curly braces if they contain spaces
        path = event.data
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
        
        # Handle multiple file paths (if any)
        if '{' in path or '}' in path:
            self.log_box.append_log("[ERROR] Hanya satu folder yang dapat didrop")
            return
            
        if os.path.isdir(path):
            self.set_folder(path)
        else:
            self.log_box.append_log("[ERROR] Yang didrop bukan folder!")

    def select_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory()
        if folder:
            self.set_folder(folder)
            
    def set_folder(self, path):
        """Set selected folder with validation."""
        # Validate input folder
        is_valid, msg = validate_input_folder(path)
        if not is_valid:
            self.log_box.append_log(f"[ERROR] {msg}")
            self.file_count_label.configure(text="❌ Folder tidak valid", text_color="#ff4444")
            self.start_btn.configure(state="disabled")
            return
        
        self.selected_folder = path
        self.folder_path_label.configure(text=f"✅ {path}", text_color="#00ff88")
        self.log_box.append_log(f"[INFO] Folder dipilih: {path}")
        
        # Preview file count
        try:
            image_files = scan_for_images(path, validate=True)
            file_count = len(image_files)
            if file_count > 0:
                self.file_count_label.configure(
                    text=f"📁 Ditemukan {file_count} gambar (siap diproses)",
                    text_color="#00ff88"
                )
                self.start_btn.configure(state="normal")
                self.log_box.append_log(f"[SUCCESS] {file_count} gambar ditemukan")
            else:
                self.file_count_label.configure(
                    text="⚠️  Tidak ada gambar valid dalam folder",
                    text_color="#ffaa44"
                )
                self.start_btn.configure(state="disabled")
                self.log_box.append_log("[WARNING] Tidak ada gambar ditemukan dalam folder ini")
        except Exception as e:
            self.log_box.append_log(f"[ERROR] Gagal memindai folder: {e}")
            self.start_btn.configure(state="disabled")
        
    def start_process(self):
        """Start the batch processing."""
        if not self.selected_folder:
            self.log_box.append_log("[ERROR] Pilih folder terlebih dahulu!")
            return
            
        self.start_btn.configure(state="disabled")
        self.select_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.open_folder_btn.configure(state="disabled")
        self.clear_log_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        
        self.log_box.append_log("[INFO] Memulai proses... (lihat log file untuk detail)")
        self.processor.start(self.selected_folder)
    
    def cancel_process(self):
        """Cancel the ongoing process."""
        self.processor.stop()
        self.cancel_btn.configure(state="disabled")
        
    def update_progress(self, val):
        """Update progress bar from worker thread."""
        # Must run in main thread
        self.after(0, self._update_progress_ui, val)
        
    def _update_progress_ui(self, val):
        """Update progress UI in main thread."""
        self.progress_bar.set(val)
        percent = int(val * 100)
        self.progress_label.configure(text=f"{percent}%")
        
    def on_process_complete(self):
        """Handle process completion signal from worker thread."""
        # Must run in main thread
        self.after(0, self._on_process_complete_ui)
        
    def _on_process_complete_ui(self):
        """Update UI when process completes."""
        self.start_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.open_folder_btn.configure(state="normal")
        self.clear_log_btn.configure(state="normal")
        
        # Show summary with improved styling
        stats = self.processor.stats
        success = stats["success"]
        failed = stats["failed"]
        total = success + failed
        
        self.log_box.append_log("\n" + "━"*60)
        self.log_box.append_log("[INFO] ✅ RINGKASAN PROSES SELESAI")
        self.log_box.append_log(f"[INFO] 📊 Total: {total} | ✅ Sukses: {success} | ❌ Gagal: {failed}")
        
        if success == total and total > 0:
            self.log_box.append_log("[SUCCESS] 🎉 Sempurna! Semua gambar berhasil diproses!")
        elif success > 0:
            percentage = int((success / total) * 100)
            self.log_box.append_log(f"[WARNING] ⚠️  {percentage}% Berhasil | {failed} gambar gagal")
        else:
            self.log_box.append_log("[ERROR] ❌ Semua gambar gagal diproses")
        
        self.log_box.append_log("━"*60 + "\n")
    
    def clear_logs(self):
        """Clear log content."""
        self.log_box.clear_log()
    
    def open_logs(self):
        """Open logs directory."""
        log_dir = get_log_directory()
        try:
            subprocess.Popen(['xdg-open', str(log_dir)])
            self.log_box.append_log(f"[INFO] Membuka folder logs: {log_dir}")
        except Exception as e:
            self.log_box.append_log(f"[ERROR] Gagal membuka folder logs: {e}")
        
    def open_output_folder(self):
        """Open the output folder."""
        if self.selected_folder:
            out_folder = get_output_folder(self.selected_folder)
            if os.path.exists(out_folder):
                try:
                    # Linux only as per PRD
                    subprocess.Popen(['xdg-open', out_folder])
                    self.log_box.append_log(f"[INFO] Membuka folder hasil: {out_folder}")
                except Exception as e:
                    self.log_box.append_log(f"[ERROR] Gagal membuka folder hasil: {e}")
            else:
                self.log_box.append_log("[WARNING] Folder output belum ada. Proses lebih dulu!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Log box takes remaining space
        
        # 1. Header with gradient-like effect
        header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=12)
        header_frame.grid(row=0, column=0, padx=15, pady=(15, 8), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🖼️  PNG Background Remover", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#00d4ff"
        )
        title_label.pack(pady=(12, 4), padx=20)
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="✨ AI Offline Batch Processor | Hapus background ratusan gambar sekaligus",
            font=ctk.CTkFont(size=12),
            text_color="#a0a0a0"
        )
        subtitle_label.pack(pady=(0, 4), padx=20)
        
        # File count label with better styling
        self.file_count_label = ctk.CTkLabel(
            header_frame, 
            text="", 
            text_color="#00ff88", 
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.file_count_label.pack(pady=(0, 12), padx=20)
        
        # 2. Folder Selection Section
        folder_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=12)
        folder_frame.grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        folder_frame.grid_columnconfigure(0, weight=1)
        
        folder_label = ctk.CTkLabel(
            folder_frame,
            text="📂 Pilih Folder Sumber",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00d4ff"
        )
        folder_label.pack(pady=(12, 8), padx=20, anchor="w")
        
        self.dnd_label = ctk.CTkLabel(
            folder_frame, 
            text="🎯 Drag & Drop Folder di Sini\nATAU", 
            height=70, 
            fg_color="#0f3460", 
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.dnd_label.pack(padx=20, pady=8, fill="x", expand=False)
        
        # Enable DND on the label
        self.dnd_label.drop_target_register(DND_FILES)
        self.dnd_label.dnd_bind('<<Drop>>', self.on_drop)
        
        btn_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        btn_frame.pack(padx=20, pady=8, anchor="center")
        
        self.select_btn = ctk.CTkButton(
            btn_frame, 
            text="📁 Pilih Folder", 
            command=self.select_folder,
            fg_color="#0084d4",
            hover_color="#0066b3",
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=180,
            height=36
        )
        self.select_btn.pack(side="left", padx=8)
        
        self.folder_path_label = ctk.CTkLabel(
            folder_frame, 
            text="📍 Belum ada folder yang dipilih", 
            text_color="#666666",
            font=ctk.CTkFont(size=10)
        )
        self.folder_path_label.pack(pady=(0, 12), padx=20, anchor="w")
        
        # 3. Process Controls Section
        control_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=12)
        control_frame.grid(row=2, column=0, padx=15, pady=8, sticky="ew")
        control_frame.grid_columnconfigure(2, weight=1)
        
        process_label = ctk.CTkLabel(
            control_frame,
            text="⚙️  Kontrol Proses",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00d4ff"
        )
        process_label.grid(row=0, column=0, columnspan=4, pady=(10, 8), padx=20, sticky="w")
        
        self.start_btn = ctk.CTkButton(
            control_frame, 
            text="▶️  Mulai Proses", 
            command=self.start_process, 
            state="disabled",
            fg_color="#00aa44",
            hover_color="#008833",
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            height=34
        )
        self.start_btn.grid(row=1, column=0, padx=(20, 8), pady=(0, 12))
        
        self.cancel_btn = ctk.CTkButton(
            control_frame, 
            text="⏹️  Berhenti", 
            command=self.cancel_process, 
            state="disabled", 
            fg_color="#d41f1f",
            hover_color="#b31818",
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            height=34
        )
        self.cancel_btn.grid(row=1, column=1, padx=8, pady=(0, 12))
        
        # Progress section
        self.progress_bar = ctk.CTkProgressBar(control_frame, height=24)
        self.progress_bar.grid(row=1, column=2, sticky="ew", padx=8, pady=(0, 12))
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            control_frame, 
            text="0%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00ff88",
            width=50
        )
        self.progress_label.grid(row=1, column=3, padx=(8, 20), pady=(0, 12))
        
        # 4. Log Section
        log_label = ctk.CTkLabel(
            self,
            text="📋 Activity Log",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00d4ff"
        )
        log_label.grid(row=3, column=0, padx=20, pady=(8, 2), sticky="w")
        
        self.log_box = LogTextBox(self, height=180, fg_color="#0f1419", border_color="#1a3a4d", border_width=2)
        self.log_box.grid(row=4, column=0, padx=15, pady=(0, 8), sticky="nsew")
        
        # 5. Footer with action buttons
        footer_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=12)
        footer_frame.grid(row=5, column=0, padx=15, pady=(8, 15), sticky="ew")
        footer_frame.grid_columnconfigure(1, weight=1)
        
        self.clear_log_btn = ctk.CTkButton(
            footer_frame, 
            text="🗑️  Clear Log", 
            command=self.clear_logs, 
            width=100,
            fg_color="#666666",
            hover_color="#777777",
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.clear_log_btn.pack(side="left", padx=(15, 8), pady=10)
        
        self.open_folder_btn = ctk.CTkButton(
            footer_frame, 
            text="📂 Buka Folder Hasil", 
            command=self.open_output_folder, 
            state="disabled",
            fg_color="#0084d4",
            hover_color="#0066b3",
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.open_folder_btn.pack(side="right", padx=(8, 15), pady=10)

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
        self.folder_path_label.configure(text=f"✅ {path}", text_color="#00ff88")
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
        
        # Show summary with improved styling
        stats = self.processor.stats
        total = stats["success"] + stats["failed"]
        self.log_box.append_log("\n" + "━"*60)
        self.log_box.append_log(f"[INFO] ✅ RINGKASAN PROSES SELESAI")
        self.log_box.append_log(f"[INFO] 📊 Total: {total} | ✅ Sukses: {stats['success']} | ❌ Gagal: {stats['failed']}")
        if stats["success"] == total:
            self.log_box.append_log("[INFO] 🎉 Sempurna! Semua gambar berhasil diproses!")
        elif stats["success"] > 0:
            percentage = int((stats["success"] / total) * 100)
            self.log_box.append_log(f"[INFO] ⚠️  {percentage}% Berhasil | {stats['failed']} gambar gagal diproses")
        self.log_box.append_log("━"*60 + "\n")
    
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
