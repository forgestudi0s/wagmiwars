from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from datetime import datetime

from ..core.database import get_db
from ..core.config import settings
from ..core.security import get_current_user
from ..schemas.crypto_transaction import CryptoTransactionResponse, CryptoPaymentRequest
from ..models.crypto_transaction import CryptoTransaction
from ..models.user import User
from ..services.web3_service import Web3Service

router = APIRouter()

@router.post("/payment", response_model=CryptoTransactionResponse)
async def create_crypto_payment(
    payment_request: CryptoPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not settings.PAYMENT_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payments are disabled in this environment"
        )

    web3_service = Web3Service()
    
    # Convert USD to crypto amount
    crypto_amount = await web3_service.convert_usd_to_crypto(
        payment_request.amount_usd,
        payment_request.currency
    )
    
    # Create payment transaction
    transaction = CryptoTransaction(
        user_id=current_user.id,
        transaction_hash="",  # Will be filled after payment
        wallet_address=payment_request.wallet_address,
        payment_type=payment_request.payment_type,
        amount_crypto=crypto_amount,
        amount_usd=payment_request.amount_usd,
        currency=payment_request.currency,
        chain_id=payment_request.chain_id,
        chain_name=web3_service.get_chain_name(payment_request.chain_id),
        match_id=payment_request.match_id,
        agent_id=payment_request.agent_id
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Generate payment request
    payment_data = await web3_service.create_payment_request(
        transaction_id=transaction.id,
        amount=crypto_amount,
        currency=payment_request.currency,
        chain_id=payment_request.chain_id,
        wallet_address=payment_request.wallet_address
    )
    
    return {
        "transaction": transaction,
        "payment_data": payment_data
    }

@router.get("/transactions", response_model=List[CryptoTransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transactions = db.query(CryptoTransaction).filter(
        CryptoTransaction.user_id == current_user.id
    ).order_by(CryptoTransaction.created_at.desc()).offset(skip).limit(limit).all()
    
    return transactions

@router.get("/transaction/{transaction_id}", response_model=CryptoTransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = db.query(CryptoTransaction).filter(
        CryptoTransaction.id == transaction_id,
        CryptoTransaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction

@router.post("/transaction/{transaction_id}/verify")
async def verify_transaction(
    transaction_id: int,
    transaction_hash: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not settings.PAYMENT_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payments are disabled in this environment"
        )

    transaction = db.query(CryptoTransaction).filter(
        CryptoTransaction.id == transaction_id,
        CryptoTransaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    web3_service = Web3Service()
    
    # Verify transaction on blockchain
    is_confirmed = await web3_service.verify_transaction(
        transaction_hash,
        transaction.chain_id
    )
    
    if is_confirmed:
        transaction.transaction_hash = transaction_hash
        transaction.status = "confirmed"
        transaction.confirmed_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Transaction verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction not found or not confirmed"
        )

@router.get("/supported-chains")
async def get_supported_chains():
    web3_service = Web3Service()
    return web3_service.get_supported_chains()

@router.get("/exchange-rate")
async def get_exchange_rate(
    from_currency: str = "USD",
    to_currency: str = "ETH"
):
    web3_service = Web3Service()
    rate = await web3_service.get_exchange_rate(from_currency, to_currency)
    return {"from": from_currency, "to": to_currency, "rate": rate}

@router.get("/payment-methods")
async def get_payment_methods():
    return {
        "arena_entry": {
            "name": "Arena Entry",
            "description": "Entry fee for arena matches",
            "default_amount_usd": 10.0
        },
        "agent_clone": {
            "name": "Agent Clone",
            "description": "Clone another agent with royalty",
            "default_amount_usd": 50.0
        },
        "sponsorship": {
            "name": "Agent Sponsorship",
            "description": "Sponsor an agent for visibility",
            "default_amount_usd": 100.0
        },
        "premium_features": {
            "name": "Premium Features",
            "description": "Access to premium platform features",
            "default_amount_usd": 25.0
        }
    }