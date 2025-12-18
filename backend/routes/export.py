"""
Export Router - API endpoints for layered TIFF export
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.job import Job
from processing.layered_psd import layered_psd_generator
import os
from datetime import datetime

router = APIRouter(tags=["Export"], prefix="/export")


class LayeredTiffRequest(BaseModel):
    """Request model for layered TIFF export"""
    job_id: int
    ppi: int = 250
    include_color_layer: bool = True
    bit_depth: int = 16  # 8 or 16


class LayeredTiffResponse(BaseModel):
    """Response model for layered TIFF export"""
    message: str
    file_path: str
    file_size: int
    layers_count: int


@router.post("/layered-tiff", response_class=FileResponse)
async def export_layered_tiff(
    request: LayeredTiffRequest,
    db: Session = Depends(get_db)
):
    """
    Export job result as a layered PSD file (Photoshop Compatible)
    Note: Endpoint kept as /layered-tiff for frontend compatibility, but returns PSD.
    """
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
        
    if not job.output_path or not os.path.exists(job.output_path):
        raise HTTPException(
            status_code=404,
            detail="Processed image file not found"
        )

    try:
        # Create output path for PSD
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"textile_layered_{job.id}_{timestamp}.psd"
        output_dir = "outputs/layered"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        # Generate layered PSD
        final_path, file_size = layered_psd_generator.create_layered_psd(
            image_path=job.output_path,
            output_path=output_path,
            ppi=request.ppi,
            include_color_layer=request.include_color_layer,
            bit_depth=request.bit_depth
        )
        
        # Calculate number of layers
        layers_count = 5  # Base + Detail + Pattern + Shadow + Highlights
        if request.include_color_layer:
            layers_count += 1
        
        return FileResponse(
            final_path,
            media_type="image/vnd.adobe.photoshop",
            filename=output_filename,
            headers={
                "Content-Disposition": f'attachment; filename="{output_filename}"',
                "X-Layers-Count": str(layers_count),
                "X-Bit-Depth": str(request.bit_depth),
                "X-PPI": str(request.ppi)
            }
        )

    except Exception as e:
        print(f"LAYERED PSD ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate layered PSD: {str(e)}"
        )


@router.get("/info/{job_id}")
async def get_export_info(job_id: int, db: Session = Depends(get_db)):
    """
    Get information about available export options for a job
    
    Args:
        job_id: Job ID
        db: Database session
    
    Returns:
        Export information including available formats and estimated file sizes
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "completed":
        return {
            "job_id": job_id,
            "status": job.status,
            "export_available": False,
            "message": "Job must be completed before export"
        }
    
    # Get current file size
    current_size = 0
    if job.output_path and os.path.exists(job.output_path):
        current_size = os.path.getsize(job.output_path)
    
    # Estimate layered TIFF size (approximately 6x for 6 layers)
    estimated_8bit_size = current_size * 6
    estimated_16bit_size = current_size * 12  # 16-bit is roughly 2x larger
    
    return {
        "job_id": job_id,
        "status": job.status,
        "export_available": True,
        "current_file_size": current_size,
        "estimated_layered_8bit_size": estimated_8bit_size,
        "estimated_layered_16bit_size": estimated_16bit_size,
        "available_ppi": [200, 225, 250, 275, 300],
        "available_bit_depths": [8, 16],
        "layer_types": [
            "Base Layer",
            "Detail Enhancement",
            "Pattern/Texture",
            "Shadow Layer",
            "Highlights Layer",
            "Color Correction (optional)"
        ]
    }
