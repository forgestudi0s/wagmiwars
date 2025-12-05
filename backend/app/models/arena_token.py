from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class ArenaToken(Base):
    __tablename__ = "arena_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User Reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Token Details
    token_balance = Column(Numeric(20, 8), default=0.0)
    token_symbol = Column(String(10), default="WAGMI")
    
    # Usage Tracking
    tokens_earned = Column(Numeric(20, 8), default=0.0)
    tokens_spent = Column(Numeric(20, 8), default=0.0)
    
    # Tournament Boosts
    active_boosts = Column(String(500))  # JSON array of active boosts
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")