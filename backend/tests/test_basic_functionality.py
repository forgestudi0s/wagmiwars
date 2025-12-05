"""
Basic functionality tests for WagmiWars platform
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import create_access_token, verify_token, get_password_hash
from app.models.user import User
from app.models.agent import Agent, AgentVersion
from app.models.match import Match, MatchParticipant
from app.services.simulation_engine import SimulationEngine
from app.services.websocket_manager import WebSocketManager
from app.services.web3_service import Web3Service

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_user(test_db):
    """Create a sample user for testing"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def sample_agent(test_db, sample_user):
    """Create a sample agent for testing"""
    agent = Agent(
        name="Test Agent",
        description="A test trading agent",
        owner_id=sample_user.id,
        strategy_type="moving_average",
        risk_tolerance="moderate",
        preferred_markets=["BTC/USDT", "ETH/USDT"]
    )
    test_db.add(agent)
    test_db.commit()
    test_db.refresh(agent)
    return agent

@pytest.fixture
def sample_match(test_db, sample_agent):
    """Create a sample match for testing"""
    match = Match(
        name="Test Match",
        mode="testing",
        duration_minutes=60,
        initial_balance=Decimal("10000.0"),
        market_pairs='["BTC/USDT", "ETH/USDT"]',
        data_source="binance"
    )
    test_db.add(match)
    test_db.commit()
    test_db.refresh(match)
    
    # Add participant
    participant = MatchParticipant(
        match_id=match.id,
        agent_id=sample_agent.id,
        starting_balance=Decimal("10000.0")
    )
    test_db.add(participant)
    test_db.commit()
    
    return match

# Authentication Tests
class TestAuthentication:
    
    def test_password_hashing(self):
        """Test password hashing functionality"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long
        
    def test_jwt_token_creation(self):
        """Test JWT token creation and verification"""
        data = {"sub": "testuser", "user_id": 1}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50
        
        # Verify token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == 1

# Database Tests
class TestDatabase:
    
    def test_user_creation(self, test_db, sample_user):
        """Test user creation and retrieval"""
        assert sample_user.id is not None
        assert sample_user.username == "testuser"
        assert sample_user.email == "test@example.com"
        assert sample_user.is_active is True
        
        # Test retrieval
        retrieved_user = test_db.query(User).filter(User.id == sample_user.id).first()
        assert retrieved_user is not None
        assert retrieved_user.username == sample_user.username
        
    def test_agent_creation(self, test_db, sample_agent, sample_user):
        """Test agent creation and relationships"""
        assert sample_agent.id is not None
        assert sample_agent.name == "Test Agent"
        assert sample_agent.owner_id == sample_user.id
        assert sample_agent.owner.username == "testuser"
        
    def test_match_creation(self, test_db, sample_match, sample_agent):
        """Test match creation and participant relationships"""
        assert sample_match.id is not None
        assert sample_match.name == "Test Match"
        assert sample_match.mode == "testing"
        
        # Test participant relationship
        participant = test_db.query(MatchParticipant).filter(
            MatchParticipant.match_id == sample_match.id
        ).first()
        
        assert participant is not None
        assert participant.agent_id == sample_agent.id
        assert participant.starting_balance == Decimal("10000.0")

# Service Tests
class TestServices:
    
    @pytest.mark.asyncio
    async def test_web3_service(self):
        """Test Web3 service functionality"""
        web3_service = Web3Service()
        
        # Test chain information
        chains = web3_service.get_supported_chains()
        assert len(chains) > 0
        assert 1 in chains  # Ethereum mainnet
        assert 137 in chains  # Polygon
        
        # Test exchange rate conversion
        rate = await web3_service.get_exchange_rate("USD", "ETH")
        assert rate > 0
        assert isinstance(rate, Decimal)
        
        # Test payment request creation
        payment_data = await web3_service.create_payment_request(
            transaction_id=1,
            amount=Decimal("0.01"),
            currency="ETH",
            chain_id=1,
            wallet_address="0x742d35Cc6634C0532925a3b8D4C0C8b3C2D4e6f8"
        )
        
        assert payment_data is not None
        assert "payment_url" in payment_data
        assert "qr_code" in payment_data
        
    @pytest.mark.asyncio
    async def test_websocket_manager(self):
        """Test WebSocket manager functionality"""
        manager = WebSocketManager()
        await manager.startup()
        
        # Test basic functionality
        assert manager.is_connected() is True
        
        # Test message broadcasting (mock)
        await manager.publish_match_update(1, {
            "tick": 100,
            "participants": []
        })
        
        await manager.shutdown()
        
    @pytest.mark.asyncio
    async def test_simulation_engine(self, test_db, sample_match):
        """Test simulation engine core functionality"""
        websocket_manager = WebSocketManager()
        engine = SimulationEngine(test_db, websocket_manager)
        
        # Test market data generation
        current_prices = {"BTC/USDT": Decimal("50000.0")}
        market_data = await engine._generate_market_data(current_prices, 1)
        
        assert market_data is not None
        assert "tick" in market_data
        assert "timestamp" in market_data
        assert "prices" in market_data
        assert "BTC/USDT" in market_data["prices"]
        
        await websocket_manager.shutdown()

# Integration Tests
class TestIntegration:
    
    def test_full_user_workflow(self, test_db):
        """Test complete user workflow"""
        # Create user
        user = User(
            username="workflowuser",
            email="workflow@example.com",
            hashed_password=get_password_hash("password123")
        )
        test_db.add(user)
        test_db.commit()
        
        # Create agent
        agent = Agent(
            name="Workflow Agent",
            owner_id=user.id,
            strategy_type="test",
            risk_tolerance="low"
        )
        test_db.add(agent)
        test_db.commit()
        
        # Create match
        match = Match(
            name="Workflow Test Match",
            mode="testing",
            duration_minutes=30
        )
        test_db.add(match)
        test_db.commit()
        
        # Add agent to match
        participant = MatchParticipant(
            match_id=match.id,
            agent_id=agent.id,
            starting_balance=Decimal("10000.0")
        )
        test_db.add(participant)
        test_db.commit()
        
        # Verify all relationships
        assert len(user.agents) == 1
        assert user.agents[0].id == agent.id
        assert len(match.participants) == 1
        assert match.participants[0].agent_id == agent.id
        
    def test_performance_metrics(self, test_db, sample_agent):
        """Test agent performance metrics calculation"""
        # Update agent with mock performance data
        sample_agent.total_matches = 10
        sample_agent.wins = 7
        sample_agent.losses = 3
        sample_agent.total_pnl = Decimal("1500.50")
        
        test_db.commit()
        
        # Calculate metrics
        win_rate = (sample_agent.wins / sample_agent.total_matches) * 100
        avg_return = sample_agent.total_pnl / sample_agent.total_matches
        
        assert win_rate == 70.0
        assert avg_return == Decimal("150.05")

# Performance Tests
class TestPerformance:
    
    def test_database_query_performance(self, test_db):
        """Test database query performance"""
        import time
        
        # Create multiple users
        users = []
        for i in range(100):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password=get_password_hash("password123")
            )
            users.append(user)
            test_db.add(user)
        
        test_db.commit()
        
        # Measure query performance
        start_time = time.time()
        retrieved_users = test_db.query(User).all()
        query_time = time.time() - start_time
        
        assert len(retrieved_users) == 101  # Including sample user
        assert query_time < 1.0  # Should complete in under 1 second
        
    @pytest.mark.asyncio
    async def test_simulation_performance(self, test_db):
        """Test simulation engine performance"""
        import time
        
        websocket_manager = WebSocketManager()
        engine = SimulationEngine(test_db, websocket_manager)
        
        # Test market data generation performance
        current_prices = {"BTC/USDT": Decimal("50000.0")}
        
        start_time = time.time()
        for i in range(100):
            await engine._generate_market_data(current_prices, i)
        generation_time = time.time() - start_time
        
        assert generation_time < 5.0  # Should generate 100 ticks in under 5 seconds
        
        await websocket_manager.shutdown()

if __name__ == "__main__":
    # Run tests
    pytest.main(["-v", __file__])