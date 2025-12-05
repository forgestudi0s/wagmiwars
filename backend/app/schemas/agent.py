from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    strategy_type: Optional[str] = None
    risk_tolerance: Optional[str] = None
    preferred_markets: Optional[List[str]] = []

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_clonable: Optional[bool] = None
    clone_price: Optional[Decimal] = None
    royalty_percentage: Optional[Decimal] = Field(None, ge=0, le=100)

class AgentResponse(AgentBase):
    id: int
    owner_id: int
    total_matches: int
    wins: int
    losses: int
    total_pnl: Decimal
    avg_return: Decimal
    sharpe_ratio: Decimal
    max_drawdown: Decimal
    is_public: bool
    is_clonable: bool
    clone_price: Decimal
    royalty_percentage: Decimal
    current_version: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class AgentVersionResponse(BaseModel):
    id: int
    agent_id: int
    version: int
    docker_image: Optional[str] = None
    changelog: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AgentCloneRequest(BaseModel):
    agent_id: int
    new_name: str
    is_public: bool = False