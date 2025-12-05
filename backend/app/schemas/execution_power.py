from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ExecutionPowerRequest(BaseModel):
    max_position_size: Decimal = Field(..., gt=0)
    max_daily_loss: Decimal = Field(..., gt=0)
    can_trade_spot: bool = False
    can_trade_futures: bool = False
    can_trade_options: bool = False
    can_use_leverage: bool = False
    max_leverage: Decimal = Field(default=1.0, ge=1, le=100)

class ExecutionPowerResponse(BaseModel):
    id: int
    user_id: int
    level: int
    max_position_size: Decimal
    max_daily_loss: Decimal
    max_monthly_loss: Decimal
    can_trade_spot: bool
    can_trade_futures: bool
    can_trade_options: bool
    can_use_leverage: bool
    max_leverage: Decimal
    approval_status: str
    risk_score: Decimal
    kyc_verified: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True