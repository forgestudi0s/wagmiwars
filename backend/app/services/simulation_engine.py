import asyncio
import json
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy.orm import Session, sessionmaker

from ..core.config import settings
from ..models.agent import Agent
from ..models.match import Match, MatchParticipant
from .market_data_provider import MarketDataProvider
from .websocket_manager import WebSocketManager

class SimulationEngine:
    def __init__(self, db_or_factory: Session | sessionmaker, websocket_manager: WebSocketManager):
        # Always use a session factory to avoid using request-scoped sessions in background tasks
        if isinstance(db_or_factory, sessionmaker):
            self.session_factory = db_or_factory
        else:
            self.session_factory = sessionmaker(
                bind=db_or_factory.get_bind(),
                autocommit=False,
                autoflush=False,
            )
        self.websocket_manager = websocket_manager
        self.market_data_provider = MarketDataProvider()
        self.active_simulations: Dict[int, asyncio.Task] = {}

    async def run_match(self, match_id: int):
        """Run a complete match simulation using a dedicated DB session"""
        session: Session = self.session_factory()
        try:
            match = session.query(Match).filter(Match.id == match_id).first()
            if not match:
                return

            participants = session.query(MatchParticipant).filter(
                MatchParticipant.match_id == match_id
            ).all()

            # Initialize match data
            market_pairs = json.loads(match.market_pairs)
            current_prices = await self._get_initial_prices(market_pairs)

            # Start simulation loop
            for tick in range(match.current_tick, match.total_ticks):
                if match.status != "running":
                    break

                # Update match tick
                match.current_tick = tick

                # Generate market data for this tick
                market_data = await self._generate_market_data(current_prices, tick)

                # Send market data to all agents
                await self._send_market_data_to_agents(participants, market_data)

                # Collect agent decisions (mock for now)
                agent_decisions = await self._collect_agent_decisions(participants)

                # Process trades
                await self._process_trades(participants, agent_decisions, market_data)

                # Update participant balances and metrics
                await self._update_participant_metrics(participants, market_data)

                # Send updates via WebSocket
                await self._broadcast_match_update(match, participants, market_data)

                # Small delay between ticks
                await asyncio.sleep(settings.SIMULATION_TICK_INTERVAL)

                # Commit changes to database
                session.commit()

            # Match completed
            match.status = "completed"
            match.completed_at = datetime.utcnow()

            # Determine winner
            winner = max(participants, key=lambda p: p.ending_balance)
            match.winner_id = winner.agent_id

            session.commit()

            # Final update
            await self._broadcast_match_completed(session, match, participants)
        finally:
            session.close()
        
    async def _get_initial_prices(self, market_pairs: List[str]) -> Dict[str, Decimal]:
        """Get initial market prices"""
        prices = {}
        for pair in market_pairs:
            # Get real market data or use mock
            price = await self.market_data_provider.get_current_price(pair)
            prices[pair] = price or Decimal("50000.00")  # Default BTC price
        return prices
        
    async def _generate_market_data(self, current_prices: Dict[str, Decimal], tick: int) -> Dict:
        """Generate market data for a tick"""
        market_data = {
            "tick": tick,
            "timestamp": datetime.utcnow().isoformat(),
            "prices": {}
        }
        
        for pair, price in current_prices.items():
            # Simulate small price movements
            volatility = Decimal("0.001")  # 0.1% volatility per tick
            change = (Decimal(random.uniform(-1, 1)) * volatility * price)
            new_price = max(price + change, Decimal("0.01"))
            
            market_data["prices"][pair] = {
                "open": price,
                "high": max(price, new_price),
                "low": min(price, new_price),
                "close": new_price,
                "volume": Decimal(random.uniform(100, 1000))
            }
            
            # Update current price
            current_prices[pair] = new_price
            
        return market_data
        
    async def _send_market_data_to_agents(self, participants: List[MatchParticipant], market_data: Dict):
        """Send market data to agent containers"""
        for participant in participants:
            if participant.is_active:
                # TODO: Send to actual agent container via API
                pass
                
    async def _collect_agent_decisions(self, participants: List[MatchParticipant]) -> Dict[int, List[Dict]]:
        """Collect trading decisions from agents"""
        decisions = {}
        
        for participant in participants:
            if participant.is_active:
                # Mock agent decisions for now
                decisions[participant.id] = []
                
                # Randomly decide to trade
                if random.random() < 0.1:  # 10% chance per tick
                    action = random.choice(["buy", "sell"])
                    pair = random.choice(["BTC/USDT", "ETH/USDT"])
                    size = Decimal(random.uniform(0.001, 0.1))
                    
                    decisions[participant.id].append({
                        "action": action,
                        "pair": pair,
                        "size": size,
                        "participant_id": participant.id
                    })
                    
        return decisions
        
    async def _process_trades(self, participants: List[MatchParticipant], decisions: Dict, market_data: Dict):
        """Process agent trading decisions"""
        for participant_id, trades in decisions.items():
            participant = next(p for p in participants if p.id == participant_id)
            
            for trade in trades:
                pair = trade["pair"]
                price = market_data["prices"][pair]["close"]
                size = trade["size"]
                
                if trade["action"] == "buy":
                    cost = size * price
                    if participant.ending_balance >= cost:
                        participant.ending_balance -= cost
                        # Add to positions (simplified)
                        if not participant.current_positions:
                            participant.current_positions = {}
                        participant.current_positions[pair] = size
                        
                elif trade["action"] == "sell":
                    # Check if agent has position
                    if participant.current_positions and pair in participant.current_positions:
                        revenue = participant.current_positions[pair] * price
                        participant.ending_balance += revenue
                        del participant.current_positions[pair]
                
                participant.total_trades += 1
                
    async def _update_participant_metrics(self, participants: List[MatchParticipant], market_data: Dict):
        """Update participant performance metrics"""
        for participant in participants:
            # Calculate PnL
            participant.total_pnl = participant.ending_balance - participant.starting_balance
            participant.return_percentage = (participant.total_pnl / participant.starting_balance) * 100
            
            # Update trade counts
            if participant.total_trades > 0:
                # Mock profitable/losing trades
                participant.profitable_trades = int(participant.total_trades * 0.6)  # 60% win rate
                participant.losing_trades = participant.total_trades - participant.profitable_trades
                
    async def _broadcast_match_update(self, match: Match, participants: List[MatchParticipant], market_data: Dict):
        """Broadcast match update via WebSocket"""
        update_data = {
            "match_id": match.id,
            "tick": match.current_tick,
            "total_ticks": match.total_ticks,
            "market_data": market_data,
            "participants": [
                {
                    "id": p.id,
                    "agent_id": p.agent_id,
                    "agent_name": p.agent.name,
                    "balance": float(p.ending_balance),
                    "pnl": float(p.total_pnl),
                    "return_percentage": float(p.return_percentage),
                    "total_trades": p.total_trades
                }
                for p in participants
            ]
        }
        
        await self.websocket_manager.publish_match_update(match.id, update_data)
        
    async def _broadcast_match_completed(self, session: Session, match: Match, participants: List[MatchParticipant]):
        """Broadcast match completion"""
        winner = max(participants, key=lambda p: p.ending_balance)
        
        completion_data = {
            "match_id": match.id,
            "winner_id": winner.agent_id,
            "winner_name": winner.agent.name,
            "final_standings": [
                {
                    "agent_id": p.agent_id,
                    "agent_name": p.agent.name,
                    "final_balance": float(p.ending_balance),
                    "total_pnl": float(p.total_pnl),
                    "return_percentage": float(p.return_percentage),
                    "total_trades": p.total_trades
                }
                for p in sorted(participants, key=lambda p: p.ending_balance, reverse=True)
            ]
        }
        
        await self.websocket_manager.publish_match_update(match.id, completion_data)

        # Update leaderboard
        await self._update_leaderboard(session)

    async def _update_leaderboard(self, session: Session):
        """Update global leaderboard"""
        # Get top agents by performance
        top_agents = session.query(Agent).order_by(
            Agent.total_pnl.desc()
        ).limit(10).all()
        
        leaderboard_data = [
            {
                "agent_id": agent.id,
                "agent_name": agent.name,
                "owner_name": agent.owner.username,
                "total_pnl": float(agent.total_pnl),
                "total_matches": agent.total_matches,
                "win_rate": (agent.wins / agent.total_matches * 100) if agent.total_matches > 0 else 0
            }
            for agent in top_agents
        ]
        
        await self.websocket_manager.publish_leaderboard_update({
            "top_agents": leaderboard_data,
            "updated_at": datetime.utcnow().isoformat()
        })