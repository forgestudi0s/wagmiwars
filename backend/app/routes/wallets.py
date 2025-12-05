from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_user
from ..schemas.wallet import WalletResponse, WalletCreate, WalletVerificationRequest
from ..models.wallet import Wallet
from ..models.user import User
from ..services.web3_service import Web3Service

router = APIRouter()

@router.post("/", response_model=WalletResponse)
async def add_wallet(
    wallet_data: WalletCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if wallet already exists
    existing = db.query(Wallet).filter(
        Wallet.address == wallet_data.address
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet already exists"
        )
    
    # Check if user already has a primary wallet
    existing_primary = db.query(Wallet).filter(
        Wallet.user_id == current_user.id,
        Wallet.is_primary == True
    ).first()
    
    # Set as primary if no other primary wallet exists
    is_primary = not existing_primary
    
    wallet = Wallet(
        user_id=current_user.id,
        address=wallet_data.address,
        chain_id=wallet_data.chain_id,
        chain_name=wallet_data.chain_name,
        wallet_type=wallet_data.wallet_type,
        nickname=wallet_data.nickname,
        is_primary=is_primary
    )
    
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    
    return wallet

@router.get("/", response_model=List[WalletResponse])
async def get_wallets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallets = db.query(Wallet).filter(
        Wallet.user_id == current_user.id
    ).order_by(Wallet.created_at.desc()).all()
    
    return wallets

@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    return wallet

@router.delete("/{wallet_id}")
async def delete_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    # Don't allow deletion of primary wallet if it's the only one
    if wallet.is_primary:
        other_wallets = db.query(Wallet).filter(
            Wallet.user_id == current_user.id,
            Wallet.id != wallet_id
        ).count()
        
        if other_wallets == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your only wallet"
            )
    
    db.delete(wallet)
    db.commit()
    
    return {"message": "Wallet deleted successfully"}

@router.post("/{wallet_id}/verify", response_model=WalletResponse)
async def verify_wallet(
    wallet_id: int,
    verification: WalletVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    # Verify wallet ownership using signature
    web3_service = Web3Service()
    is_valid = web3_service.verify_wallet_signature(
        wallet.address,
        verification.message,
        verification.signature
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    wallet.is_verified = True
    wallet.verification_message = verification.message
    wallet.verification_signature = verification.signature
    wallet.last_used_at = datetime.utcnow()
    
    db.commit()
    db.refresh(wallet)
    
    return wallet

@router.post("/{wallet_id}/set-primary", response_model=WalletResponse)
async def set_primary_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    # Remove primary status from all other wallets
    db.query(Wallet).filter(
        Wallet.user_id == current_user.id
    ).update({"is_primary": False})
    
    # Set this wallet as primary
    wallet.is_primary = True
    db.commit()
    db.refresh(wallet)
    
    return wallet

@router.get("/{wallet_id}/balance")
async def get_wallet_balance(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    web3_service = Web3Service()
    balance = await web3_service.get_wallet_balance(
        wallet.address,
        wallet.chain_id
    )
    
    return {
        "address": wallet.address,
        "chain": wallet.chain_name,
        "balance": balance
    }