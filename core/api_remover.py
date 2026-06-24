import os
import time
import requests
from utils.logger import logger
from config import PROCESS_TIMEOUT_SECONDS, REMOVEBG_API_KEY

def remove_background_api(input_path: str, output_path: str) -> tuple[bool, str]:
    """
    Removes the background from the image at input_path using remove.bg API
    and saves it to output_path.
    Returns (success: bool, error_message: str)
    """
    try:
        start_time = time.time()
        
        if not REMOVEBG_API_KEY:
            error_msg = "API Key remove.bg tidak ditemukan (periksa api_remove_bk.md)"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg

        if not os.path.exists(input_path):
            error_msg = "File input tidak ditemukan"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg
            
        file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        logger.debug(f"Processing file with API: {input_path} ({file_size_mb:.1f}MB)")

        try:
            with open(input_path, 'rb') as f:
                response = requests.post(
                    'https://api.remove.bg/v1.0/removebg',
                    files={'image_file': f},
                    data={'size': 'auto'},
                    headers={'X-Api-Key': REMOVEBG_API_KEY},
                    timeout=PROCESS_TIMEOUT_SECONDS
                )
        except requests.exceptions.RequestException as e:
            error_msg = f"API Request failed: {e}"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg

        if response.status_code == requests.codes.ok:
            try:
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    
                if os.path.exists(output_path):
                    os.remove(output_path)

                with open(output_path, 'wb') as out:
                    out.write(response.content)
                    
                elapsed = time.time() - start_time
                logger.debug(f"Successfully saved via API: {output_path} (total: {elapsed:.2f}s)")
                return True, ""
            except Exception as e:
                error_msg = f"Failed to save output: {e}"
                logger.error(f"Failed to process {input_path}: {error_msg}")
                return False, error_msg
        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            logger.error(f"Failed to process {input_path}: {error_msg}")
            return False, error_msg

    except Exception as e:
        error_msg = f"Unexpected API error: {e}"
        logger.error(f"Failed to process {input_path}: {error_msg}")
        return False, error_msg
