from typing import Dict, Optional, Any
from decimal import Decimal
import aiohttp
from datetime import datetime, timedelta

from ..core.config import settings

class Web3Service:
    def __init__(self):
        self.infura_url = f"https://mainnet.infura.io/v3/{settings.INFURA_PROJECT_ID}"
        self.alchemy_url = f"https://eth-mainnet.alchemyapi.io/v2/{settings.ALCHEMY_API_KEY}"
        
        # Supported chains
        self.chains = {
            1: {
                "name": "ethereum",
                "rpc_url": self.infura_url,
                "currency": "ETH",
                "explorer": "https://etherscan.io"
            },
            137: {
                "name": "polygon",
                "rpc_url": "https://polygon-rpc.com",
                "currency": "MATIC",
                "explorer": "https://polygonscan.com"
            },
            8453: {
                "name": "base",
                "rpc_url": "https://mainnet.base.org",
                "currency": "ETH",
                "explorer": "https://basescan.org"
            },
            42161: {
                "name": "arbitrum",
                "rpc_url": "https://arb1.arbitrum.io/rpc",
                "currency": "ETH",
                "explorer": "https://arbiscan.io"
            }
        }
        
    def get_chain_name(self, chain_id: int) -> str:
        """Get chain name from chain ID"""
        return self.chains.get(chain_id, {}).get("name", "unknown")
        
    def get_supported_chains(self) -> Dict:
        """Get list of supported chains"""
        return {
            chain_id: {
                "name": chain["name"],
                "currency": chain["currency"],
                "explorer": chain["explorer"]
            }
            for chain_id, chain in self.chains.items()
        }
        
    async def convert_usd_to_crypto(self, usd_amount: Decimal, currency: str) -> Decimal:
        """Convert USD amount to crypto amount"""
        exchange_rate = await self.get_exchange_rate("USD", currency)
        return Decimal(usd_amount) / exchange_rate
        
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """Get exchange rate between currencies"""
        # Mock exchange rates for demo
        mock_rates = {
            ("USD", "ETH"): Decimal("2500.00"),
            ("USD", "USDC"): Decimal("1.00"),
            ("USD", "USDT"): Decimal("1.00"),
            ("USD", "DAI"): Decimal("1.00"),
            ("USD", "MATIC"): Decimal("0.80"),
        }
        
        rate = mock_rates.get((from_currency.upper(), to_currency.upper()))
        if rate:
            return rate
            
        # Try reverse rate
        reverse_rate = mock_rates.get((to_currency.upper(), from_currency.upper()))
        if reverse_rate:
            return Decimal("1") / reverse_rate
            
        # Default fallback
        return Decimal("1.00")
        
    async def create_payment_request(self, transaction_id: int, amount: Decimal, 
                                   currency: str, chain_id: int, wallet_address: str) -> Dict:
        """Create a payment request"""
        payment_data = {
            "transaction_id": transaction_id,
            "amount": str(amount),
            "currency": currency,
            "chain_id": chain_id,
            "wallet_address": wallet_address,
            "payment_url": f"ethereum:{wallet_address}?amount={amount}",
            "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=ethereum:{wallet_address}?amount={amount}",
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        return payment_data
        
    async def verify_transaction(self, tx_hash: str, chain_id: int) -> bool:
        """Verify transaction on blockchain"""
        # Mock verification for demo
        # In production, this would call the actual blockchain
        return True
        
    def verify_wallet_signature(self, wallet_address: str, message: str, signature: str) -> bool:
        """Verify wallet signature"""
        # Mock signature verification for demo
        # In production, this would use web3.py to verify the signature
        return len(signature) > 10 and wallet_address.startswith("0x")
        
    async def get_wallet_balance(self, wallet_address: str, chain_id: int) -> Dict:
        """Get wallet balance"""
        chain = self.chains.get(chain_id)
        if not chain:
            raise ValueError(f"Unsupported chain ID: {chain_id}")
            
        # Mock balance for demo
        # In production, this would call the blockchain
        return {
            "address": wallet_address,
            "chain": chain["name"],
            "native_balance": "1.5",
            "token_balances": {
                "USDC": "1000.00",
                "USDT": "500.00",
                "DAI": "250.00"
            }
        }
        
    async def monitor_transaction(self, tx_hash: str, chain_id: int) -> Dict:
        """Monitor transaction status"""
        # Mock monitoring for demo
        return {
            "hash": tx_hash,
            "status": "confirmed",
            "confirmations": 6,
            "block_number": 18500000,
            "gas_used": 21000,
            "effective_gas_price": "20000000000"
        }