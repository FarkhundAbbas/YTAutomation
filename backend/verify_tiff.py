import tifffile
import glob
import os

try:
    files = glob.glob('/app/outputs/layered/*.tiff')
    if not files:
        print("No TIFF files found.")
        exit(1)
        
    latest_file = max(files, key=os.path.getctime)
    print(f'Checking {latest_file}...')
    
    with tifffile.TiffFile(latest_file) as tif:
        print(f'Number of pages: {len(tif.pages)}')
        for i, p in enumerate(tif.pages):
            desc = "No Description"
            if "ImageDescription" in p.tags:
                desc = p.tags["ImageDescription"].value
            print(f'Page {i}: {desc}')
            
except Exception as e:
    print(f"Error: {e}")
