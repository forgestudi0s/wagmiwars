from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class MatchCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    mode: str = Field(..., regex="^(testing|demo|production)$")
    duration_minutes: int = Field(default=60, ge=1, le=480)
    initial_balance: Decimal = Field(default=10000.0, gt=0)
    market_pairs: List[str] = Field(..., min_items=1)
    agent_ids: List[int] = Field(..., min_items=1, max_items=10)

class MatchResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    mode: str
    duration_minutes: int
    initial_balance: Decimal
    market_pairs: List[str]
    data_source: Optional[str] = None
    status: str
    current_tick: int
    total_ticks: int
    winner_id: Optional[int] = None
    total_volume: Decimal
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MatchParticipantResponse(BaseModel):
    id: int
    match_id: int
    agent_id: int
    starting_balance: Decimal
    ending_balance: Decimal
    total_trades: int
    profitable_trades: int
    losing_trades: int
    total_pnl: Decimal
    return_percentage: Decimal
    max_drawdown: Decimal
    sharpe_ratio: Decimal
    is_active: bool
    
    class Config:
        from_attributes = True

class MatchJoinRequest(BaseModel):
    agent_id: int

class MatchStartRequest(BaseModel):
    match_id: int