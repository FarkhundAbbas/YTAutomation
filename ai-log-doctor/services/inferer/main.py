"""Inferer service - AI-powered pattern generation."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database import get_db_context, ErrorGroup, Proposal
from .engine import inference_engine
import hashlib
from datetime import datetime

app = FastAPI(title="AI Log Doctor - Inferer Service")


class PatternGenerationRequest(BaseModel):
    error_group_id: int
    sample_logs: List[str]
    platform: str = "generic"


class PatternGenerationResponse(BaseModel):
    proposal_id: int
    candidates: List[Dict[str, Any]]


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "inferer"}


@app.post("/generate-patterns", response_model=PatternGenerationResponse)
async def generate_patterns(request: PatternGenerationRequest):
    """Generate regex/grok patterns for failed logs."""
    try:
        # Generate patterns using AI engine
        candidates = inference_engine.generate_regex_patterns(request.sample_logs)
        
        if not candidates:
            raise HTTPException(status_code=500, detail="Failed to generate patterns")
        
        # For each candidate, generate platform-specific decoder
        for candidate in candidates:
            decoder = inference_engine.generate_platform_decoder(
                request.platform,
                candidate["pattern"],
                candidate["pattern_type"]
            )
            candidate["decoder"] = decoder
        
        # Store proposal in database
        with get_db_context() as db:
            proposal = Proposal(
                error_group_id=request.error_group_id,
                candidate_patterns=candidates,
                validation_scores={},
                status="pending",
                created_at=datetime.utcnow()
            )
            db.add(proposal)
            db.flush()
            proposal_id = proposal.id
        
        return PatternGenerationResponse(
            proposal_id=proposal_id,
            candidates=candidates
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-logs")
async def analyze_logs(logs: List[str]):
    """Analyze log structure."""
    try:
        analysis = inference_engine.analyze_logs(logs)
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
