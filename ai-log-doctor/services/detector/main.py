"""Detector service - Error detection and clustering."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os
import hashlib
import json
from datetime import datetime
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database import get_db_context, LogEvent, ErrorGroup

app = FastAPI(title="AI Log Doctor - Detector Service")


class LogAnalysisRequest(BaseModel):
    logs: List[str]
    platform: str = "generic"


class ErrorGroupResponse(BaseModel):
    error_group_id: int
    hash: str
    log_count: int
    sample_logs: List[str]


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "detector"}


@app.post("/detect-errors", response_model=List[ErrorGroupResponse])
async def detect_errors(request: LogAnalysisRequest):
    """Detect parsing errors and cluster similar failures."""
    try:
        # Simplified error detection: treat all as unparsed for demo
        error_groups = {}
        
        with get_db_context() as db:
            for log_text in request.logs:
                # Create hash for clustering (simplified - in production use embeddings)
                log_hash = hashlib.md5(log_text[:50].encode()).hexdigest()[:8]
                
                # Store log event
                log_event = LogEvent(
                    raw_text=log_text,
                    detected_fields={},
                    parsed_ok=False,
                    platform=request.platform,
                    timestamp=datetime.utcnow()
                )
                
                # Find or create error group
                error_group = db.query(ErrorGroup).filter_by(hash=log_hash).first()
                
                if not error_group:
                    error_group = ErrorGroup(
                        hash=log_hash,
                        example_logs=[log_text],
                        platform=request.platform,
                        log_count=1,
                        created_at=datetime.utcnow()
                    )
                    db.add(error_group)
                    db.flush()
                else:
                    error_group.log_count += 1
                    if len(error_group.example_logs) < 10:
                        error_group.example_logs.append(log_text)
                
                log_event.error_group_id = error_group.id
                db.add(log_event)
                
                if log_hash not in error_groups:
                    error_groups[log_hash] = {
                        "error_group_id": error_group.id,
                        "hash": log_hash,
                        "log_count": error_group.log_count,
                        "sample_logs": error_group.example_logs[:5]
                    }
        
        return [ErrorGroupResponse(**group) for group in error_groups.values()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/error-groups", response_model=List[ErrorGroupResponse])
async def get_error_groups(platform: Optional[str] = None, limit: int = 50):
    """Get all error groups."""
    try:
        with get_db_context() as db:
            query = db.query(ErrorGroup)
            if platform:
                query = query.filter_by(platform=platform)
            
            groups = query.order_by(ErrorGroup.created_at.desc()).limit(limit).all()
            
            return [
                ErrorGroupResponse(
                    error_group_id=g.id,
                    hash=g.hash,
                    log_count=g.log_count,
                    sample_logs=g.example_logs[:5]
                )
                for g in groups
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
