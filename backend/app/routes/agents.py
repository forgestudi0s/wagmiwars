from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import json

from ..core.database import get_db
from ..core.config import settings
from ..core.security import get_current_user
from ..schemas.agent import AgentCreate, AgentResponse, AgentUpdate, AgentCloneRequest
from ..models.agent import Agent, AgentVersion
from ..models.user import User

router = APIRouter()

@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_agent = Agent(
        **agent_data.dict(),
        owner_id=current_user.id
    )
    
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    # Create initial version
    db_version = AgentVersion(
        agent_id=db_agent.id,
        version=1,
        config={},
        requirements=[]
    )
    db.add(db_version)
    db.commit()
    
    return db_agent

@router.get("/", response_model=List[AgentResponse])
async def get_agents(
    skip: int = 0,
    limit: int = 100,
    public_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Agent)
    
    if public_only:
        query = query.filter(Agent.is_public == True)
    else:
        # Show user's own agents + public agents
        query = query.filter(
            (Agent.owner_id == current_user.id) | (Agent.is_public == True)
        )
    
    agents = query.offset(skip).limit(limit).all()
    return agents

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check permissions
    if not agent.is_public and agent.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    
    # Update fields
    for field, value in agent_update.dict(exclude_unset=True).items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    
    return agent

@router.post("/{agent_id}/upload")
async def upload_agent_code(
    agent_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not settings.AGENT_UPLOAD_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent uploads are disabled in this environment"
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
    
    # TODO: Implement actual file upload and Docker image creation
    # For now, just create a new version
    latest_version = db.query(AgentVersion).filter(
        AgentVersion.agent_id == agent_id
    ).order_by(AgentVersion.version.desc()).first()
    
    new_version = AgentVersion(
        agent_id=agent_id,
        version=(latest_version.version + 1) if latest_version else 1,
        docker_image=f"wagmi-agent:{agent_id}-v{(latest_version.version + 1) if latest_version else 1}",
        config={},
        requirements=[]
    )
    
    db.add(new_version)
    agent.current_version = new_version.version
    db.commit()
    
    return {"message": "Agent code uploaded successfully", "version": new_version.version}

@router.post("/{agent_id}/clone", response_model=AgentResponse)
async def clone_agent(
    clone_request: AgentCloneRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    original_agent = db.query(Agent).filter(Agent.id == clone_request.agent_id).first()
    if not original_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    if not original_agent.is_clonable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent is not clonable"
        )
    
    # Create cloned agent
    cloned_agent = Agent(
        name=clone_request.new_name,
        description=f"Cloned from {original_agent.name}",
        owner_id=current_user.id,
        strategy_type=original_agent.strategy_type,
        risk_tolerance=original_agent.risk_tolerance,
        preferred_markets=original_agent.preferred_markets,
        is_public=clone_request.is_public
    )
    
    db.add(cloned_agent)
    db.commit()
    db.refresh(cloned_agent)
    
    # Handle royalty payment if applicable
    if original_agent.royalty_percentage > 0 and original_agent.clone_price > 0:
        # TODO: Implement royalty payment logic
        pass
    
    return cloned_agent

@router.get("/my/stats")
async def get_my_agent_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    agents = db.query(Agent).filter(Agent.owner_id == current_user.id).all()
    
    total_agents = len(agents)
    total_matches = sum(agent.total_matches for agent in agents)
    total_wins = sum(agent.wins for agent in agents)
    total_pnl = sum(agent.total_pnl for agent in agents)
    
    return {
        "total_agents": total_agents,
        "total_matches": total_matches,
        "total_wins": total_wins,
        "win_rate": (total_wins / total_matches * 100) if total_matches > 0 else 0,
        "total_pnl": total_pnl
    }