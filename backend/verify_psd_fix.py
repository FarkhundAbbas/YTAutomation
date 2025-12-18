
import os
import sys
import numpy as np
from PIL import Image

# Ensure we can import from the application root
sys.path.append('/app')

try:
    from processing.layered_psd import layered_psd_generator
    print("SUCCESS: Imported layered_psd_generator")
except ImportError as e:
    print(f"FAILURE: Could not import layered_psd_generator: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILURE: Error during import: {e}")
    sys.exit(1)

def test_generation():
    print("Starting PSD generation test...")
    
    # Create dummy image
    img = Image.new('RGB', (1000, 1000), color = 'red')
    input_path = "verify_test_input.png"
    output_path = "verify_test_output.psd"
    img.save(input_path)
    
    try:
        final_path, size = layered_psd_generator.create_layered_psd(
            image_path=input_path,
            output_path=output_path,
            ppi=300,
            include_color_layer=True
        )
        print(f"SUCCESS: Generated PSD at {final_path} (Size: {size} bytes)")
        
        if os.path.exists(final_path) and size > 0:
             print("VERIFICATION PASSED: File exists and has content.")
        else:
             print("VERIFICATION FAILED: File missing or empty.")
             
    except Exception as e:
        print(f"VERIFICATION FAILED: Exception during generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    test_generation()
