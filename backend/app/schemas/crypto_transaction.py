from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class CryptoTransactionResponse(BaseModel):
    id: int
    user_id: int
    transaction_hash: str
    wallet_address: str
    payment_type: str
    amount_crypto: Decimal
    amount_usd: Decimal
    currency: str
    chain_id: int
    chain_name: str
    status: str
    confirmations: int
    match_id: Optional[int] = None
    agent_id: Optional[int] = None
    sponsorship_id: Optional[int] = None
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CryptoPaymentRequest(BaseModel):
    payment_type: str
    amount_usd: Decimal
    currency: str
    chain_id: int
    wallet_address: str
    match_id: Optional[int] = None
    agent_id: Optional[int] = None