# AEM chatbot and agent

A production-ready chatbot application using Python serverless functions on Vercel, powered by LangChain and OpenAI, with LangSmith tracing integration.

## 🏗️ Architecture

- **Python Serverless Functions**: LangChain-powered API endpoints (deployed with Vercel's Python runtime)
- **Node.js Frontend (Express)**: Beautiful web interface for the chat
- **LangSmith**: Real-time tracing and monitoring of all LLM interactions
- **Vercel Platform**: Serverless deployment with automatic scaling

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- OpenAI API key
- LangSmith API key (optional, for tracing)

## 🚀 Quick Start

### 1. Install Dependencies

Already done! But if you need to reinstall:

```bash
# Python dependencies
source venv/bin/activate
pip install -r requirements.txt

# Node.js dependencies
npm install
```

### 2. Environment Variables

All environment variables are already configured in `.env`:

- `OPENAI_API_KEY` - Your OpenAI API key
- `LANGSMITH_API_KEY` - Your LangSmith API key
- `LANGSMITH_TRACING` - Enable/disable tracing (true/false)
- `LANGSMITH_ENDPOINT` - LangSmith API endpoint
- `LANGSMITH_PROJECT` - Your LangSmith project name

### 3. Start the Application

**Option A: Use the startup script (Recommended)**

```bash
chmod +x start.sh
./start.sh
```

**Option B: Start servers manually**

Terminal 1 - Python Backend:
```bash
source venv/bin/activate
python agent_api.py
```

Terminal 2 - Node.js Frontend:
```bash
node server.js
```

### 4. Open the Chat Interface

Open your browser and navigate to:
```
http://localhost:3000
```

## 📁 Project Structure

```
RAG-demo/
├── api/
│   ├── chat.py          # Python serverless function for chat
│   ├── reset.py         # Python serverless function for reset
│   └── health.py        # Python serverless function for health
├── views/
│   └── chat.ejs         # Beautiful chat interface
├── agent_api.py         # Flask API for local development
├── server.js            # Node.js Express server
├── requirements.txt     # Python dependencies (for Vercel)
├── package.json         # Node.js dependencies
├── vercel.json          # Vercel configuration (Python + Node.js)
├── test_agent.py        # Test script
├── .env                 # Environment variables (local only)
└── venv/                # Python virtual environment (local only)
```

## 🔧 API Endpoints

### Local Development

**Python Backend (Port 5001):**
- `GET /health` - Health check
- `POST /chat` - Chat with AI
- `POST /reset` - Reset conversation

**Node.js Frontend (Port 3000):**
- `GET /` - Chat interface
- `POST /api/chat` - Proxy to backend
- `POST /api/reset` - Proxy to backend
- `GET /health` - Health check

### Production (Vercel)

**Python Serverless Functions:**
- `/api/chat` - Chat endpoint
- `/api/reset` - Reset endpoint
- `/api/health` - Health check

All routes are serverless and auto-scale!

## 📊 LangSmith Tracing

All conversations are automatically traced in LangSmith. View your traces at:
- URL: https://smith.langchain.com
- Project: `pr-pertinent-bookend-77`

## 🧪 Testing

Run the simple test agent:

```bash
source venv/bin/activate
python test_agent.py
```

## 🎨 Features

- ✅ Real-time chat interface
- ✅ Conversation history per session
- ✅ LangSmith tracing integration
- ✅ Beautiful gradient UI
- ✅ Responsive design
- ✅ Reset conversation feature
- ✅ Typing indicator
- ✅ Error handling

## 🔒 Security Notes

- Never commit `.env` file to version control
- Add `.env` to `.gitignore`
- Keep your API keys secure
- Use environment-specific configuration for production

## 🚀 Deploying to Vercel

This app uses **Vercel's Python runtime** for serverless Python functions!

See detailed deployment guide: [VERCEL_PYTHON_DEPLOYMENT.md](./VERCEL_PYTHON_DEPLOYMENT.md)

**Quick steps:**
1. Push to GitHub (already done!)
2. Import to Vercel: https://vercel.com
3. Add environment variables (OPENAI_API_KEY, etc.)
4. Deploy!

Reference: [Vercel Python Runtime Documentation](https://vercel.com/docs/functions/runtimes/python)

## 📝 License

ISC

