import os
from utils.logger import logger

def scan_for_images(folder_path: str) -> list[str]:
    """
    Scans the given folder and its subfolders for image files (.png, .jpg, .jpeg).
    Returns a list of absolute paths to the found files.
    """
    image_files = []
    logger.info(f"Scanning folder: {folder_path}")
    
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        logger.error(f"Invalid folder: {folder_path}")
        return image_files

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_files.append(os.path.join(root, file))
                
    logger.info(f"Found {len(image_files)} image files.")
    return image_files
