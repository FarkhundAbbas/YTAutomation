"""
Layered PSD Generation Module
Generates Photoshop-compatible PSD files with multiple layers using pytoshop.
"""

import numpy as np
from PIL import Image
import pytoshop
from pytoshop.user import nested_layers
from pytoshop.enums import ColorMode, BlendMode, ColorChannel, ChannelId
import os
from typing import Tuple

class LayeredPsdGenerator:
    """Generate Photoshop-compatible layered PSD files"""
    
    def __init__(self):
        pass
    
    def create_layered_psd(
        self,
        image_path: str,
        output_path: str,
        ppi: int = 250,
        include_color_layer: bool = True,
        bit_depth: int = 8 # PSD typically works best with 8-bit for compatibility, though 16 is supported
    ) -> Tuple[str, int]:
        """
        Create a layered PSD file
        
        Args:
            image_path: Path to input image
            output_path: Path for output layered PSD
            ppi: Pixels per inch
            include_color_layer: Whether to include color correction layer
            bit_depth: 8 or 16 bits per channel
        
        Returns:
            Tuple of (output_path, file_size_bytes)
        """
        # Increase PIL limit for large images
        Image.MAX_IMAGE_PIXELS = None
        
        print(f"DEBUG: Loading image from {image_path}")
        # Load image
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        img_array = np.array(img)
        height, width, channels = img_array.shape
        
        print(f"DEBUG: Image shape: {img_array.shape}, dtype: {img_array.dtype}")
        
        # Ensure image data valid for 8-bit PSD (pytoshop is robust with 8-bit)
        if img_array.dtype == np.uint16:
            print("DEBUG: Converting 16-bit image to 8-bit for PSD compatibility")
            img_array = (img_array / 256).astype(np.uint8)
        elif img_array.dtype != np.uint8:
            print(f"DEBUG: Converting {img_array.dtype} to uint8")
            img_array = img_array.astype(np.uint8)
            
        # Create layers list
        layers = []
        
        # Helper to create a layer from numpy array
        def add_layer(name, array, opacity=255, blend_mode=BlendMode.normal):
            print(f"DEBUG: Adding layer '{name}' shape={array.shape} dtype={array.dtype}")
            
            # Additional safety check
            if array.dtype != np.uint8:
                 array = array.astype(np.uint8)
            
            layer = nested_layers.Image(
                name=name,
                visible=True,
                opacity=opacity,
                group_id=0,
                blend_mode=blend_mode,
                color_mode=ColorMode.rgb
            )
            # Ensure contiguous and copy
            r_channel = np.ascontiguousarray(array[:, :, 0])
            g_channel = np.ascontiguousarray(array[:, :, 1])
            b_channel = np.ascontiguousarray(array[:, :, 2])
            
            # Create alpha channel (full opacity) to prevent pytoshop from inserting -1 placeholder
            # which causes OverflowError
            a_channel = np.full(r_channel.shape, 255, dtype=np.uint8)
            
            print(f"DEBUG: Setting channels for '{name}'. Shapes: {r_channel.shape}")
            
            layer.set_channel(ColorChannel.red, r_channel)
            layer.set_channel(ColorChannel.green, g_channel)
            layer.set_channel(ColorChannel.blue, b_channel)
            layer.set_channel(ChannelId.transparency, a_channel)
            
            layers.append(layer)

        # Layer 1: Base Layer (Clean upscaled)
        add_layer("Base Layer", img_array)
        detail_layer = np.clip(img_array.astype(np.float32) * 1.1, 0, 255).astype(np.uint8)
        add_layer("Detail Enhancement", detail_layer, opacity=255, blend_mode=BlendMode.soft_light)
        del detail_layer
        
        # Layer 3: Pattern/Texture (Edge detection simulation)
        # Using original image as placeholder for pattern to save processing time/memory
        # In a real scenario, this would be an edge detection filter
        add_layer("Pattern/Texture", img_array, opacity=128, blend_mode=BlendMode.overlay)
        
        # Layer 4: Shadow Layer
        shadow_layer = np.clip(img_array.astype(np.float32) * 0.7, 0, 255).astype(np.uint8)
        add_layer("Shadow Layer", shadow_layer, opacity=192, blend_mode=BlendMode.multiply)
        del shadow_layer
        
        # Layer 5: Highlights Layer
        highlight_layer = np.clip(img_array.astype(np.float32) * 1.3, 0, 255).astype(np.uint8)
        add_layer("Highlights Layer", highlight_layer, opacity=192, blend_mode=BlendMode.screen)
        del highlight_layer
        
        # Layer 6: Color Correction
        if include_color_layer:
            # Just a placeholder for color correction, maybe slightly warmer
            add_layer("Color Correction", img_array, opacity=128, blend_mode=BlendMode.color)

        print(f"DEBUG: Generating PSD structure...")
        # Convert to PSD with RAW compression to avoid RLE overflow on large images
        # compression=0 is Raw, 1 is RLE. RLE fails on >2GB or specific byte patterns in pytoshop
        psd = nested_layers.nested_layers_to_psd(
            layers, 
            color_mode=ColorMode.rgb,
            compression=0
        )
        
        # Ensure output directory exists if path contains one
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Change extension to .psd if needed
        if not output_path.lower().endswith('.psd'):
            output_path = os.path.splitext(output_path)[0] + '.psd'
            
        print(f"DEBUG: Writing PSD to {output_path}")
        with open(output_path, 'wb') as f:
            psd.write(f)
            
        file_size = os.path.getsize(output_path)
        print(f"DEBUG: PSD write complete. Size: {file_size} bytes")
        
        return output_path, file_size

# Global instance
layered_psd_generator = LayeredPsdGenerator()
