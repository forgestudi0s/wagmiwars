from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_premium: bool
    execution_power_level: int
    max_position_size: Decimal
    max_daily_loss: Decimal
    created_at: datetime
    last_login: Optional[datetime]
    total_matches: Optional[int] = 0
    total_wins: Optional[int] = 0
    total_pnl: Optional[Decimal] = Decimal(0)
    
    class Config:
        from_attributes = True