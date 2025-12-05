from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class AgentRun(Base):
    __tablename__ = "agent_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Agent Reference
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    agent_version_id = Column(Integer, ForeignKey("agent_versions.id"), nullable=False)
    
    # Run Context
    match_id = Column(Integer, ForeignKey("matches.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Execution Details
    execution_mode = Column(String(20), nullable=False)  # simulation, real
    docker_container_id = Column(String(100))
    
    # Status
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    
    # Performance
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Results
    logs = Column(Text)  # Full execution logs
    error_message = Column(Text)
    performance_metrics = Column(JSON)  # CPU, memory, etc.
    
    # Trading Results (if applicable)
    initial_balance = Column(Numeric(20, 8))
    final_balance = Column(Numeric(20, 8))
    total_trades = Column(Integer, default=0)
    pnl = Column(Numeric(20, 8), default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="agent_runs")
    agent_version = relationship("AgentVersion", back_populates="agent_runs")