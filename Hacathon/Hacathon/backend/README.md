# 🧭 Jupiter Smart Swap - Backend Services

## 📁 Project Structure

```
backend/
├── README.md                    # This file
├── services/
│   ├── __init__.py
│   ├── route_analyzer.py        # Core route analysis logic
│   ├── jupiter_api.py           # Jupiter API client
│   ├── swap_executor.py         # Swap execution logic
│   └── wallet_integration.py    # Wallet connection logic
├── models/
│   ├── __init__.py
│   ├── swap_request.py          # Data models
│   └── route_analysis.py        # Route analysis models
├── utils/
│   ├── __init__.py
│   ├── scoring.py               # Efficiency scoring algorithms
│   └── formatters.py            # Data formatting utilities
├── api/
│   ├── __init__.py
│   ├── routes.py                # API endpoints
│   └── server.py                # FastAPI server
└── config/
    ├── __init__.py
    └── settings.py              # Configuration settings
```

## 🚀 How It Works

### 1. **Route Analyzer Service** (`services/route_analyzer.py`)
- Fetches routes from Jupiter API
- Analyzes efficiency using custom algorithms
- Returns ranked routes with scores

### 2. **Swap Executor Service** (`services/swap_executor.py`)
- Gets swap transaction from Jupiter
- Handles wallet signing
- Executes transactions on Solana

### 3. **API Layer** (`api/`)
- REST API endpoints for mobile app integration
- Handles requests and responses
- Manages different swap modes

## 🔄 Flow Diagram

```
User Request → API → Route Analyzer → Jupiter API → Analysis → Swap Executor → Solana Network
     ↓              ↓                    ↓              ↓           ↓              ↓
  Mobile App    Backend API         Route Data    Efficiency   Transaction    Success/Fail
```

## 🎯 Integration Points

### **For Jupiter Mobile App:**
1. Mobile app calls your API
2. Your service analyzes routes
3. Returns best route or executes auto-swap
4. Mobile app shows results to user

### **For Hackathon Demo:**
1. Web UI calls your API
2. Shows real-time analysis
3. Demonstrates auto-swap functionality
4. Proves concept works

## 📊 API Endpoints

- `POST /analyze` - Analyze routes only
- `POST /auto-swap` - Auto-select and execute best route
- `POST /manual-swap` - Get analysis for manual selection
- `GET /health` - Service health check

## 🛠️ Setup Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Start API server: `python api/server.py`
3. Test endpoints with provided examples
4. Integrate with mobile app or web UI

## 🎭 Demo Mode

- Uses mock data when Jupiter API is unavailable
- Perfect for hackathon demonstrations
- Shows complete functionality without external dependencies 