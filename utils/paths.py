import os
from pathlib import Path

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
    """
    rel_path = os.path.relpath(file_path, input_folder)
    out_file_path = os.path.join(output_folder, rel_path)
    out_dir = os.path.dirname(out_file_path)
    
    os.makedirs(out_dir, exist_ok=True)
    return out_file_path
