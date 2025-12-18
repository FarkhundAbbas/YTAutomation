from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Image Upscaler API", version="1.0.0")

# CORS Configuration - Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from database import engine, Base
from auth import router as auth_router
from routes import processing as processing_router
from routes import export as export_router

Base.metadata.create_all(bind=engine)

app.include_router(auth_router.router)
app.include_router(processing_router.router)
app.include_router(export_router.router)

@app.get("/")
async def root():
    return {"message": "Image Upscaler API is running"}
