from rembg import remove
from PIL import Image
from utils.logger import logger

def remove_background(input_path: str, output_path: str) -> bool:
    """
    Removes the background from the image at input_path and saves it to output_path.
    Returns True on success, False on failure.
    """
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)
        output_image.save(output_path, format='PNG')
        return True
    except Exception as e:
        logger.error(f"Failed to process {input_path}: {e}")
        return False
