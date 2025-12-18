from fastapi import APIRouter, UploadFile, File, Form, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.job import Job
from models.user import User
from auth.jwt_handler import decodeJWT
from processing.pipeline import process_image_task, UPLOAD_DIR
from processing.image_utils import get_image_metadata
import shutil
import os
import uuid
from fastapi.responses import FileResponse

router = APIRouter(tags=["Processing"])

# Dependency to get current user
def get_current_user(token: str = Depends(decodeJWT), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == token["user_id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/process/upload")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    scale: int = Form(...),
    ppi: int = Form(...),
    enhance: bool = Form(False),
    db: Session = Depends(get_db),
    # user: User = Depends(get_current_user) # Commented out for easier testing, uncomment for prod
):
    # Validate file
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Save file
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create Job
    # user_id = user.id
    user_id = 1 # Placeholder for testing without auth header
    
    meta = get_image_metadata(file_path)
    
    new_job = Job(
        user_id=user_id,
        filename=file.filename,
        original_size=f"{meta['width']}x{meta['height']}",
        upscale_factor=scale,
        ppi=ppi,
        status="pending"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Trigger background task
    background_tasks.add_task(process_image_task, new_job.id, file_path, scale, ppi, enhance, db)

    return {"job_id": new_job.id, "status": "pending"}

@router.get("/process/status/{job_id}")
def get_status(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/process/download/{job_id}")
def download_result(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or job.status != "completed":
        raise HTTPException(status_code=404, detail="Result not ready")
    
    return FileResponse(job.output_path, media_type="image/tiff", filename=f"enhanced_{job.filename}.tiff")
