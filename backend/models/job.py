from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    original_size = Column(String)
    enhanced_size = Column(String)
    upscale_factor = Column(Integer)
    ppi = Column(Integer)
    status = Column(String) # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    output_path = Column(String, nullable=True)

    user = relationship("User", backref="jobs")
