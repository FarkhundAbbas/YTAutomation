import os
import sys
sys.path.insert(0, '/app')

from processing.layered_tiff import LayeredTiffGenerator

# Test with an existing output file
test_image = "/app/outputs/d25387a0-ddcb-43ab-89a6-6e0511c61b96_final.tiff"

if not os.path.exists(test_image):
    print(f"Test image not found: {test_image}")
    sys.exit(1)

print(f"Testing layered TIFF generation with: {test_image}")

generator = LayeredTiffGenerator()
output_path = "/app/outputs/layered/test_layered.tiff"

try:
    final_path, file_size = generator.create_layered_tiff(
        image_path=test_image,
        output_path=output_path,
        ppi=250,
        include_color_layer=True,
        bit_depth=16,
        compression='lzw'
    )
    print(f"SUCCESS! Generated: {final_path}, Size: {file_size} bytes")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
