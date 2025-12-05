from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
import json
import asyncio
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_user
from ..schemas.match import MatchCreate, MatchResponse, MatchParticipantResponse
from ..models.match import Match, MatchParticipant
from ..models.agent import Agent
from ..models.user import User
from ..services.simulation_engine import SimulationEngine
from ..services.websocket_manager import ws_manager

router = APIRouter()

@router.post("/", response_model=MatchResponse)
async def create_match(
    match_data: MatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify all agents exist and user has access
    for agent_id in match_data.agent_ids:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        # Check permissions
        if not agent.is_public and agent.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for agent {agent_id}"
            )
    
    # Create match
    db_match = Match(
        name=match_data.name,
        description=match_data.description,
        mode=match_data.mode,
        duration_minutes=match_data.duration_minutes,
        initial_balance=match_data.initial_balance,
        market_pairs=json.dumps(match_data.market_pairs),
        data_source="binance",  # Default data source
        total_ticks=int(match_data.duration_minutes * 60)  # 1 tick per second
    )
    
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    
    # Add participants
    for agent_id in match_data.agent_ids:
        participant = MatchParticipant(
            match_id=db_match.id,
            agent_id=agent_id,
            starting_balance=match_data.initial_balance
        )
        db.add(participant)
    
    db.commit()
    
    return db_match

@router.get("/", response_model=List[MatchResponse])
async def get_matches(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    mode_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Match)
    
    if status_filter:
        query = query.filter(Match.status == status_filter)
    
    if mode_filter:
        query = query.filter(Match.mode == mode_filter)
    
    matches = query.order_by(Match.created_at.desc()).offset(skip).limit(limit).all()
    return matches

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    return match

@router.get("/{match_id}/participants", response_model=List[MatchParticipantResponse])
async def get_match_participants(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    participants = db.query(MatchParticipant).filter(
        MatchParticipant.match_id == match_id
    ).all()
    
    return participants

@router.post("/{match_id}/start")
async def start_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    if match.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match already started or completed"
        )
    
    # Update match status
    match.status = "running"
    match.started_at = datetime.utcnow()
    db.commit()
    
    # Start simulation in background
    simulation_engine = SimulationEngine(db, ws_manager)
    asyncio.create_task(simulation_engine.run_match(match_id))
    
    return {"message": "Match started successfully", "match_id": match_id}

@router.post("/{match_id}/join")
async def join_match(
    match_id: int,
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    if match.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match already started or completed"
        )
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    if agent.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if already participating
    existing = db.query(MatchParticipant).filter(
        and_(MatchParticipant.match_id == match_id,
             MatchParticipant.agent_id == agent_id)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent already participating in this match"
        )
    
    # Add participant
    participant = MatchParticipant(
        match_id=match_id,
        agent_id=agent_id,
        starting_balance=match.initial_balance
    )
    db.add(participant)
    db.commit()
    
    return {"message": "Successfully joined match", "match_id": match_id, "agent_id": agent_id}

@router.get("/live/leaderboard")
async def get_live_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get active matches with current standings
    active_matches = db.query(Match).filter(Match.status == "running").all()
    
    leaderboard = []
    for match in active_matches:
        participants = db.query(MatchParticipant).filter(
            MatchParticipant.match_id == match.id
        ).all()
        
        match_data = {
            "match_id": match.id,
            "match_name": match.name,
            "participants": [
                {
                    "agent_id": p.agent_id,
                    "agent_name": p.agent.name,
                    "current_balance": float(p.ending_balance),
                    "total_pnl": float(p.total_pnl),
                    "return_percentage": float(p.return_percentage),
                    "total_trades": p.total_trades
                }
                for p in participants
            ]
        }
        leaderboard.append(match_data)
    
    return leaderboard