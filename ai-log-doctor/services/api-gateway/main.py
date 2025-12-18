"""API Gateway - Main entry point."""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database import get_db_context, User, Proposal, ErrorGroup, SIEMConnector, AuditLog, Rule
from shared.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    Token
)
from shared.connectors import get_connector

app = FastAPI(title="AI Log Doctor - API Gateway", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Service URLs
DETECTOR_URL = os.getenv("DETECTOR_URL", "http://localhost:8002")
INFERER_URL = os.getenv("INFERER_URL", "http://localhost:8003")
VALIDATOR_URL = os.getenv("VALIDATOR_URL", "http://localhost:8004")


# Models
class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: str = "viewer"


class ProposalApprove(BaseModel):
    pattern_index: int
    user: str


class SIEMConnectorCreate(BaseModel):
    name: str
    platform: str
    base_url: str
    credentials: Dict[str, Any]
    config: Optional[Dict[str, Any]] = {}


# Auth dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user."""
    token_data = decode_access_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return token_data


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-gateway"}


# Auth endpoints
@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user."""
    try:
        with get_db_context() as db:
            # Check if user exists
            existing = db.query(User).filter(
                (User.username == user_data.username) | (User.email == user_data.email)
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="User already exists")
            
            # Create user
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=get_password_hash(user_data.password),
                full_name=user_data.full_name,
                role=user_data.role,
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.flush()
            
            # Create access token
            access_token = create_access_token(
                data={"sub": user.username, "role": user.role}
            )
            return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Login and get access token."""
    try:
        with get_db_context() as db:
            user = db.query(User).filter_by(username=login_data.username).first()
            if not user or not verify_password(login_data.password, user.hashed_password):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            user.last_login = datetime.utcnow()
            db.commit()
            
            access_token = create_access_token(
                data={"sub": user.username, "role": user.role}
            )
            return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Proposal endpoints
@app.post("/proposals/create")
async def create_proposal(
    error_group_id: int,
    platform: str = "generic",
    current_user = Depends(get_current_user)
):
    """Create a new pattern proposal."""
    try:
        # Get error group
        with get_db_context() as db:
            error_group = db.query(ErrorGroup).filter_by(id=error_group_id).first()
            if not error_group:
                raise HTTPException(status_code=404, detail="Error group not found")
            
            sample_logs = error_group.example_logs
        
        # Call inferer service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{INFERER_URL}/generate-patterns",
                json={
                    "error_group_id": error_group_id,
                    "sample_logs": sample_logs,
                    "platform": platform
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: int, current_user = Depends(get_current_user)):
    """Get proposal details."""
    try:
        with get_db_context() as db:
            proposal = db.query(Proposal).filter_by(id=proposal_id).first()
            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal not found")
            
            return {
                "id": proposal.id,
                "error_group_id": proposal.error_group_id,
                "candidate_patterns": proposal.candidate_patterns,
                "validation_scores": proposal.validation_scores,
                "status": proposal.status,
                "created_at": proposal.created_at.isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/proposals/{proposal_id}/approve")
async def approve_proposal(
    proposal_id: int,
    approval: ProposalApprove,
    current_user = Depends(get_current_user)
):
    """Approve a proposal."""
    try:
        with get_db_context() as db:
            proposal = db.query(Proposal).filter_by(id=proposal_id).first()
            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal not found")
            
            proposal.status = "approved"
            proposal.selected_pattern_index = approval.pattern_index
            proposal.approved_at = datetime.utcnow()
            proposal.approved_by = approval.user
            
            # Log action
            audit = AuditLog(
                user=approval.user,
                action="proposal_approved",
                details={"proposal_id": proposal_id, "pattern_index": approval.pattern_index},
                timestamp=datetime.utcnow()
            )
            db.add(audit)
            
            return {"status": "approved", "proposal_id": proposal_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/proposals/{proposal_id}/reject")
async def reject_proposal(proposal_id: int, current_user = Depends(get_current_user)):
    """Reject a proposal."""
    try:
        with get_db_context() as db:
            proposal = db.query(Proposal).filter_by(id=proposal_id).first()
            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal not found")
            
            proposal.status = "rejected"
            
            return {"status": "rejected", "proposal_id": proposal_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Apply/Rollback endpoints
@app.post("/apply/{proposal_id}")
async def apply_fix(proposal_id: int, current_user = Depends(get_current_user)):
    """Apply a fix to the SIEM platform."""
    try:
        with get_db_context() as db:
            proposal = db.query(Proposal).filter_by(id=proposal_id).first()
            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal not found")
            
            if proposal.status != "approved":
                raise HTTPException(status_code=400, detail="Proposal not approved")
            
            # Get selected pattern
            pattern_idx = proposal.selected_pattern_index
            if pattern_idx is None:
                raise HTTPException(status_code=400, detail="No pattern selected")
            
            pattern_data = proposal.candidate_patterns[pattern_idx]
            
            # Get error group to determine platform
            error_group = db.query(ErrorGroup).filter_by(id=proposal.error_group_id).first()
            platform = error_group.platform if error_group else "generic"
            
            # Create rule
            rule = Rule(
                proposal_id=proposal_id,
                platform=platform,
                pattern=pattern_data["pattern"],
                pattern_type=pattern_data.get("pattern_type", "regex"),
                version=1,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(rule)
            db.flush()
            
            proposal.status = "applied"
            proposal.applied_at = datetime.utcnow()
            
            # Log action
            audit = AuditLog(
                user=current_user.username,
                action="fix_applied",
                details={"proposal_id": proposal_id, "rule_id": rule.id},
                timestamp=datetime.utcnow()
            )
            db.add(audit)
            
            return {
                "status": "applied",
                "proposal_id": proposal_id,
                "rule_id": rule.id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rollback/{rule_id}")
async def rollback(rule_id: int, current_user = Depends(get_current_user)):
    """Rollback a rule."""
    try:
        with get_db_context() as db:
            rule = db.query(Rule).filter_by(id=rule_id).first()
            if not rule:
                raise HTTPException(status_code=404, detail="Rule not found")
            
            rule.is_active = False
            
            # Update proposal status
            proposal = db.query(Proposal).filter_by(id=rule.proposal_id).first()
            if proposal:
                proposal.status = "rolled_back"
            
            # Log action
            audit = AuditLog(
                user=current_user.username,
                action="rule_rolled_back",
                details={"rule_id": rule_id},
                timestamp=datetime.utcnow()
            )
            db.add(audit)
            
            return {"status": "rolled_back", "rule_id": rule_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# SIEM Connector endpoints
@app.post("/connectors/test")
async def test_connector(connector_id: int, current_user = Depends(get_current_user)):
    """Test SIEM connector."""
    try:
        with get_db_context() as db:
            connector = db.query(SIEMConnector).filter_by(id=connector_id).first()
            if not connector:
                raise HTTPException(status_code=404, detail="Connector not found")
            
            # Get connector instance
            siem_connector = get_connector(connector.platform, {
                "base_url": connector.base_url,
                "credentials": connector.credentials,
                **connector.config
            })
            
            # Test connection
            result = await siem_connector.test_connection()
            
            # Update connector
            connector.last_tested = datetime.utcnow()
            connector.last_test_status = result.get("status", "error")
            db.commit()
            
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Validation report
@app.get("/validation/{proposal_id}")
async def get_validation_report(proposal_id: int, current_user = Depends(get_current_user)):
    """Get validation report."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VALIDATOR_URL}/validation/{proposal_id}",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dashboard stats
@app.get("/stats/dashboard")
async def get_dashboard_stats(current_user = Depends(get_current_user)):
    """Get dashboard statistics."""
    try:
        with get_db_context() as db:
            total_errors = db.query(ErrorGroup).count()
            pending_proposals = db.query(Proposal).filter_by(status="pending").count()
            applied_fixes = db.query(Proposal).filter_by(status="applied").count()
            active_rules = db.query(Rule).filter_by(is_active=True).count()
            
            return {
                "total_error_groups": total_errors,
                "pending_proposals": pending_proposals,
                "applied_fixes": applied_fixes,
                "active_rules": active_rules
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
