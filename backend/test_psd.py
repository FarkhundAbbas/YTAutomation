import numpy as np
import pytoshop
from pytoshop.user import nested_layers
from pytoshop.enums import ColorMode, BlendMode, ColorChannel
import os

output_path = "test_output.psd"
width = 100
height = 100

# Create dummy layers
layers = []

# Layer 1: Base
img1 = np.zeros((height, width, 3), dtype=np.uint8)
img1[:, :, 0] = 255 # Red
layer1 = nested_layers.Image(name="Base Layer", visible=True, opacity=255, group_id=0, blend_mode=BlendMode.normal, color_mode=ColorMode.rgb)
layer1.set_channel(ColorChannel.red, img1[:, :, 0])
layer1.set_channel(ColorChannel.green, img1[:, :, 1])
layer1.set_channel(ColorChannel.blue, img1[:, :, 2])
layers.append(layer1)

# Layer 2: Detail
img2 = np.zeros((height, width, 3), dtype=np.uint8)
img2[:, :, 1] = 255 # Green
layer2 = nested_layers.Image(name="Detail Layer", visible=True, opacity=128, group_id=0, blend_mode=BlendMode.normal, color_mode=ColorMode.rgb)
layer2.set_channel(ColorChannel.red, img2[:, :, 0])
layer2.set_channel(ColorChannel.green, img2[:, :, 1])
layer2.set_channel(ColorChannel.blue, img2[:, :, 2])
layers.append(layer2)

psd = nested_layers.nested_layers_to_psd(layers, color_mode=ColorMode.rgb)

with open(output_path, 'wb') as f:
    psd.write(f)

print(f"PSD generated at {output_path}")
print(f"File size: {os.path.getsize(output_path)} bytes")
