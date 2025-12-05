import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
from starlette.requests import Request
from starlette.responses import Response

from .core.config import settings
from .core.database import create_tables, get_db, get_redis
from .routes import agents, auth, crypto, execution, matches, users, wallets
from .services.websocket_manager import ws_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# Global WebSocket manager (shared across modules)
websocket_manager = ws_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    await websocket_manager.startup()
    yield
    # Shutdown
    await websocket_manager.shutdown()

app = FastAPI(
    title="WagmiWars API",
    description="AI Trading Agent Arena Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware for traceability
app.add_middleware(RequestIDMiddleware)

# Host protection (allow "*" only for local/dev)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS or ["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(execution.router, prefix="/api/execution", tags=["execution"])
app.include_router(crypto.router, prefix="/api/crypto", tags=["crypto"])
app.include_router(wallets.router, prefix="/api/wallets", tags=["wallets"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to WagmiWars API",
        "version": "1.0.0",
        "status": "operational",
        "features": {
            "simulation": True,
            "real_trading": settings.EXECUTION_POWER_ENABLED,
            "crypto_payments": settings.PAYMENT_ENABLED,
            "websocket": True
        }
    }

@app.get("/health")
async def health_check(db=Depends(get_db), redis=Depends(get_redis)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        # Test Redis connection
        redis.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "websocket": websocket_manager.is_connected()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket, client_id: str):
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.broadcast(f"Client {client_id}: {data}")
    except:
        websocket_manager.disconnect(client_id)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )