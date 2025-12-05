from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Agent Configuration
    strategy_type = Column(String(50))  # scalping, swing, arbitrage, etc.
    risk_tolerance = Column(String(20))  # conservative, moderate, aggressive
    preferred_markets = Column(JSON)  # list of market pairs
    
    # Performance
    total_matches = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    total_pnl = Column(Numeric(20, 8), default=0.0)
    avg_return = Column(Numeric(10, 4), default=0.0)
    sharpe_ratio = Column(Numeric(10, 4), default=0.0)
    max_drawdown = Column(Numeric(10, 4), default=0.0)
    
    # Marketplace
    is_public = Column(Boolean, default=False)
    is_clonable = Column(Boolean, default=False)
    clone_price = Column(Numeric(20, 8), default=0.0)
    royalty_percentage = Column(Numeric(5, 2), default=0.0)  # 0-100%
    
    # Status
    is_active = Column(Boolean, default=True)
    current_version = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_match_at = Column(DateTime(timezone=True))
    
    # Relationships
    owner = relationship("User", back_populates="agents")
    versions = relationship("AgentVersion", back_populates="agent")
    match_participants = relationship("MatchParticipant", back_populates="agent")
    agent_runs = relationship("AgentRun", back_populates="agent")
    sponsorships = relationship("AgentSponsorship", back_populates="agent")

class AgentVersion(Base):
    __tablename__ = "agent_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    version = Column(Integer, nullable=False)
    
    # Code Storage
    code_url = Column(String(255))  # URL to stored code
    docker_image = Column(String(255))  # Docker image tag
    checksum = Column(String(64))  # SHA256 checksum
    
    # Configuration
    config = Column(JSON)  # Agent-specific configuration
    requirements = Column(JSON)  # Python requirements
    
    # Metadata
    changelog = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="versions")
    agent_runs = relationship("AgentRun", back_populates="agent_version")