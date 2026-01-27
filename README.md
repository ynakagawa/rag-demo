# AEM RAG Chatbot with MCP Integration

A production-ready RAG (Retrieval-Augmented Generation) chatbot application for Adobe Experience Manager (AEM) with Model Context Protocol (MCP) integration. Built with Python serverless functions on Vercel, powered by LangChain and OpenAI, with intelligent routing between RAG, MCP tools, and conversational AI.

## 🏗️ Architecture

- **Python Backend**: Flask API with LangChain, RAG, and MCP integration
- **RAG System**: Vector store (FAISS) with AEM documentation embeddings for knowledge retrieval
- **MCP Integration**: Adobe I/O Runtime MCP server with 12 AEM tools for automated operations
- **Intelligent Agent**: Automatic routing between RAG (knowledge), MCP tools (actions), and conversational AI
- **Node.js Frontend (Express)**: Beautiful web interface for the chat
- **LangSmith**: Real-time tracing and monitoring of all LLM interactions
- **Vercel Platform**: Serverless deployment with automatic scaling (Python + Node.js)

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- OpenAI API key
- LangSmith API key (optional, for tracing)
- AEM credentials (for MCP tools): AEM_SERVER and AEM_TOKEN

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

### 2. Index AEM Documentation (First Time Setup)

Before using the RAG features, index the AEM documentation:

```bash
source venv/bin/activate
python indexer.py
```

This creates a vector store in `./vector_store/` with AEM documentation embeddings.

### 3. Environment Variables

All environment variables are configured in `.env`:

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key

**Optional (for LangSmith tracing):**
- `LANGSMITH_API_KEY` - Your LangSmith API key
- `LANGSMITH_TRACING` - Enable/disable tracing (true/false)
- `LANGSMITH_ENDPOINT` - LangSmith API endpoint
- `LANGSMITH_PROJECT` - Your LangSmith project name

**For MCP Tools (AEM operations):**
- `AEM_SERVER` - Your AEM instance URL
- `AEM_TOKEN` - Your AEM authentication token

### 4. Start the Application

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

### 5. Open the Chat Interface

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
├── vector_store/        # FAISS vector store (created by indexer.py)
│   ├── index.faiss      # Vector index
│   └── index.pkl        # Metadata
├── agent_api.py         # Flask API for local development
├── server.js            # Node.js Express server
├── indexer.py           # Document indexer for RAG
├── rag_agent.py         # RAG agent for AEM documentation queries
├── mcp_client.py         # MCP client for Adobe I/O Runtime
├── intelligent_agent.py # Intelligent agent with automatic routing
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies
├── vercel.json          # Vercel configuration (Python + Node.js)
├── start.sh             # Startup script for local development
├── test_agent.py        # Test script
├── .env                 # Environment variables (local only)
└── venv/                # Python virtual environment (local only)
```

## 🔧 API Endpoints

### Local Development

**Python Backend (Port 5001):**
- `GET /health` - Health check (includes RAG and MCP status)
- `POST /chat` - Chat with intelligent agent (RAG/MCP/conversational)
- `POST /reset` - Reset conversation
- `GET /mcp/tools` - List available MCP tools
- `POST /mcp/execute` - Execute an MCP tool

**Node.js Frontend (Port 3000):**
- `GET /` - Chat interface
- `POST /api/chat` - Proxy to backend
- `POST /api/reset` - Proxy to backend
- `GET /health` - Health check

### Production (Vercel)

**Python Serverless Functions:**
- `/api/chat` - Chat endpoint with intelligent routing
- `/api/reset` - Reset endpoint
- `/api/health` - Health check

All routes are serverless and auto-scale!

## 📊 LangSmith Tracing

All conversations are automatically traced in LangSmith. View your traces at:
- URL: https://smith.langchain.com
- Project: `rag demo`

## 🧪 Testing

**Test RAG Agent:**
```bash
source venv/bin/activate
python rag_agent.py
```

**Test MCP Client:**
```bash
python mcp_client.py
```

**Test Intelligent Agent:**
```bash
python intelligent_agent.py
```

**Test Basic Agent:**
```bash
python test_agent.py
```

## 🎨 Features

### Core Features
- ✅ Real-time chat interface
- ✅ Conversation history per session
- ✅ Beautiful gradient UI
- ✅ Responsive design
- ✅ Typing indicator
- ✅ Error handling

### RAG (Retrieval-Augmented Generation)
- ✅ Vector store with AEM documentation embeddings
- ✅ Semantic search for AEM knowledge questions
- ✅ Source citations for transparency
- ✅ Automatic routing for AEM-related queries

### MCP Integration
- ✅ 12 Adobe I/O Runtime MCP tools available
- ✅ AEM site management (create, list, get info, delete)
- ✅ AEM content operations (components, content fragments, assets)
- ✅ Workflow management
- ✅ Automatic credential injection

### Intelligent Agent
- ✅ Automatic intent detection
- ✅ Smart routing: RAG for knowledge, MCP for actions, chat for general
- ✅ LLM-powered tool selection
- ✅ Natural language to tool arguments mapping

### Observability
- ✅ LangSmith tracing integration
- ✅ Health check endpoints
- ✅ Comprehensive error handling

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
3. Add environment variables:
   - `OPENAI_API_KEY` (required)
   - `LANGSMITH_API_KEY`, `LANGSMITH_TRACING`, `LANGSMITH_PROJECT` (optional)
   - `AEM_SERVER`, `AEM_TOKEN` (for MCP tools)
4. Deploy!

**Note:** The vector store (`vector_store/`) needs to be included in deployment or generated during build.

Reference: [Vercel Python Runtime Documentation](https://vercel.com/docs/functions/runtimes/python)

## 📚 Documentation

- **[TRAINING_INSTRUCTIONS.md](./TRAINING_INSTRUCTIONS.md)** - Complete step-by-step guide for building this app
- **[RAG_GUIDE.md](./RAG_GUIDE.md)** - Detailed RAG implementation guide
- **[MCP_INTEGRATION.md](./MCP_INTEGRATION.md)** - MCP integration documentation
- **[VERCEL_PYTHON_DEPLOYMENT.md](./VERCEL_PYTHON_DEPLOYMENT.md)** - Vercel deployment guide
- **[QUICK_START.md](./QUICK_START.md)** - Quick start guide

## 💡 Usage Examples

### Ask AEM Knowledge Questions (Uses RAG)
- "What is Adobe Experience Manager?"
- "How do AEM components work?"
- "What is AEM Dispatcher?"
- "Explain AEM as a Cloud Service"

### Request AEM Actions (Uses MCP Tools)
- "List my AEM sites"
- "Create a new microsite called 'Product Launch'"
- "Get info for diomicrosite"
- "Show me available templates"

### General Conversation
- "Hello, how are you?"
- "Tell me a joke"
- "What's the weather like?"

## 📝 License

ISC

