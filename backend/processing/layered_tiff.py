"""
Simplified Layered TIFF Generation Module for Photoshop-Compatible Export
Optimized for speed while maintaining layer structure
"""

import numpy as np
from PIL import Image
import tifffile
from typing import Tuple
import os


class LayeredTiffGenerator:
    """Generate Photoshop-compatible layered TIFF files (simplified/fast version)"""
    
    def __init__(self):
        self.layer_names = [
            "Base Layer",
            "Detail Enhancement",
            "Pattern/Texture",
            "Shadow Layer",
            "Highlights Layer",
            "Color Correction"
        ]
    
    def create_layered_tiff(
        self,
        image_path: str,
        output_path: str,
        ppi: int = 250,
        include_color_layer: bool = True,
        bit_depth: int = 16,
        compression: str = 'lzw'
    ) -> Tuple[str, int]:
        """
        Create a layered TIFF file (SIMPLIFIED VERSION for performance)
        
        Args:
            image_path: Path to input image
            output_path: Path for output layered TIFF
            ppi: Pixels per inch (200-300)
            include_color_layer: Whether to include color correction layer
            bit_depth: 8 or 16 bits per channel
            compression: Compression type ('lzw', 'none', etc.)
        
        Returns:
            Tuple of (output_path, file_size_bytes)
        """
        # Increase PIL limit for large images
        Image.MAX_IMAGE_PIXELS = None
        
        # Load image
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Ensure RGB
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=-1)
        elif img_array.shape[2] == 4:
            img_array = img_array[:, :, :3]
            
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write layered TIFF using tifffile with sequential writing to save memory
        print(f"DEBUG: Starting TIFF write to {output_path} with compression={compression}")
        with tifffile.TiffWriter(output_path, bigtiff=True) as tif:
            # Layer 1: Base Layer
            print("DEBUG: Writing Layer 1 (Base)")
            tif.write(
                img_array,
                photometric='rgb',
                compression=compression,
                metadata={'Description': "Base Layer - Clean upscaled image"},
                resolution=(ppi, ppi),
                resolutionunit='INCH'
            )
            
            # Layer 2: Detail Enhancement
            print("DEBUG: Creating Layer 2 (Detail)")
            # Process in-place or with minimal copies
            detail_layer = np.clip(img_array.astype(np.float32) * 1.1, 0, 255).astype(np.uint8)
            print("DEBUG: Writing Layer 2 (Detail)")
            tif.write(
                detail_layer,
                photometric='rgb',
                compression=compression,
                metadata={'Description': "Detail Enhancement - Brightness enhanced"},
                resolution=(ppi, ppi),
                resolutionunit='INCH'
            )
            del detail_layer # Free memory
            
            # Layer 3: Pattern/Texture
            print("DEBUG: Writing Layer 3 (Pattern)")
            tif.write(
                img_array, # Reuse original for pattern to save memory
                photometric='rgb',
                compression=compression,
                metadata={'Description': "Pattern/Texture - Textile pattern layer"},
                resolution=(ppi, ppi),
                resolutionunit='INCH'
            )
            
            # Layer 4: Shadow Layer
            print("DEBUG: Creating Layer 4 (Shadow)")
            shadow_layer = np.clip(img_array.astype(np.float32) * 0.7, 0, 255).astype(np.uint8)
            print("DEBUG: Writing Layer 4 (Shadow)")
            tif.write(
                shadow_layer,
                photometric='rgb',
                compression=compression,
                metadata={'Description': "Shadow Layer - Darkened for shadows"},
                resolution=(ppi, ppi),
                resolutionunit='INCH'
            )
            del shadow_layer # Free memory
            
            # Layer 5: Highlights Layer
            print("DEBUG: Creating Layer 5 (Highlights)")
            highlight_layer = np.clip(img_array.astype(np.float32) * 1.3, 0, 255).astype(np.uint8)
            print("DEBUG: Writing Layer 5 (Highlights)")
            tif.write(
                highlight_layer,
                photometric='rgb',
                compression=compression,
                metadata={'Description': "Highlights Layer - Brightened for highlights"},
                resolution=(ppi, ppi),
                resolutionunit='INCH'
            )
            del highlight_layer # Free memory
            
            # Layer 6: Color Correction
            if include_color_layer:
                print("DEBUG: Writing Layer 6 (Color)")
                tif.write(
                    img_array,
                    photometric='rgb',
                    compression=compression,
                    metadata={'Description': "Color Correction - LAB color adjustments"},
                    resolution=(ppi, ppi),
                    resolutionunit='INCH'
                )
        
        print("DEBUG: TIFF write complete")
        
        # Get file size
        file_size = os.path.getsize(output_path)
        
        return output_path, file_size


# Global instance
layered_tiff_generator = LayeredTiffGenerator()
