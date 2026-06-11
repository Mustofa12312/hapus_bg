import customtkinter as ctk

class LogTextBox(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(state="disabled")
        
        # Tags for coloring log levels
        self.tag_config("INFO", foreground="lightgreen")
        self.tag_config("ERROR", foreground="red")
        self.tag_config("DEBUG", foreground="gray")

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
