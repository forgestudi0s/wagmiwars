from typing import List, Optional

from pydantic import AnyHttpUrl, Field, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "WagmiWars"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    ALLOWED_HOSTS: List[str] = ["*"]

    # Database
    DATABASE_URL: str = "postgresql://wagmi:wagmi123@localhost/wagmiwars_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_POOL_SIZE: int = 10

    # Security
    SECRET_KEY: str = Field(
        default="CHANGE_ME_SUPER_SECRET_KEY_32_CHARS_MIN",
        min_length=32,
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # Simple login rate limiting (per IP/username)
    LOGIN_RATE_LIMIT: int = 10
    LOGIN_RATE_WINDOW_SECONDS: int = 60

    # Web3/Crypto
    INFURA_PROJECT_ID: Optional[str] = None
    ALCHEMY_API_KEY: Optional[str] = None
    ETHERSCAN_API_KEY: Optional[str] = None

    # Exchange APIs
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET: Optional[str] = None
    COINBASE_API_KEY: Optional[str] = None
    COINBASE_SECRET: Optional[str] = None

    # Simulation
    SIMULATION_TICK_INTERVAL: float = 0.1  # seconds
    MAX_SIMULATION_TICKS: int = 10000
    DEFAULT_INITIAL_BALANCE: float = 10000.0

    # Execution Powers
    EXECUTION_POWER_ENABLED: bool = False
    MAX_POSITION_SIZE: float = 1000.0
    MAX_DAILY_LOSS: float = 100.0

    # Payment Systems
    PAYMENT_ENABLED: bool = False
    PAYMENT_WEBHOOK_SECRET: Optional[str] = None
    AGENT_UPLOAD_ENABLED: bool = False
    ADMIN_USERS: List[str] = Field(default_factory=list)

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )

    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def split_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @validator("ALLOWED_HOSTS", pre=True)
    def split_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v
    
    @validator("ADMIN_USERS", pre=True)
    def split_admin_users(cls, v):
        if isinstance(v, str):
            return [user.strip() for user in v.split(",") if user.strip()]
        return v

settings = Settings()