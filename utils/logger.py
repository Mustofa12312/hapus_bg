import logging
import sys
from pathlib import Path
from datetime import datetime
from config import LOG_DIR

def setup_logger(log_callback=None):
    """
    Setup comprehensive logging to console, file, and optionally to a UI callback.
    """
    logger = logging.getLogger("BGRemover")
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    # Create formatters for different handlers
    detailed_formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    simple_formatter = logging.Formatter("[%(levelname)s] %(message)s")

    # Console handler - simple format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler - detailed format with timestamp
    try:
        log_filename = LOG_DIR / f"bg_remover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"[WARNING] Could not create log file: {e}")

    # Error log file handler - only errors and warnings
    try:
        error_log_filename = LOG_DIR / f"errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        error_file_handler = logging.FileHandler(error_log_filename, encoding='utf-8')
        error_file_handler.setLevel(logging.WARNING)
        error_file_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_file_handler)
    except Exception as e:
        print(f"[WARNING] Could not create error log file: {e}")

    # Custom UI handler
    if log_callback:
        class UICallbackHandler(logging.Handler):
            def emit(self, record):
                log_entry = self.format(record)
                try:
                    log_callback(log_entry)
                except Exception as e:
                    print(f"[ERROR] Failed to send log to UI: {e}")
        
        ui_handler = UICallbackHandler()
        ui_handler.setLevel(logging.INFO)
        ui_handler.setFormatter(simple_formatter)
        logger.addHandler(ui_handler)

    return logger

logger = setup_logger()

def set_ui_callback(callback):
    """Update logger with UI callback."""
    global logger
    logger = setup_logger(callback)

def get_logger():
    """Get the current logger instance."""
    return logger

def get_log_directory():
    """Return path to logs directory."""
    return LOG_DIR
