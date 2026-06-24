import os
import time
from rembg import remove
from PIL import Image
from utils.logger import logger
from config import PROCESS_TIMEOUT_SECONDS

class RemovalError(Exception):
    """Base class for removal errors"""
    pass

class CorruptedImageError(RemovalError):
    """Image file is corrupted or invalid"""
    pass

class ProcessingTimeoutError(RemovalError):
    """Image processing took too long"""
    pass

class OutputWriteError(RemovalError):
    """Failed to write output image"""
    pass

def remove_background(input_path: str, output_path: str) -> tuple[bool, str]:
    """
    Removes the background from the image at input_path and saves it to output_path.
    Returns (success: bool, error_message: str)
    """
    try:
        start_time = time.time()
        
        # Validate input file exists
        if not os.path.exists(input_path):
            error_msg = "File input tidak ditemukan"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg
        
        # Check file size before loading
        file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        logger.debug(f"Processing file: {input_path} ({file_size_mb:.1f}MB)")
        
        # Load input image
        try:
            input_image = Image.open(input_path)
            input_image.load()  # Force load to detect corruption early
        except IOError as e:
            error_msg = f"Tidak bisa membaca file: {e}"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"File gambar rusak atau tidak valid: {e}"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg
        
        # Validate image format
        if input_image.format and input_image.format.upper() not in ['PNG', 'JPEG', 'JPG']:
            error_msg = f"Format gambar tidak didukung: {input_image.format}"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg
        
        # Convert RGBA image to RGB for rembg if needed
        if input_image.mode not in ('RGB', 'RGBA'):
            try:
                input_image = input_image.convert('RGB')
                logger.debug(f"Converted image mode from {input_image.mode} to RGB")
            except Exception as e:
                error_msg = f"Tidak bisa mengkonversi mode gambar: {e}"
                logger.error(f"Failed to process {input_path}: {error_msg}")
                return False, error_msg
        
        # Remove background with timeout check
        try:
            # Menggunakan alpha matting dan post process mask untuk hasil yang lebih halus
            output_image = remove(
                input_image,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10,
                post_process_mask=True
            )
            elapsed = time.time() - start_time
            if elapsed > PROCESS_TIMEOUT_SECONDS:
                error_msg = f"Processing timeout ({elapsed:.1f}s > {PROCESS_TIMEOUT_SECONDS}s)"
                logger.error(f"Failed to process {input_path}: {error_msg}")
                return False, error_msg
            logger.debug(f"Background removed in {elapsed:.2f}s")
        except MemoryError as e:
            error_msg = "Memori tidak cukup untuk memproses gambar"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Error removing background: {e}"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg
        
        # Ensure output directory exists
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            error_msg = f"Tidak bisa membuat folder output: {e}"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg
        
        # Check if output file already exists and handle it
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.debug(f"Removed existing output file: {output_path}")
            except Exception as e:
                error_msg = f"Tidak bisa menghapus file output yang sudah ada: {e}"
                logger.error(f"Failed to process {input_path}: {error_msg}")
                return False, error_msg
        
        # Save output image with error handling
        try:
            output_image.save(output_path, format='PNG')
            elapsed = time.time() - start_time
            logger.debug(f"Successfully saved: {output_path} (total: {elapsed:.2f}s)")
            return True, ""
        except IOError as e:
            error_msg = f"Tidak bisa menulis file output: {e}"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Error saving output: {e}"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg
    
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(f"Failed to process {input_path}: {error_msg}")
        return False, error_msg
