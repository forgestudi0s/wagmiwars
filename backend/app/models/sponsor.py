from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Sponsor(Base):
    __tablename__ = "sponsors"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Sponsor Details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    website_url = Column(String(255))
    logo_url = Column(String(255))
    
    # Contact
    contact_email = Column(String(100))
    contact_person = Column(String(100))
    
    # Sponsorship Details
    sponsorship_tier = Column(String(20), default="bronze")  # bronze, silver, gold, platinum
    monthly_budget = Column(Numeric(20, 8), default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sponsorships = relationship("AgentSponsorship", back_populates="sponsor")

class AgentSponsorship(Base):
    __tablename__ = "agent_sponsorships"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # References
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    sponsor_user_id = Column(Integer, ForeignKey("users.id"))  # If individual user sponsoring
    
    # Sponsorship Details
    amount = Column(Numeric(20, 8), nullable=False)
    duration_months = Column(Integer, default=1)
    
    # Badge Placement
    badge_text = Column(String(100))
    badge_url = Column(String(255))
    badge_position = Column(String(20), default="profile")  # profile, leaderboard, both
    
    # Status
    status = Column(String(20), default="active")  # active, completed, cancelled
    
    # Performance Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    sponsor = relationship("Sponsor", back_populates="sponsorships")
    agent = relationship("Agent", back_populates="sponsorships")
    sponsor_user = relationship("User", back_populates="sponsored_agents")
    crypto_transactions = relationship("CryptoTransaction", back_populates="sponsorship")