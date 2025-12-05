from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # API
    api_key = Column(String(255), unique=True, index=True)
    
    # Execution Powers
    execution_power_level = Column(Integer, default=0)  # 0-10 scale
    max_position_size = Column(Numeric(20, 8), default=1000.0)
    max_daily_loss = Column(Numeric(20, 8), default=100.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    agents = relationship("Agent", back_populates="owner")
    wallets = relationship("Wallet", back_populates="user")
    crypto_transactions = relationship("CryptoTransaction", back_populates="user")
    execution_powers = relationship("ExecutionPower", back_populates="user")
    sponsored_agents = relationship("AgentSponsorship", back_populates="sponsor_user")