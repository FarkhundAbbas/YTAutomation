from PIL import Image
import os

def save_as_tiff(image_path: str, output_path: str, ppi: int = 250):
    """
    Converts an image to TIFF format with specified PPI and LZW compression.
    """
    try:
        with Image.open(image_path) as img:
            # Ensure RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as TIFF
            img.save(
                output_path,
                format='TIFF',
                dpi=(ppi, ppi),
                compression='tiff_lzw_le' # LZW compression
            )
        return True
    except Exception as e:
        print(f"Error saving TIFF: {e}")
        return False

def get_image_metadata(image_path: str):
    with Image.open(image_path) as img:
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode
        }
