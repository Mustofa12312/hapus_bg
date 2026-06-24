"""
Configuration settings for PNG Background Remover
"""
import os
from pathlib import Path

# Application settings
APP_NAME = "PNG Background Remover"
APP_VERSION = "1.1"
LOG_DIR = Path(__file__).parent / "logs"

# Processing settings
MAX_IMAGE_SIZE_MB = 100  # Maximum file size in MB
MAX_CONCURRENT_OPERATIONS = 1  # Keep at 1 for memory efficiency
PROCESS_TIMEOUT_SECONDS = 300  # Timeout per image (5 minutes)
RETRY_ATTEMPTS = 2  # Number of retries for failed images
BATCH_SIZE_WARNING = 500  # Warn user if batch > this size

# Resource limits
MIN_FREE_DISK_SPACE_MB = 500  # Minimum free disk space required
MAX_RAM_USAGE_PERCENT = 80  # Maximum RAM usage percentage

# Output settings
OUTPUT_FORMAT = "PNG"  # Output image format
PRESERVE_DIR_STRUCTURE = True  # Keep folder structure in output
BACKUP_ORIGINALS = False  # Create backup of originals
OVERWRITE_EXISTING = False  # Overwrite if output already exists

# Supported image formats
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg'}

# Magic bytes for file validation
FILE_MAGIC_BYTES = {
    b'\x89PNG\r\n\x1a\n': 'png',
    b'\xff\xd8\xff': 'jpg',  # JPEG/JFIF
    b'GIF8': 'gif',  # GIF (not supported, but for detection)
    b'BM': 'bmp',  # BMP (not supported, but for detection)
}

# Create logs directory if it doesn't exist
LOG_DIR.mkdir(exist_ok=True)

# API Configuration
def get_removebg_api_key():
    api_file = Path(__file__).parent / "api_remove_bk.md"
    if api_file.exists():
        try:
            with open(api_file, 'r') as f:
                return f.read().strip()
        except Exception:
            pass
    return ""

REMOVEBG_API_KEY = get_removebg_api_key()
