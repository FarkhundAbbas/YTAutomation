"""Validator service - Pattern validation."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database import get_db_context, Proposal

app = FastAPI(title="AI Log Doctor - Validator Service")


class ValidationRequest(BaseModel):
    proposal_id: int
    pattern_index: int
    test_logs: List[str]


class ValidationResponse(BaseModel):
    proposal_id: int
    pattern_index: int
    total_logs: int
    parsed_successfully: int
    parse_rate: float
    errors: List[str]
    status: str


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "validator"}


@app.post("/validate-pattern", response_model=ValidationResponse)
async def validate_pattern(request: ValidationRequest):
    """Validate a pattern against test logs."""
    try:
        # Get proposal from database
        with get_db_context() as db:
            proposal = db.query(Proposal).filter_by(id=request.proposal_id).first()
            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal not found")
            
            candidates = proposal.candidate_patterns
            if request.pattern_index >= len(candidates):
                raise HTTPException(status_code=400, detail="Invalid pattern index")
            
            pattern_data = candidates[request.pattern_index]
            pattern = pattern_data["pattern"]
            pattern_type = pattern_data.get("pattern_type", "regex")
            
            # Validate pattern
            parsed_count = 0
            errors = []
            
            for i, log in enumerate(request.test_logs):
                try:
                    if pattern_type == "regex":
                        match = re.search(pattern, log)
                        if match:
                            parsed_count += 1
                        else:
                            errors.append(f"Log {i}: No match")
                    elif pattern_type == "grok":
                        # Simplified grok validation
                        if "GREEDYDATA" in pattern or "IP" in pattern:
                            parsed_count += 1
                        else:
                            errors.append(f"Log {i}: Grok pattern validation needed")
                except re.error as e:
                    errors.append(f"Log {i}: Regex error - {str(e)}")
            
            total = len(request.test_logs)
            parse_rate = parsed_count / total if total > 0 else 0
            
            # Update proposal with validation scores
            if not proposal.validation_scores:
                proposal.validation_scores = {}
            
            proposal.validation_scores[str(request.pattern_index)] = {
                "total_logs": total,
                "parsed_successfully": parsed_count,
                "parse_rate": parse_rate,
                "errors": errors[:10]  # Store first 10 errors
            }
            db.commit()
            
            return ValidationResponse(
                proposal_id=request.proposal_id,
                pattern_index=request.pattern_index,
                total_logs=total,
                parsed_successfully=parsed_count,
                parse_rate=parse_rate,
                errors=errors[:10],
                status="success" if parse_rate >= 0.8 else "needs_improvement"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/validation/{proposal_id}")
async def get_validation_report(proposal_id: int):
    """Get validation report for a proposal."""
    try:
        with get_db_context() as db:
            proposal = db.query(Proposal).filter_by(id=proposal_id).first()
            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal not found")
            
            return {
                "proposal_id": proposal_id,
                "status": proposal.status,
                "validation_scores": proposal.validation_scores or {},
                "candidates": proposal.candidate_patterns
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
