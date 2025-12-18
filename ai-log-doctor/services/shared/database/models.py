"""Shared database models for AI Log Doctor."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class LogEvent(Base):
    """Raw log events."""
    
    __tablename__ = "log_events"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(Text, nullable=False)
    detected_fields = Column(JSON, default=dict)
    parsed_ok = Column(Boolean, default=False, index=True)
    platform = Column(String(50), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    error_group_id = Column(Integer, ForeignKey("error_groups.id"), nullable=True)
    
    error_group = relationship("ErrorGroup", back_populates="log_events")


class ErrorGroup(Base):
    """Clustered error groups."""
    
    __tablename__ = "error_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String(64), unique=True, index=True)
    example_logs = Column(JSON, default=list)
    platform = Column(String(50), index=True)
    log_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    log_events = relationship("LogEvent", back_populates="error_group")
    proposals = relationship("Proposal", back_populates="error_group")


class Proposal(Base):
    """Fix proposals with candidate patterns."""
    
    __tablename__ = "proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    error_group_id = Column(Integer, ForeignKey("error_groups.id"), nullable=False)
    candidate_patterns = Column(JSON, default=list)
    validation_scores = Column(JSON, default=dict)
    status = Column(
        String(20),
        default="pending",
        index=True,
    )  # pending, approved, applied, rolled_back, rejected
    selected_pattern_index = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    applied_at = Column(DateTime, nullable=True)
    approved_by = Column(String(100), nullable=True)
    
    error_group = relationship("ErrorGroup", back_populates="proposals")
    rules = relationship("Rule", back_populates="proposal")


class Rule(Base):
    """Applied rules and versions."""
    
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    platform = Column(String(50), index=True)
    pattern = Column(Text, nullable=False)
    pattern_type = Column(String(20))  # regex, grok, decoder
    version = Column(Integer, default=1)
    rollback_reference = Column(Integer, ForeignKey("rules.id"), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    proposal = relationship("Proposal", back_populates="rules")


class AuditLog(Base):
    """Action audit trail."""
    
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(100), index=True)
    action = Column(String(100), index=True)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String(50), nullable=True)
    success = Column(Boolean, default=True)


class User(Base):
    """User authentication."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(20), default="viewer")  # admin, operator, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class SIEMConnector(Base):
    """SIEM connection configurations."""
    
    __tablename__ = "siem_connectors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    platform = Column(String(50), index=True)  # qradar, wazuh, splunk, elastic
    base_url = Column(String(255), nullable=False)
    credentials = Column(JSON, default=dict)  # encrypted
    config = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    last_tested = Column(DateTime, nullable=True)
    last_test_status = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create indexes for performance
Index("idx_log_events_parsed_timestamp", LogEvent.parsed_ok, LogEvent.timestamp)
Index("idx_proposals_status_created", Proposal.status, Proposal.created_at)
Index("idx_rules_platform_active", Rule.platform, Rule.is_active)
