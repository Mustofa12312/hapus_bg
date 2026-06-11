import threading
import time
import os
from core.scanner import scan_for_images
from core.remover import remove_background
from utils.paths import get_output_folder, recreate_dir_structure
from utils.logger import logger

class BatchProcessor:
    def __init__(self, progress_callback, completion_callback):
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self.is_processing = False
        
    def start(self, input_folder: str):
        if self.is_processing:
            logger.error("Processing already in progress.")
            return
            
        self.is_processing = True
        thread = threading.Thread(target=self._process_worker, args=(input_folder,))
        thread.daemon = True
        thread.start()
        
    def _process_worker(self, input_folder: str):
        logger.info("Starting batch process...")
        try:
            image_files = scan_for_images(input_folder)
            if not image_files:
                logger.info("No image files to process.")
                return

            output_folder = get_output_folder(input_folder)
            logger.info(f"Output folder: {output_folder}")

            total_files = len(image_files)
            
            for i, file_path in enumerate(image_files):
                # Calculate paths
                out_file_path = recreate_dir_structure(input_folder, output_folder, file_path)
                
                # Force output extension to .png because we need transparency
                out_file_path = os.path.splitext(out_file_path)[0] + '.png'
                
                # Remove BG
                logger.info(f"Processing: {file_path}")
                remove_background(file_path, out_file_path)
                
                # Update progress
                progress_val = (i + 1) / total_files
                self.progress_callback(progress_val)

                
        except Exception as e:
            logger.error(f"Fatal error during processing: {e}")
        finally:
            self.is_processing = False
            logger.info("Batch process finished.")
            self.completion_callback()
