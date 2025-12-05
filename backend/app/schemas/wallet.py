from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WalletCreate(BaseModel):
    address: str = Field(..., regex="^0x[a-fA-F0-9]{40}$")
    chain_id: int = Field(default=1)
    chain_name: str = Field(default="ethereum")
    wallet_type: str = Field(default="metamask")
    nickname: Optional[str] = None

class WalletResponse(BaseModel):
    id: int
    user_id: int
    address: str
    chain_id: int
    chain_name: str
    wallet_type: str
    is_verified: bool
    is_primary: bool
    nickname: Optional[str] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class WalletVerificationRequest(BaseModel):
    address: str
    message: str
    signature: str