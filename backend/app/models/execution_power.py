from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class ExecutionPower(Base):
    __tablename__ = "execution_powers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Permission Level
    level = Column(Integer, default=0)  # 0-10 scale
    
    # Trading Limits
    max_position_size = Column(Numeric(20, 8), default=1000.0)
    max_daily_loss = Column(Numeric(20, 8), default=100.0)
    max_monthly_loss = Column(Numeric(20, 8), default=1000.0)
    
    # Permissions
    can_trade_spot = Column(Boolean, default=False)
    can_trade_futures = Column(Boolean, default=False)
    can_trade_options = Column(Boolean, default=False)
    can_use_leverage = Column(Boolean, default=False)
    max_leverage = Column(Numeric(5, 2), default=1.0)
    
    # Exchanges
    allowed_exchanges = Column(String(500))  # JSON list of exchange IDs
    
    # Approval Status
    approval_status = Column(String(20), default="pending")  # pending, approved, rejected
    approval_notes = Column(Text)
    approved_by = Column(String(100))
    approved_at = Column(DateTime(timezone=True))
    
    # Risk Management
    risk_score = Column(Numeric(5, 2), default=0.0)  # 0-100
    kyc_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="execution_powers")