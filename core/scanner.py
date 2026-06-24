import os
from pathlib import Path
from PIL import Image
from utils.logger import logger
from config import SUPPORTED_FORMATS, MAX_IMAGE_SIZE_MB, FILE_MAGIC_BYTES

def validate_image_file(file_path: str) -> tuple[bool, str]:
    """
    Validate if a file is a valid image based on magic bytes and PIL check.
    Returns (is_valid: bool, reason_if_invalid: str)
    """
    try:
        # Check file extension
        ext = Path(file_path).suffix.lower()
        if ext not in SUPPORTED_FORMATS:
            return False, f"Format tidak didukung: {ext}"
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > MAX_IMAGE_SIZE_MB:
            return False, f"File terlalu besar: {file_size_mb:.1f}MB > {MAX_IMAGE_SIZE_MB}MB"
        
        # Check magic bytes (file signature)
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if not header:
                    return False, "File kosong"
                
                # Validate magic bytes
                is_valid_magic = False
                for magic_bytes, format_type in FILE_MAGIC_BYTES.items():
                    if header.startswith(magic_bytes):
                        if format_type not in ['png', 'jpg']:
                            return False, f"Format magic bytes tidak didukung: {format_type}"
                        is_valid_magic = True
                        break
                
                if not is_valid_magic:
                    return False, "Format file tidak dikenali (magic bytes tidak cocok)"
        
        except IOError as e:
            return False, f"Error membaca file: {e}"
        
        # Validate with PIL
        try:
            with Image.open(file_path) as img:
                # Check image format
                if img.format and img.format.lower() not in ['png', 'jpeg', 'jpg']:
                    return False, f"Format PIL tidak didukung: {img.format}"
                # Try to verify image integrity
                img.verify()
        except Exception as e:
            return False, f"File bukan gambar yang valid: {e}"
        
        return True, ""
    
    except Exception as e:
        return False, f"Error validasi file: {e}"

def scan_for_images(folder_path: str, validate: bool = True) -> list[str]:
    """
    Scans the given folder and its subfolders for image files (.png, .jpg, .jpeg).
    Returns a list of absolute paths to the found files.
    Optionally validates each file.
    """
    image_files = []
    invalid_files = []
    
    logger.info(f"Scanning folder: {folder_path}")
    
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        logger.error(f"Invalid folder: {folder_path}")
        return image_files

    try:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(SUPPORTED_FORMATS):
                    file_path = os.path.join(root, file)
                    
                    if validate:
                        is_valid, reason = validate_image_file(file_path)
                        if is_valid:
                            image_files.append(file_path)
                        else:
                            invalid_files.append((file_path, reason))
                            logger.debug(f"Invalid image skipped: {file_path} - {reason}")
                    else:
                        image_files.append(file_path)
        
        logger.info(f"Found {len(image_files)} valid image files.")
        
        if invalid_files:
            logger.warning(f"Skipped {len(invalid_files)} invalid files.")
            for file_path, reason in invalid_files[:5]:  # Log first 5
                logger.debug(f"  - {file_path}: {reason}")
        
        return image_files
    
    except Exception as e:
        logger.error(f"Error during folder scan: {e}")
        return image_files
