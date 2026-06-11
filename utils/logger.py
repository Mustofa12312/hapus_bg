import logging
import sys

def setup_logger(log_callback=None):
    """
    Setup basic logging to output to console and optionally to a UI callback.
    """
    logger = logging.getLogger("BGRemover")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(levelname)s] %(message)s")

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Custom UI handler
    if log_callback:
        class UICallbackHandler(logging.Handler):
            def emit(self, record):
                log_entry = self.format(record)
                log_callback(log_entry)
        
        ui_handler = UICallbackHandler()
        ui_handler.setLevel(logging.INFO)
        ui_handler.setFormatter(formatter)
        logger.addHandler(ui_handler)

    return logger

logger = setup_logger()

def set_ui_callback(callback):
    global logger
    logger = setup_logger(callback)
