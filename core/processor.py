import threading
import time
import os
import psutil
from core.scanner import scan_for_images
from core.remover import remove_background
from core.api_remover import remove_background_api
from utils.paths import get_output_folder, recreate_dir_structure, validate_input_folder, validate_output_folder, get_available_disk_space
from utils.logger import logger
from config import BATCH_SIZE_WARNING, MIN_FREE_DISK_SPACE_MB, RETRY_ATTEMPTS, MAX_RAM_USAGE_PERCENT

class BatchProcessor:
    def __init__(self, progress_callback, completion_callback):
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self.is_processing = False
        self.should_stop = False
        self.stats = {
            "success": 0, 
            "failed": 0, 
            "skipped": 0,
            "retried": 0,
            "total": 0
        }
        self.failed_files = []  # Track failed files for reporting
        
    def start(self, input_folder: str, mode: str = "local"):
        """Start batch processing with validation."""
        if self.is_processing:
            logger.error("Processing already in progress.")
            return
            
        self.is_processing = True
        self.should_stop = False
        self.stats = {"success": 0, "failed": 0, "skipped": 0, "retried": 0, "total": 0}
        self.failed_files = []
        thread = threading.Thread(target=self._process_worker, args=(input_folder, mode))
        thread.daemon = True
        thread.start()
    
    def stop(self):
        """Signal the processor to stop gracefully."""
        self.should_stop = True
        logger.info("Stopping process...")
        
    def _check_system_resources(self) -> tuple[bool, str]:
        """Check if system has sufficient resources."""
        try:
            # Check RAM usage
            ram_percent = psutil.virtual_memory().percent
            if ram_percent > MAX_RAM_USAGE_PERCENT:
                return False, f"Penggunaan RAM terlalu tinggi: {ram_percent:.1f}%"
            
            return True, ""
        except Exception as e:
            logger.warning(f"Could not check system resources: {e}")
            return True, ""  # Don't fail if we can't check
    
    def _process_worker(self, input_folder: str, mode: str):
        """Main processing worker thread."""
        logger.info("=" * 60)
        logger.info("🚀 Starting batch process...")
        logger.info("=" * 60)
        
        try:
            # ========== VALIDATION PHASE ==========
            logger.info("📋 Phase 1: Validating input folder...")
            
            is_valid, msg = validate_input_folder(input_folder)
            if not is_valid:
                logger.error(f"Input validation failed: {msg}")
                return
            logger.info(f"✅ Input folder valid: {input_folder}")
            
            # Scan for images
            logger.info("📋 Phase 2: Scanning for images...")
            image_files = scan_for_images(input_folder, validate=True)
            
            if not image_files:
                logger.warning("⚠️  No valid image files found to process.")
                return
            
            total_files = len(image_files)
            self.stats["total"] = total_files
            logger.info(f"✅ Found {total_files} images to process")
            
            # Warn if large batch
            if total_files > BATCH_SIZE_WARNING:
                logger.warning(f"⚠️  Large batch detected ({total_files} files). Processing will take time.")
            
            # Get output folder
            output_folder = get_output_folder(input_folder)
            
            # Validate output folder
            logger.info("📋 Phase 3: Validating output folder...")
            is_valid, msg = validate_output_folder(output_folder)
            if not is_valid:
                logger.error(f"Output validation failed: {msg}")
                return
            logger.info(f"✅ Output folder valid: {output_folder}")
            
            # Check disk space
            free_space_mb = get_available_disk_space(output_folder)
            if free_space_mb < MIN_FREE_DISK_SPACE_MB:
                logger.warning(f"⚠️  Low disk space: {free_space_mb:.1f}MB available")
            else:
                logger.info(f"✅ Disk space OK: {free_space_mb:.1f}MB available")
            
            # ========== PROCESSING PHASE ==========
            logger.info("📋 Phase 4: Processing images...")
            logger.info(f"Starting to process {total_files} files...")
            
            start_time = time.time()
            
            for i, file_path in enumerate(image_files):
                # Check if stop signal received
                if self.should_stop:
                    logger.warning("⏹️  Process stopped by user.")
                    break
                
                # Check system resources periodically
                if i % 10 == 0:  # Check every 10 files
                    ok, msg = self._check_system_resources()
                    if not ok:
                        logger.error(f"System resource check failed: {msg}")
                        break
                
                # Calculate paths
                try:
                    out_file_path = recreate_dir_structure(input_folder, output_folder, file_path)
                    # Force output extension to .png because we need transparency
                    out_file_path = os.path.splitext(out_file_path)[0] + '.png'
                except Exception as e:
                    logger.error(f"Failed to calculate output path for {file_path}: {e}")
                    self.stats["failed"] += 1
                    self.failed_files.append((file_path, str(e)))
                    continue
                
                # Remove background with retry logic
                success = False
                error_msg = ""
                
                for attempt in range(1, RETRY_ATTEMPTS + 1):
                    if self.should_stop:
                        break
                    
                    logger.info(f"[{i+1}/{total_files}] Processing: {os.path.basename(file_path)}")
                    if mode == "api":
                        success, error_msg = remove_background_api(file_path, out_file_path)
                    else:
                        success, error_msg = remove_background(file_path, out_file_path)
                    
                    if success:
                        self.stats["success"] += 1
                        logger.info(f"✅ Success: {os.path.basename(file_path)}")
                        break
                    elif attempt < RETRY_ATTEMPTS:
                        self.stats["retried"] += 1
                        logger.warning(f"⚠️  Attempt {attempt}/{RETRY_ATTEMPTS} failed. Retrying...")
                        time.sleep(1)  # Brief delay before retry
                    else:
                        logger.error(f"❌ Failed after {RETRY_ATTEMPTS} attempts: {os.path.basename(file_path)}")
                
                if not success:
                    self.stats["failed"] += 1
                    self.failed_files.append((file_path, error_msg))
                
                # Update progress
                progress_val = (i + 1) / total_files
                self.progress_callback(progress_val)
            
            # ========== COMPLETION PHASE ==========
            elapsed = time.time() - start_time
            logger.info("\n" + "=" * 60)
            logger.info("✅ BATCH PROCESS COMPLETED")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Fatal error during processing: {e}", exc_info=True)
        
        finally:
            self.is_processing = False
            self._log_summary(elapsed if 'elapsed' in locals() else 0)
            self.completion_callback()
    
    def _log_summary(self, elapsed_time: float):
        """Log detailed summary of processing."""
        total = self.stats["success"] + self.stats["failed"]
        success_rate = (self.stats["success"] / total * 100) if total > 0 else 0
        
        logger.info(f"📊 Processing Summary:")
        logger.info(f"   ✅ Success: {self.stats['success']}/{total} ({success_rate:.1f}%)")
        logger.info(f"   ❌ Failed: {self.stats['failed']}")
        logger.info(f"   🔄 Retries: {self.stats['retried']}")
        logger.info(f"   ⏱️  Total time: {elapsed_time:.1f}s")
        
        if total > 0:
            avg_time = elapsed_time / total
            logger.info(f"   ⏱️  Average per file: {avg_time:.2f}s")
        
        if self.failed_files:
            logger.warning(f"\n❌ Failed files ({len(self.failed_files)}):")
            for file_path, error in self.failed_files[:10]:  # Log first 10 failures
                logger.warning(f"   - {os.path.basename(file_path)}: {error}")
            if len(self.failed_files) > 10:
                logger.warning(f"   ... and {len(self.failed_files) - 10} more")
        
        logger.info("=" * 60)
