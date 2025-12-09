# 🚀 Quick Start Guide

## Your Chatbot is Running! 🎉

### 🌐 Access Your Chatbot

Open your web browser and navigate to:

```
http://localhost:3000
```

### 📊 View LangSmith Traces

Monitor your agent's performance at:

```
https://smith.langchain.com
Project: pr-pertinent-bookend-77
```

### 🔧 Server Status

✅ **Python Backend (Flask API)**
- Running on: `http://localhost:5001`
- Terminal: `/terminals/4.txt`

✅ **Node.js Frontend (Express)**
- Running on: `http://localhost:3000`
- Terminal: `/terminals/5.txt`

### 💬 Using the Chatbot

1. Type your message in the input field
2. Press Enter or click "Send"
3. Watch as the AI responds in real-time
4. Click "🔄 Reset" to start a new conversation
5. All interactions are traced in LangSmith

### 🛑 Stopping the Servers

To stop the servers, you can:
- Press `Ctrl+C` in each terminal
- Or kill the processes from Activity Monitor/Task Manager

### 🔄 Restarting

To restart the servers:

```bash
# Terminal 1 - Python Backend
cd /Users/ynaka/Documents/RAG-demo
source venv/bin/activate
python agent_api.py

# Terminal 2 - Node.js Frontend
cd /Users/ynaka/Documents/RAG-demo
node server.js
```

Or use the startup script:
```bash
./start.sh
```

### ✨ Features

- 🤖 Powered by GPT-4o-mini
- 💬 Conversational memory per session
- 📊 LangSmith tracing for debugging
- 🎨 Beautiful gradient UI
- 📱 Responsive design
- ⚡ Real-time responses

### 🐛 Troubleshooting

**Port already in use?**
- Python: Change port in `agent_api.py` (currently 5001)
- Node.js: Change PORT in `server.js` (currently 3000)

**Backend not responding?**
- Check if Python backend is running
- Verify `.env` file has correct API keys
- Check terminal logs for errors

**Can't see traces in LangSmith?**
- Verify `LANGSMITH_TRACING=true` in `.env`
- Check your API key is correct
- Visit https://smith.langchain.com and login

### 📚 Next Steps

- Customize the chat interface in `views/chat.ejs`
- Add more tools to the agent in `agent_api.py`
- Integrate RAG (Retrieval-Augmented Generation) with vector stores
- Add authentication
- Deploy to production

Enjoy your AI chatbot! 🎉

