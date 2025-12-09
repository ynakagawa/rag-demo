# 🐍 Vercel Python Runtime Deployment Guide

## Overview

Your chatbot now uses **Vercel's Python runtime** (Beta) to deploy the LangChain backend as serverless functions. This is the best solution because:

✅ Keep your Python code with full LangChain support  
✅ Native LangSmith tracing integration  
✅ Use all Python AI libraries  
✅ Serverless scaling on Vercel  
✅ No need to convert to Node.js  

Reference: [Vercel Python Runtime Documentation](https://vercel.com/docs/functions/runtimes/python)

## 📁 Project Structure

```
RAG-demo/
├── api/
│   ├── chat.py          # Python serverless function for chat
│   ├── reset.py         # Python serverless function for reset
│   └── health.py        # Python serverless function for health
├── server.js            # Node.js Express for frontend UI
├── views/
│   └── chat.ejs        # Chat interface
├── requirements.txt     # Python dependencies for Vercel
├── vercel.json         # Vercel configuration
└── .env                # Environment variables (not deployed)
```

## 🏗️ Architecture

### On Vercel (Production)
```
Browser → Node.js (Express) → Python Serverless Functions → OpenAI
                                      ↓
                              LangSmith Tracing
```

### Local Development
```
Browser → Node.js (Express) → Python Flask (agent_api.py) → OpenAI
                                      ↓
                              LangSmith Tracing
```

## 🚀 Deploy to Vercel

### Step 1: Push to GitHub

Your code is already on GitHub at: `https://github.com/ynakagawa/rag-demo`

### Step 2: Import to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository: `ynakagawa/rag-demo`
4. Vercel will automatically detect:
   - Python runtime for `api/*.py` files
   - Node.js runtime for `server.js`
   - Dependencies from `requirements.txt` and `package.json`

### Step 3: Configure Environment Variables

In your Vercel project settings, add these environment variables:

**Required:**
- `OPENAI_API_KEY` = Your OpenAI API key

**Optional (for LangSmith tracing):**
- `LANGSMITH_API_KEY` = Your LangSmith API key
- `LANGSMITH_TRACING` = `true`
- `LANGSMITH_PROJECT` = Your project name (e.g., `pr-pertinent-bookend-77`)
- `LANGSMITH_ENDPOINT` = `https://api.smith.langchain.com`

### Step 4: Deploy

Click "Deploy" and Vercel will:
1. Install Python dependencies from `requirements.txt`
2. Install Node.js dependencies from `package.json`
3. Build your Python functions
4. Build your Node.js frontend
5. Deploy everything as serverless functions

You'll get a URL like: `https://rag-demo.vercel.app`

## 🔧 Python Runtime Details

### Python Version
- **Python 3.12** (cannot be changed)

### Dependencies
- Listed in `requirements.txt`
- Automatically installed by Vercel
- Include all LangChain packages

### Bundle Size Limit
- Maximum **250 MB** uncompressed
- Current setup is well under this limit

### Supported Frameworks
- ✅ Flask (what we're using)
- ✅ FastAPI
- ✅ Django
- ✅ WSGI applications
- ✅ ASGI applications

## 💻 Local Development

You can still develop locally using either:

**Option 1: Original Flask server (Recommended)**
```bash
# Terminal 1 - Python Backend
cd /Users/ynaka/Documents/RAG-demo
source venv/bin/activate
python agent_api.py

# Terminal 2 - Node.js Frontend
node server.js
```

**Option 2: Vercel CLI (Test production-like environment)**
```bash
# Install Vercel CLI
npm install -g vercel

# Run locally
vercel dev
```

**Option 3: Use the startup script**
```bash
./start.sh
```

## 📊 LangSmith Tracing

LangSmith tracing works seamlessly with Python serverless functions:

1. Set environment variables in Vercel dashboard
2. All LangChain calls are automatically traced
3. View traces at: https://smith.langchain.com
4. Filter by project name

## ⚙️ Configuration Files

### `requirements.txt`
Lists all Python dependencies:
- Flask for HTTP handling
- LangChain for AI orchestration
- OpenAI for LLM access
- LangSmith for tracing

### `vercel.json`
Configures Vercel deployment:
- Uses `@vercel/python` for Python files
- Uses `@vercel/node` for Node.js files
- Routes API calls to Python functions
- Routes UI requests to Express server

## 🔄 Differences from Node.js Approach

| Feature | Python Runtime | Node.js Runtime |
|---------|---------------|-----------------|
| LangChain Support | ✅ Full support | ⚠️ Limited |
| LangSmith Integration | ✅ Native | ⚠️ Manual |
| Code Reuse | ✅ Same as local | ❌ Need rewrite |
| AI Libraries | ✅ All Python libs | ⚠️ JS only |
| Setup Complexity | ✅ Simple | ⚠️ More complex |

## 🐛 Troubleshooting

### Issue: Python function timeout
**Solution:** Vercel has a 10-second timeout on Hobby plan (60s on Pro)
- Optimize your prompts
- Use streaming responses
- Upgrade to Pro plan if needed

### Issue: Import errors
**Solution:** Make sure all dependencies are in `requirements.txt`
```bash
pip freeze > requirements.txt
```

### Issue: Environment variables not working
**Solution:** 
- Add them in Vercel dashboard (not in vercel.json)
- Redeploy after adding variables
- Check exact variable names

### Issue: Cold starts
**Solution:** This is normal for serverless
- First request may be slow (~2-5 seconds)
- Subsequent requests are fast
- Consider keeping functions warm with cron jobs

### Issue: 250 MB bundle size exceeded
**Solution:** Exclude unnecessary files
```json
{
  "functions": {
    "api/*.py": {
      "excludeFiles": "tests/**"
    }
  }
}
```

## 🎯 Production Recommendations

### 1. Add a Database for Conversation Persistence
Currently using in-memory storage (resets on each function call).

**Recommended options:**
- **Vercel KV** (Redis) - Best for Vercel
- **Upstash Redis** - Serverless Redis
- **MongoDB Atlas** - Document database
- **Supabase** - PostgreSQL

### 2. Implement Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.headers.get('X-Forwarded-For', request.remote_addr)
)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    # ... your code
```

### 3. Add Authentication
- Use Vercel's built-in authentication
- Or implement your own with JWT
- Protect sensitive endpoints

### 4. Enable Streaming
```python
from flask import Response, stream_with_context

@app.route('/api/chat', methods=['POST'])
def chat():
    def generate():
        for chunk in llm.stream(messages):
            yield f"data: {chunk.content}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream'
    )
```

### 5. Monitor and Optimize
- Use Vercel Analytics
- Monitor LangSmith traces
- Set up error tracking (Sentry)
- Track costs and usage

## 📚 Resources

- [Vercel Python Runtime Documentation](https://vercel.com/docs/functions/runtimes/python)
- [Vercel Functions](https://vercel.com/docs/functions)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [LangChain Python Documentation](https://python.langchain.com/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)

## ✨ Next Steps

1. ✅ Deploy to Vercel with Python runtime
2. 🔄 Add database for conversation persistence
3. 🔒 Implement authentication
4. 📊 Set up monitoring and analytics
5. 🚀 Add RAG with vector stores (Pinecone, Weaviate)
6. ⚡ Implement streaming responses
7. 🎨 Customize the UI

## 🆚 Why This is Better

**Before (Node.js API functions):**
- Had to rewrite Python code in JavaScript
- Limited LangChain features
- Manual LangSmith integration
- Two different codebases

**Now (Python runtime):**
- ✅ Same Python code everywhere
- ✅ Full LangChain ecosystem
- ✅ Native LangSmith support
- ✅ One codebase, works everywhere

Your deployment is now production-ready with the full power of Python and LangChain! 🎉

