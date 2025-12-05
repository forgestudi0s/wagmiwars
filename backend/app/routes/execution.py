from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..core.database import get_db
from ..core.config import settings
from ..core.security import get_current_user
from ..schemas.execution_power import ExecutionPowerResponse, ExecutionPowerRequest
from ..models.execution_power import ExecutionPower
from ..models.user import User

router = APIRouter()

@router.post("/request", response_model=ExecutionPowerResponse)
async def request_execution_power(
    request: ExecutionPowerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not settings.EXECUTION_POWER_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Execution power requests are disabled"
        )

    # Check if user already has execution power
    existing = db.query(ExecutionPower).filter(
        ExecutionPower.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Execution power request already exists"
        )
    
    # Create new execution power request
    execution_power = ExecutionPower(
        user_id=current_user.id,
        max_position_size=request.max_position_size,
        max_daily_loss=request.max_daily_loss,
        can_trade_spot=request.can_trade_spot,
        can_trade_futures=request.can_trade_futures,
        can_trade_options=request.can_trade_options,
        can_use_leverage=request.can_use_leverage,
        max_leverage=request.max_leverage
    )
    
    db.add(execution_power)
    db.commit()
    db.refresh(execution_power)
    
    return execution_power

@router.get("/status", response_model=ExecutionPowerResponse)
async def get_execution_power_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not settings.EXECUTION_POWER_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Execution power is disabled"
        )

    execution_power = db.query(ExecutionPower).filter(
        ExecutionPower.user_id == current_user.id
    ).first()
    
    if not execution_power:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No execution power found for user"
        )
    
    return execution_power

@router.get("/admin/pending", response_model=List[ExecutionPowerResponse])
async def get_pending_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.username not in settings.ADMIN_USERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    if not settings.EXECUTION_POWER_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Execution power is disabled"
        )

    pending_requests = db.query(ExecutionPower).filter(
        ExecutionPower.approval_status == "pending"
    ).all()
    
    return pending_requests

@router.post("/admin/approve/{request_id}")
async def approve_execution_power(
    request_id: int,
    level: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.username not in settings.ADMIN_USERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    if not settings.EXECUTION_POWER_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Execution power is disabled"
        )
    execution_power = db.query(ExecutionPower).filter(
        ExecutionPower.id == request_id
    ).first()
    
    if not execution_power:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution power request not found"
        )
    
    if execution_power.approval_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request already processed"
        )
    
    # Approve request
    execution_power.approval_status = "approved"
    execution_power.level = level
    execution_power.approved_by = current_user.username
    execution_power.approved_at = datetime.utcnow()
    
    # Update user execution power level
    user = db.query(User).filter(User.id == execution_power.user_id).first()
    if user:
        user.execution_power_level = level
        user.max_position_size = execution_power.max_position_size
        user.max_daily_loss = execution_power.max_daily_loss
    
    db.commit()
    
    return {"message": "Execution power approved successfully"}

@router.get("/limits")
async def get_execution_limits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not settings.EXECUTION_POWER_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Execution power is disabled"
        )
    return {
        "max_position_size": current_user.max_position_size,
        "max_daily_loss": current_user.max_daily_loss,
        "execution_power_level": current_user.execution_power_level
    }