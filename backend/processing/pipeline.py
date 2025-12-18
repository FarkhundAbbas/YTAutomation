import os
import uuid
from sqlalchemy.orm import Session
from models.job import Job
from processing.upscaler import upscaler_service
from processing.image_utils import save_as_tiff, get_image_metadata

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def process_image_task(job_id: int, file_path: str, scale: int, ppi: int, enhance: bool, db: Session):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return

    try:
        job.status = "processing"
        db.commit()

        # Generate output paths
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        upscaled_filename = f"{name}_upscaled_{scale}x.png"
        final_filename = f"{name}_final.tiff"
        
        upscaled_path = os.path.join(OUTPUT_DIR, upscaled_filename)
        final_path = os.path.join(OUTPUT_DIR, final_filename)

        # Step 1: Upscale
        # For 16K (scale 8x from 2K or similar), we might need recursive upscaling
        # Here we just pass the scale to the service
        upscaler_service.upscale_image(file_path, upscaled_path, scale)

        # Step 2: Enhance (Optional)
        if enhance:
            upscaler_service.enhance_details(upscaled_path, upscaled_path)

        # Step 3: Convert to TIFF with PPI
        save_as_tiff(upscaled_path, final_path, ppi)

        # Update Job
        meta = get_image_metadata(final_path)
        job.output_path = final_path
        job.enhanced_size = f"{meta['width']}x{meta['height']}"
        job.status = "completed"
        db.commit()

    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        job.status = "failed"
        db.commit()
