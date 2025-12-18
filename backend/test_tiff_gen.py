import numpy as np
import tifffile
import os

output_path = "test_output.tiff"
img_array = np.zeros((100, 100, 3), dtype=np.uint8)

print("Starting TIFF generation...")
try:
    with tifffile.TiffWriter(output_path, bigtiff=True) as tif:
        print("Writing Layer 1...")
        tif.write(
            img_array,
            photometric='rgb',
            compression='lzw',
            metadata={'Description': "Layer 1"},
            resolution=(250, 250),
            resolutionunit='INCH'
        )
        
        print("Writing Layer 2...")
        tif.write(
            img_array,
            photometric='rgb',
            compression='lzw',
            metadata={'Description': "Layer 2"},
            resolution=(250, 250),
            resolutionunit='INCH'
        )
        
    print("Generation complete.")
    
    print("Verifying...")
    with tifffile.TiffFile(output_path) as tif:
        print(f"Pages: {len(tif.pages)}")
        for i, p in enumerate(tif.pages):
            print(f"Page {i} tags: {p.tags.keys()}")
            if "ImageDescription" in p.tags:
                print(f"Page {i} Desc: {p.tags['ImageDescription'].value}")
            else:
                print(f"Page {i} Desc: NONE")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
