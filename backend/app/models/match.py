from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Match Configuration
    mode = Column(String(20), nullable=False)  # testing, demo, production
    duration_minutes = Column(Integer, default=60)
    initial_balance = Column(Numeric(20, 8), default=10000.0)
    
    # Market Configuration
    market_pairs = Column(JSON)  # ["BTC/USDT", "ETH/USDT"]
    data_source = Column(String(50))  # binance, coinbase, etc.
    
    # Status
    status = Column(String(20), default="pending")  # pending, running, completed, cancelled
    current_tick = Column(Integer, default=0)
    total_ticks = Column(Integer, default=3600)  # 1 hour at 1 tick/sec
    
    # Results
    winner_id = Column(Integer, ForeignKey("agents.id"))
    total_volume = Column(Numeric(20, 8), default=0.0)
    replay_data_url = Column(String(255))  # URL to replay file
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    participants = relationship("MatchParticipant", back_populates="match")
    winner = relationship("Agent")

class MatchParticipant(Base):
    __tablename__ = "match_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # Performance Tracking
    starting_balance = Column(Numeric(20, 8), nullable=False)
    ending_balance = Column(Numeric(20, 8), default=0.0)
    total_trades = Column(Integer, default=0)
    profitable_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    
    # Metrics
    total_pnl = Column(Numeric(20, 8), default=0.0)
    return_percentage = Column(Numeric(10, 4), default=0.0)
    max_drawdown = Column(Numeric(10, 4), default=0.0)
    sharpe_ratio = Column(Numeric(10, 4), default=0.0)
    
    # Position Tracking
    current_positions = Column(JSON)  # Current open positions
    trade_history = Column(JSON)  # All trades executed
    
    # Status
    is_active = Column(Boolean, default=True)
    disqualification_reason = Column(String(100))
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    match = relationship("Match", back_populates="participants")
    agent = relationship("Agent", back_populates="match_participants")