import aiohttp
import asyncio
import random
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime

class MarketDataProvider:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None

    async def _get_session(self):
        """Ensure an aiohttp session exists"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
            
    async def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current price for a symbol"""
        try:
            # Convert symbol format (BTC/USDT -> BTCUSDT)
            binance_symbol = symbol.replace("/", "")
            
            url = f"{self.base_url}/ticker/price"
            params = {"symbol": binance_symbol}
            
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return Decimal(data["price"])
                else:
                    # Return mock price if API fails
                    return self._get_mock_price(symbol)
                    
        except Exception as e:
            # Return mock price on error
            return self._get_mock_price(symbol)
            
    async def get_klines(self, symbol: str, interval: str = "1m", limit: int = 100):
        """Get kline/candlestick data"""
        try:
            binance_symbol = symbol.replace("/", "")
            
            url = f"{self.base_url}/klines"
            params = {
                "symbol": binance_symbol,
                "interval": interval,
                "limit": limit
            }
            
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {
                            "timestamp": kline[0],
                            "open": Decimal(kline[1]),
                            "high": Decimal(kline[2]),
                            "low": Decimal(kline[3]),
                            "close": Decimal(kline[4]),
                            "volume": Decimal(kline[5])
                        }
                        for kline in data
                    ]
                else:
                    return self._get_mock_klines(symbol, limit)
                    
        except Exception as e:
            return self._get_mock_klines(symbol, limit)
            
    async def get_orderbook(self, symbol: str, limit: int = 100):
        """Get orderbook data"""
        try:
            binance_symbol = symbol.replace("/", "")
            
            url = f"{self.base_url}/depth"
            params = {
                "symbol": binance_symbol,
                "limit": limit
            }
            
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "bids": [[Decimal(price), Decimal(qty)] for price, qty in data["bids"]],
                        "asks": [[Decimal(price), Decimal(qty)] for price, qty in data["asks"]]
                    }
                else:
                    return self._get_mock_orderbook(symbol)
                    
        except Exception as e:
            return self._get_mock_orderbook(symbol)
            
    async def get_ticker_24h(self, symbol: str):
        """Get 24hr ticker change statistics"""
        try:
            binance_symbol = symbol.replace("/", "")
            
            url = f"{self.base_url}/ticker/24hr"
            params = {"symbol": binance_symbol}
            
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "price_change": Decimal(data["priceChange"]),
                        "price_change_percent": Decimal(data["priceChangePercent"]),
                        "weighted_avg_price": Decimal(data["weightedAvgPrice"]),
                        "last_price": Decimal(data["lastPrice"]),
                        "volume": Decimal(data["volume"]),
                        "high_price": Decimal(data["highPrice"]),
                        "low_price": Decimal(data["lowPrice"])
                    }
                else:
                    return self._get_mock_ticker(symbol)
                    
        except Exception as e:
            return self._get_mock_ticker(symbol)
            
    def _get_mock_price(self, symbol: str) -> Decimal:
        """Get mock price for symbol"""
        mock_prices = {
            "BTC/USDT": Decimal("50000.00"),
            "ETH/USDT": Decimal("3000.00"),
            "ADA/USDT": Decimal("1.20"),
            "DOT/USDT": Decimal("25.00"),
            "LINK/USDT": Decimal("30.00"),
            "UNI/USDT": Decimal("20.00"),
            "MATIC/USDT": Decimal("1.50"),
            "AVAX/USDT": Decimal("80.00"),
            "SOL/USDT": Decimal("150.00"),
            "ATOM/USDT": Decimal("40.00")
        }
        return mock_prices.get(symbol, Decimal("100.00"))
        
    def _get_mock_klines(self, symbol: str, limit: int) -> list:
        """Generate mock kline data"""
        base_price = self._get_mock_price(symbol)
        klines = []
        
        for i in range(limit):
            timestamp = int(datetime.utcnow().timestamp() * 1000) - (i * 60000)
            
            # Generate random price movement
            change_percent = (random.random() - 0.5) * 0.02  # ±1%
            price = base_price * (1 + Decimal(change_percent))
            
            klines.append({
                "timestamp": timestamp,
                "open": price,
                "high": price * Decimal("1.001"),
                "low": price * Decimal("0.999"),
                "close": price,
                "volume": Decimal(random.uniform(10, 100))
            })
            
        return klines[::-1]  # Reverse to get chronological order
        
    def _get_mock_orderbook(self, symbol: str) -> Dict:
        """Generate mock orderbook data"""
        base_price = self._get_mock_price(symbol)
        
        bids = []
        asks = []
        
        for i in range(1, 101):
            # Bids (buy orders) - lower prices
            bid_price = base_price * (1 - Decimal(i) * Decimal("0.0001"))
            bid_quantity = Decimal(random.uniform(0.1, 2.0))
            bids.append([bid_price, bid_quantity])
            
            # Asks (sell orders) - higher prices
            ask_price = base_price * (1 + Decimal(i) * Decimal("0.0001"))
            ask_quantity = Decimal(random.uniform(0.1, 2.0))
            asks.append([ask_price, ask_quantity])
            
        return {"bids": bids, "asks": asks}
        
    def _get_mock_ticker(self, symbol: str) -> Dict:
        """Generate mock ticker data"""
        base_price = self._get_mock_price(symbol)
        change_percent = Decimal(random.uniform(-5, 5))
        
        return {
            "price_change": base_price * (change_percent / 100),
            "price_change_percent": change_percent,
            "weighted_avg_price": base_price,
            "last_price": base_price,
            "volume": Decimal(random.uniform(1000, 10000)),
            "high_price": base_price * Decimal("1.02"),
            "low_price": base_price * Decimal("0.98")
        }
        
    async def get_multiple_prices(self, symbols: list) -> Dict[str, Decimal]:
        """Get current prices for multiple symbols"""
        prices = {}
        
        # Use asyncio.gather for concurrent requests
        tasks = [self.get_current_price(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                prices[symbol] = self._get_mock_price(symbol)
            else:
                prices[symbol] = result
                
        return prices