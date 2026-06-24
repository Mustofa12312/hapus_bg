import os
import shutil
from pathlib import Path
from utils.logger import logger
from config import MIN_FREE_DISK_SPACE_MB

def validate_input_folder(folder_path: str) -> tuple[bool, str]:
    """
    Validate if the input folder is accessible and valid.
    Returns (is_valid: bool, message: str)
    """
    try:
        path = Path(folder_path)
        
        # Check if path exists
        if not path.exists():
            return False, f"Folder tidak ditemukan: {folder_path}"
        
        # Check if it's a directory
        if not path.is_dir():
            return False, f"Path bukan folder: {folder_path}"
        
        # Check if it's a symlink (potential security risk)
        if path.is_symlink():
            logger.warning(f"Input folder is a symlink: {folder_path}")
        
        # Check read permission
        if not os.access(folder_path, os.R_OK):
            return False, f"Tidak memiliki izin baca untuk folder: {folder_path}"
        
        return True, "OK"
    
    except Exception as e:
        return False, f"Error validating folder: {e}"

def validate_output_folder(folder_path: str) -> tuple[bool, str]:
    """
    Validate if the output folder path is writable and has enough disk space.
    Returns (is_valid: bool, message: str)
    """
    try:
        path = Path(folder_path)
        parent = path.parent
        
        # Check if parent exists
        if not parent.exists():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Tidak bisa membuat folder output: {e}"
        
        # Check write permission on parent
        if not os.access(parent, os.W_OK):
            return False, f"Tidak memiliki izin tulis untuk folder: {parent}"
        
        # Check disk space
        try:
            stat = shutil.disk_usage(parent)
            free_mb = stat.free / (1024 * 1024)
            if free_mb < MIN_FREE_DISK_SPACE_MB:
                return False, f"Ruang disk tidak cukup. Diperlukan {MIN_FREE_DISK_SPACE_MB}MB, tersedia {free_mb:.1f}MB"
        except Exception as e:
            logger.warning(f"Could not check disk space: {e}")
        
        return True, "OK"
    
    except Exception as e:
        return False, f"Error validating output folder: {e}"

def get_output_folder(input_folder: str) -> str:
    """
    Returns the corresponding output folder next to the input folder.
    E.g., if input is /path/to/my_images, output is /path/to/my_images_output
    """
    input_path = Path(input_folder)
    output_path = input_path.parent / f"{input_path.name}_output"
    return str(output_path)

def recreate_dir_structure(input_folder: str, output_folder: str, file_path: str) -> str:
    """
    Calculates the output path for a specific file, ensuring the directory exists.
    Implements basic path traversal protection.
    """
    try:
        # Get absolute paths to prevent path traversal
        input_abs = Path(input_folder).resolve()
        file_abs = Path(file_path).resolve()
        output_abs = Path(output_folder).resolve()
        
        # Check if file is within input folder (prevent traversal attacks)
        try:
            file_abs.relative_to(input_abs)
        except ValueError:
            logger.error(f"File path traversal detected: {file_path}")
            raise ValueError(f"File is not within input folder: {file_path}")
        
        # Calculate relative path and output path
        rel_path = file_abs.relative_to(input_abs)
        out_file_path = output_abs / rel_path
        out_dir = out_file_path.parent
        
        # Create directories
        out_dir.mkdir(parents=True, exist_ok=True)
        
        return str(out_file_path)
    
    except Exception as e:
        logger.error(f"Error recreating directory structure: {e}")
        raise

def sanitize_filename(filename: str) -> str:
    """
    Remove invalid characters from filename while preserving extension.
    """
    # Characters that are invalid in filenames on most systems
    invalid_chars = r'<>:"/\|?*'
    
    name_part = Path(filename).stem
    ext_part = Path(filename).suffix
    
    # Remove invalid characters
    for char in invalid_chars:
        name_part = name_part.replace(char, '_')
    
    # Remove control characters
    name_part = ''.join(char for char in name_part if ord(char) >= 32)
    
    return name_part + ext_part

def get_available_disk_space(path: str) -> float:
    """
    Get available disk space in MB for the given path.
    """
    try:
        stat = shutil.disk_usage(path)
        return stat.free / (1024 * 1024)  # Convert to MB
    except Exception as e:
        logger.warning(f"Could not get disk space info: {e}")
        return 0.0
