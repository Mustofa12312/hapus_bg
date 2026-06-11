import customtkinter as ctk

class LogTextBox(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(state="disabled")
        
        # Tags for coloring log levels with modern colors
        self.tag_config("INFO", foreground="#00ff88", font=("Monaco", 10))
        self.tag_config("ERROR", foreground="#ff4444", font=("Monaco", 10, "bold"))
        self.tag_config("DEBUG", foreground="#88aaff", font=("Monaco", 9))

    def append_log(self, text: str):
        self.configure(state="normal")
        
        tag = None
        if "[INFO]" in text:
            tag = "INFO"
        elif "[ERROR]" in text:
            tag = "ERROR"
        elif "[DEBUG]" in text:
            tag = "DEBUG"
            
        self.insert("end", text + "\n", tag)
        self.see("end")
        self.configure(state="disabled")
    
    def clear_log(self):
        """Clear all log content."""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")
