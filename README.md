# RAG-demo Chatbot

A simple Node.js-based chatbot application powered by LangChain and OpenAI, with LangSmith tracing integration.

## 🏗️ Architecture

- **Python Backend (Flask)**: API server that handles LangChain agent interactions
- **Node.js Frontend (Express)**: Web server that serves the chat interface
- **LangSmith**: Traces and monitors all LLM interactions

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
├── agent_api.py          # Flask API backend
├── server.js             # Node.js Express server
├── package.json          # Node.js dependencies
├── views/
│   └── chat.ejs         # Chat interface template
├── test_agent.py        # Simple test script
├── .env                 # Environment variables
├── venv/                # Python virtual environment
└── start.sh             # Startup script
```

## 🔧 API Endpoints

### Python Backend (Port 5000)

- `GET /health` - Health check endpoint
- `POST /chat` - Send a message to the agent
- `POST /reset` - Reset conversation history

### Node.js Frontend (Port 3000)

- `GET /` - Chat interface
- `POST /api/chat` - Proxy to Python backend
- `POST /api/reset` - Proxy to Python backend
- `GET /health` - Combined health check

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

## 📝 License

ISC

