from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class CryptoTransaction(Base):
    __tablename__ = "crypto_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User Reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Transaction Details
    transaction_hash = Column(String(66), unique=True, index=True)  # Ethereum tx hash
    wallet_address = Column(String(42), nullable=False)  # Ethereum address
    
    # Payment Details
    payment_type = Column(String(50), nullable=False)  # arena_entry, agent_clone, sponsorship, etc.
    amount_crypto = Column(Numeric(36, 18), nullable=False)  # Amount in crypto
    amount_usd = Column(Numeric(20, 8), nullable=False)  # Converted USD amount
    currency = Column(String(10), nullable=False)  # ETH, USDC, USDT, etc.
    
    # Chain Information
    chain_id = Column(Integer, nullable=False)  # 1 for Ethereum, 137 for Polygon, etc.
    chain_name = Column(String(20), nullable=False)  # ethereum, polygon, base, arbitrum
    
    # Status
    status = Column(String(20), default="pending")  # pending, confirmed, failed
    confirmations = Column(Integer, default=0)
    
    # Related Entities
    match_id = Column(Integer, ForeignKey("matches.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    sponsorship_id = Column(Integer, ForeignKey("agent_sponsorships.id"))
    
    # Metadata
    metadata = Column(Text)  # JSON metadata
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="crypto_transactions")