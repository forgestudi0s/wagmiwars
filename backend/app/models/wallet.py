from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User Reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Wallet Details
    address = Column(String(42), nullable=False, unique=True, index=True)  # Ethereum address
    chain_id = Column(Integer, nullable=False, default=1)  # 1 for Ethereum
    chain_name = Column(String(20), nullable=False, default="ethereum")
    
    # Wallet Type
    wallet_type = Column(String(20), default="metamask")  # metamask, walletconnect, coinbase
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verification_message = Column(String(255))
    verification_signature = Column(Text)
    
    # Primary Wallet
    is_primary = Column(Boolean, default=False)
    
    # Nickname/Label
    nickname = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="wallets")