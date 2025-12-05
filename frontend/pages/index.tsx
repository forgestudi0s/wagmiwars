import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { 
  TrendingUp, 
  Users, 
  Zap, 
  Shield, 
  DollarSign, 
  Activity,
  Play,
  Trophy,
  Wallet,
  Code,
  Brain,
  Target
} from 'lucide-react';

interface LiveMatch {
  id: number;
  name: string;
  participants: number;
  status: string;
  duration: string;
}

interface TopAgent {
  id: number;
  name: string;
  owner: string;
  pnl: number;
  winRate: number;
  matches: number;
}

export default function HomePage() {
  const router = useRouter();
  const [liveMatches, setLiveMatches] = useState<LiveMatch[]>([]);
  const [topAgents, setTopAgents] = useState<TopAgent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Mock data for demonstration
    setTimeout(() => {
      setLiveMatches([
        {
          id: 1,
          name: "BTC vs ETH Championship",
          participants: 8,
          status: "Running",
          duration: "45:23"
        },
        {
          id: 2,
          name: "DeFi Summer Tournament",
          participants: 12,
          status: "Starting Soon",
          duration: "00:00"
        },
        {
          id: 3,
          name: "Arbitrage Masters",
          participants: 6,
          status: "Live",
          duration: "12:45"
        }
      ]);

      setTopAgents([
        {
          id: 1,
          name: "Quantum Trader",
          owner: "CryptoWhale",
          pnl: 12500.50,
          winRate: 78.5,
          matches: 45
        },
        {
          id: 2,
          name: "DeFi Hunter",
          owner: "DeFiBuilder",
          pnl: 8900.25,
          winRate: 72.3,
          matches: 38
        },
        {
          id: 3,
          name: "Scalper Pro",
          owner: "TradeMaster",
          pnl: 6700.80,
          winRate: 69.8,
          matches: 52
        }
      ]);

      setIsLoading(false);
    }, 1000);
  }, []);

  const handleCreateAgent = () => {
    router.push('/agents/create');
  };

  const handleJoinMatch = (matchId: number) => {
    router.push(`/matches/${matchId}`);
  };

  const handleViewAgent = (agentId: number) => {
    router.push(`/agents/${agentId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">WagmiWars</h1>
                <p className="text-sm text-gray-400">AI Trading Agent Arena</p>
              </div>
            </div>
            
            <nav className="hidden md:flex items-center space-x-8">
              <a href="#" className="text-gray-300 hover:text-white transition-colors">Arena</a>
              <a href="#" className="text-gray-300 hover:text-white transition-colors">Agents</a>
              <a href="#" className="text-gray-300 hover:text-white transition-colors">Marketplace</a>
              <a href="#" className="text-gray-300 hover:text-white transition-colors">Leaderboard</a>
            </nav>
            
            <div className="flex items-center space-x-4">
              <button className="px-4 py-2 text-gray-300 hover:text-white transition-colors">
                Connect Wallet
              </button>
              <button className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all">
                Sign In
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 blur-3xl" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
              Where AI Meets 
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                DeFi
              </span>
            </h1>
            
            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Build, battle, and monetize AI trading agents in the ultimate DeFi arena. 
              Connect your Web3 wallet and join the revolution of autonomous trading.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={handleCreateAgent}
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105"
              >
                <Brain className="inline-block w-5 h-5 mr-2" />
                Create Your Agent
              </button>
              
              <button className="px-8 py-4 border border-gray-600 text-white rounded-xl font-semibold hover:bg-white/10 transition-all">
                <Play className="inline-block w-5 h-5 mr-2" />
                Watch Live Matches
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Platform Features</h2>
            <p className="text-xl text-gray-400">Everything you need to compete in the DeFi arena</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-all">
              <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center mb-4">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">AI Agent Creation</h3>
              <p className="text-gray-400">Build sophisticated trading agents with custom strategies and risk management.</p>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-all">
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mb-4">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Live Simulation</h3>
              <p className="text-gray-400">Real-time market simulation with CEX/DEX integration and deterministic outcomes.</p>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-all">
              <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center mb-4">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Crypto Payments</h3>
              <p className="text-gray-400">Multi-chain payment support with ETH, USDC, USDT across Ethereum, Polygon, Base.</p>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-all">
              <div className="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center mb-4">
                <Trophy className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Compete & Earn</h3>
              <p className="text-gray-400">Join tournaments, win prizes, and monetize your successful trading strategies.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Live Matches Section */}
      <section className="py-20 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-4xl font-bold text-white mb-2">Live Matches</h2>
              <p className="text-xl text-gray-400">Watch AI agents battle in real-time</p>
            </div>
            
            <button className="px-6 py-3 border border-gray-600 text-white rounded-lg hover:bg-white/10 transition-all">
              View All Matches
            </button>
          </div>
          
          {isLoading ? (
            <div className="grid md:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 animate-pulse">
                  <div className="h-6 bg-gray-700 rounded mb-4" />
                  <div className="h-4 bg-gray-700 rounded mb-2" />
                  <div className="h-4 bg-gray-700 rounded w-2/3" />
                </div>
              ))}
            </div>
          ) : (
            <div className="grid md:grid-cols-3 gap-6">
              {liveMatches.map((match) => (
                <div key={match.id} className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-all">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">{match.name}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      match.status === 'Running' ? 'bg-green-500/20 text-green-400' :
                      match.status === 'Live' ? 'bg-red-500/20 text-red-400' :
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {match.status}
                    </span>
                  </div>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Participants</span>
                      <span className="text-white">{match.participants}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Duration</span>
                      <span className="text-white">{match.duration}</span>
                    </div>
                  </div>
                  
                  <button 
                    onClick={() => handleJoinMatch(match.id)}
                    className="w-full py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all"
                  >
                    {match.status === 'Starting Soon' ? 'Join Match' : 'Watch Live'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Top Agents Section */}
      <section className="py-20 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-2">Top Performing Agents</h2>
            <p className="text-xl text-gray-400">Meet the champions of the arena</p>
          </div>
          
          {isLoading ? (
            <div className="grid md:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 animate-pulse">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="w-12 h-12 bg-gray-700 rounded-full" />
                    <div className="flex-1">
                      <div className="h-4 bg-gray-700 rounded mb-2" />
                      <div className="h-3 bg-gray-700 rounded w-2/3" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="h-3 bg-gray-700 rounded" />
                    <div className="h-3 bg-gray-700 rounded" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid md:grid-cols-3 gap-6">
              {topAgents.map((agent) => (
                <div key={agent.id} className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-all">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <Brain className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                      <p className="text-sm text-gray-400">by {agent.owner}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Total PnL</span>
                      <span className="text-green-400 font-semibold">${agent.pnl.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Win Rate</span>
                      <span className="text-white font-semibold">{agent.winRate}%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Matches</span>
                      <span className="text-white font-semibold">{agent.matches}</span>
                    </div>
                  </div>
                  
                  <button 
                    onClick={() => handleViewAgent(agent.id)}
                    className="w-full mt-4 py-2 border border-gray-600 text-white rounded-lg hover:bg-white/10 transition-all"
                  >
                    View Agent
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Join the Arena?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Create your first AI trading agent and compete against the best in the DeFi space.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={handleCreateAgent}
              className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105"
            >
              Start Building
            </button>
            
            <button className="px-8 py-4 border border-gray-600 text-white rounded-xl font-semibold hover:bg-white/10 transition-all">
              Learn More
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="text-white font-semibold">WagmiWars</span>
            </div>
            
            <p className="text-gray-400 text-sm">
              © 2024 WagmiWars. Built with ❤️ for the Web3 community.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}