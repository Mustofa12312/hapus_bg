import customtkinter as ctk
from datetime import datetime

class LogTextBox(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(state="disabled")
        
        # Tags for coloring log levels
        self.tag_config("INFO", foreground="#00ff88")      # Green
        self.tag_config("ERROR", foreground="#ff4444")     # Red
        self.tag_config("DEBUG", foreground="#88aaff")     # Blue
        self.tag_config("WARNING", foreground="#ffaa44")   # Orange
        self.tag_config("SUCCESS", foreground="#44dd88")   # Bright green
        
        self.max_lines = 1000  # Limit to prevent memory issues

    def append_log(self, text: str):
        """Append log message with automatic timestamp and color coding."""
        self.configure(state="normal")
        
        # Determine tag from log level markers
        tag = None
        if "[INFO]" in text:
            tag = "INFO"
        elif "[ERROR]" in text:
            tag = "ERROR"
        elif "[DEBUG]" in text:
            tag = "DEBUG"
        elif "[WARNING]" in text:
            tag = "WARNING"
        elif "[SUCCESS]" in text or "✅" in text:
            tag = "SUCCESS"
        
        # Add timestamp if not already present
        if not text.startswith("["):
            timestamp = datetime.now().strftime("%H:%M:%S")
            text = f"[{timestamp}] {text}"
        
        # Insert text with tag
        self.insert("end", text + "\n", tag)
        
        # Auto-scroll to end
        self.see("end")
        
        # Limit log size to prevent memory issues
        line_count = int(self.index("end-1c").split(".")[0])
        if line_count > self.max_lines:
            self.delete("1.0", "2.0")  # Delete first line
        
        self.configure(state="disabled")
    
    def clear_log(self):
        """Clear all log content."""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")
