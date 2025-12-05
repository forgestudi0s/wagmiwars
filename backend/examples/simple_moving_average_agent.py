"""
Simple Moving Average Trading Agent for WagmiWars
A basic implementation demonstrating how to create a trading agent.
"""

import asyncio
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

class SimpleMovingAverageAgent:
    """
    A simple moving average crossover strategy agent.
    Buys when short MA crosses above long MA, sells when it crosses below.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.agent_id = config.get('agent_id')
        self.api_key = config.get('api_key')
        self.api_url = config.get('api_url', 'http://localhost:8000')
        
        # Trading parameters
        self.short_ma_period = config.get('short_ma_period', 20)
        self.long_ma_period = config.get('long_ma_period', 50)
        self.risk_per_trade = config.get('risk_per_trade', 0.02)  # 2% risk per trade
        self.stop_loss_pct = config.get('stop_loss_pct', 0.05)  # 5% stop loss
        self.take_profit_pct = config.get('take_profit_pct', 0.10)  # 10% take profit
        
        # State
        self.price_history: List[Decimal] = []
        self.positions: Dict[str, Dict] = {}
        self.balance = Decimal(config.get('initial_balance', '10000.0'))
        self.is_running = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f'Agent-{self.agent_id}')
        
    async def start(self):
        """Start the agent and connect to the simulation"""
        self.is_running = True
        self.logger.info(f"Starting agent {self.agent_id}")
        
        try:
            # Connect to WebSocket for real-time market data
            await self.connect_to_simulation()
            
            # Main trading loop
            while self.is_running:
                await self.trading_loop()
                await asyncio.sleep(1)  # Check every second
                
        except Exception as e:
            self.logger.error(f"Agent error: {e}")
        finally:
            await self.stop()
            
    async def stop(self):
        """Stop the agent"""
        self.is_running = False
        self.logger.info(f"Stopping agent {self.agent_id}")
        
    async def connect_to_simulation(self):
        """Connect to the simulation engine via WebSocket"""
        # In a real implementation, this would connect to the WebSocket
        # and subscribe to market data for the relevant trading pairs
        self.logger.info("Connected to simulation engine")
        
    async def trading_loop(self):
        """Main trading loop - process market data and make decisions"""
        try:
            # Get latest market data (mock implementation)
            market_data = await self.get_market_data()
            
            if market_data:
                await self.process_market_data(market_data)
                
                # Make trading decisions
                decision = await self.make_trading_decision()
                
                if decision:
                    await self.execute_trade(decision)
                    
        except Exception as e:
            self.logger.error(f"Error in trading loop: {e}")
            
    async def get_market_data(self) -> Optional[Dict]:
        """Get latest market data from simulation"""
        # Mock market data - in production this would come from WebSocket
        import random
        
        current_price = Decimal(str(random.uniform(45000, 55000)))  # BTC price
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'symbol': 'BTC/USDT',
            'price': current_price,
            'volume': random.uniform(100, 1000),
            'spread': Decimal('0.01')
        }
        
    async def process_market_data(self, market_data: Dict):
        """Process incoming market data and update indicators"""
        price = Decimal(str(market_data['price']))
        self.price_history.append(price)
        
        # Keep only the last N prices for memory efficiency
        max_history = max(self.short_ma_period, self.long_ma_period) * 2
        if len(self.price_history) > max_history:
            self.price_history = self.price_history[-max_history:]
            
        self.logger.debug(f"Price update: {price}")
        
    async def make_trading_decision(self) -> Optional[Dict]:
        """Make trading decision based on technical analysis"""
        if len(self.price_history) < self.long_ma_period:
            return None  # Not enough data
            
        # Calculate moving averages
        short_ma = self.calculate_sma(self.short_ma_period)
        long_ma = self.calculate_sma(self.long_ma_period)
        
        current_price = self.price_history[-1]
        symbol = 'BTC/USDT'
        
        # Check for crossover signals
        if len(self.price_history) >= self.long_ma_period + 1:
            prev_short_ma = self.calculate_sma(self.short_ma_period, offset=1)
            prev_long_ma = self.calculate_sma(self.long_ma_period, offset=1)
            
            # Buy signal: short MA crosses above long MA
            if prev_short_ma <= prev_long_ma and short_ma > long_ma:
                if symbol not in self.positions:
                    return {
                        'action': 'buy',
                        'symbol': symbol,
                        'price': current_price,
                        'quantity': self.calculate_position_size(current_price),
                        'reason': 'MA crossover buy signal'
                    }
                    
            # Sell signal: short MA crosses below long MA
            elif prev_short_ma >= prev_long_ma and short_ma < long_ma:
                if symbol in self.positions:
                    return {
                        'action': 'sell',
                        'symbol': symbol,
                        'price': current_price,
                        'quantity': self.positions[symbol]['quantity'],
                        'reason': 'MA crossover sell signal'
                    }
                    
        # Check stop loss and take profit
        if symbol in self.positions:
            position = self.positions[symbol]
            entry_price = position['entry_price']
            
            # Stop loss
            if current_price <= entry_price * (1 - self.stop_loss_pct):
                return {
                    'action': 'sell',
                    'symbol': symbol,
                    'price': current_price,
                    'quantity': position['quantity'],
                    'reason': 'Stop loss triggered'
                }
                
            # Take profit
            if current_price >= entry_price * (1 + self.take_profit_pct):
                return {
                    'action': 'sell',
                    'symbol': symbol,
                    'price': current_price,
                    'quantity': position['quantity'],
                    'reason': 'Take profit triggered'
                }
                
        return None
        
    def calculate_sma(self, period: int, offset: int = 0) -> Decimal:
        """Calculate Simple Moving Average"""
        if len(self.price_history) < period + offset:
            return Decimal('0')
            
        prices = self.price_history[-(period + offset):-offset if offset > 0 else None]
        return sum(prices) / len(prices)
        
    def calculate_position_size(self, price: Decimal) -> Decimal:
        """Calculate position size based on risk management"""
        risk_amount = self.balance * Decimal(str(self.risk_per_trade))
        stop_loss_amount = price * Decimal(str(self.stop_loss_pct))
        
        if stop_loss_amount > 0:
            return risk_amount / stop_loss_amount
        return Decimal('0.001')  # Minimum position size
        
    async def execute_trade(self, decision: Dict):
        """Execute a trading decision"""
        action = decision['action']
        symbol = decision['symbol']
        price = decision['price']
        quantity = decision['quantity']
        reason = decision['reason']
        
        if action == 'buy':
            # Calculate total cost including fees (mock 0.1% fee)
            total_cost = price * quantity * Decimal('1.001')
            
            if total_cost <= self.balance:
                # Execute buy
                self.balance -= total_cost
                self.positions[symbol] = {
                    'quantity': quantity,
                    'entry_price': price,
                    'entry_time': datetime.utcnow().isoformat(),
                    'reason': reason
                }
                
                self.logger.info(f"BUY {quantity} {symbol} @ {price} - {reason}")
                self.logger.info(f"Remaining balance: {self.balance}")
            else:
                self.logger.warning(f"Insufficient balance for buy order. Required: {total_cost}, Available: {self.balance}")
                
        elif action == 'sell':
            if symbol in self.positions:
                # Calculate total revenue including fees (mock 0.1% fee)
                total_revenue = price * quantity * Decimal('0.999')
                
                # Execute sell
                self.balance += total_revenue
                position = self.positions.pop(symbol)
                
                # Calculate PnL
                entry_cost = position['entry_price'] * quantity
                pnl = total_revenue - entry_cost
                
                self.logger.info(f"SELL {quantity} {symbol} @ {price} - {reason}")
                self.logger.info(f"PnL: {pnl}, New balance: {self.balance}")
                
                # Report performance to simulation engine
                await self.report_trade_performance({
                    'symbol': symbol,
                    'action': 'sell',
                    'entry_price': position['entry_price'],
                    'exit_price': price,
                    'quantity': quantity,
                    'pnl': pnl,
                    'balance': self.balance
                })
                
    async def report_trade_performance(self, trade_data: Dict):
        """Report trade performance back to simulation engine"""
        # In production, this would send data via API or WebSocket
        self.logger.info(f"Performance report: {trade_data}")
        
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics"""
        total_value = self.balance
        
        # Add value of open positions
        for symbol, position in self.positions.items():
            # Mock current price (in production, get from market data)
            current_price = position['entry_price']  # Simplified
            total_value += current_price * position['quantity']
            
        initial_balance = Decimal(str(self.config.get('initial_balance', '10000.0')))
        total_pnl = total_value - initial_balance
        total_return = (total_pnl / initial_balance) * 100
        
        return {
            'balance': float(self.balance),
            'total_value': float(total_value),
            'total_pnl': float(total_pnl),
            'total_return': float(total_return),
            'open_positions': len(self.positions),
            'is_running': self.is_running
        }
        
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'is_running': self.is_running,
            'balance': float(self.balance),
            'open_positions': list(self.positions.keys()),
            'price_history_length': len(self.price_history),
            'config': self.config
        }


# Example usage and testing
async def main():
    """Example usage of the SimpleMovingAverageAgent"""
    
    # Agent configuration
    config = {
        'agent_id': 'sma_agent_001',
        'api_key': 'your_api_key_here',
        'initial_balance': '10000.0',
        'short_ma_period': 20,
        'long_ma_period': 50,
        'risk_per_trade': 0.02,
        'stop_loss_pct': 0.05,
        'take_profit_pct': 0.10
    }
    
    # Create and start agent
    agent = SimpleMovingAverageAgent(config)
    
    try:
        # Run for a limited time for demonstration
        task = asyncio.create_task(agent.start())
        
        # Let it run for 30 seconds
        await asyncio.sleep(30)
        
        # Stop the agent
        await agent.stop()
        
        # Print final performance
        performance = agent.get_performance_metrics()
        print(f"\nFinal Performance:")
        print(f"Balance: ${performance['balance']:.2f}")
        print(f"Total Value: ${performance['total_value']:.2f}")
        print(f"Total PnL: ${performance['total_pnl']:.2f}")
        print(f"Total Return: {performance['total_return']:.2f}%")
        
    except KeyboardInterrupt:
        print("\nStopping agent...")
        await agent.stop()
    except Exception as e:
        print(f"Error: {e}")
        await agent.stop()


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())