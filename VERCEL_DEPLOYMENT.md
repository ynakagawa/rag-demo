# 🚀 Vercel Deployment Guide

## Overview

Your chatbot app has been updated to work with Vercel's serverless architecture. The Python backend has been replaced with Node.js serverless functions in the `api/` directory.

## 📁 New Files

- `api/chat.js` - Serverless function for chat endpoint
- `api/reset.js` - Serverless function for reset endpoint
- `api/health.js` - Serverless function for health check
- `vercel.json` - Vercel configuration

## 🔧 Deployment Steps

### 1. Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

### 2. Configure Environment Variables in Vercel

Go to your Vercel project settings and add these environment variables:

**Required:**
- `OPENAI_API_KEY` = `<your-openai-api-key>` (Get from https://platform.openai.com/api-keys)

**Optional (for LangSmith tracing):**
- `LANGSMITH_API_KEY` = `<your-langsmith-api-key>` (Get from https://smith.langchain.com)
- `LANGSMITH_TRACING` = `true`
- `LANGSMITH_PROJECT` = `<your-project-name>`
- `LANGSMITH_ENDPOINT` = `https://api.smith.langchain.com`

### 3. Deploy to Vercel

**Option A: Via Vercel Dashboard**
1. Go to https://vercel.com
2. Click "Import Project"
3. Connect your GitHub repository: `https://github.com/ynakagawa/rag-demo`
4. Vercel will auto-detect the configuration
5. Add environment variables
6. Click "Deploy"

**Option B: Via CLI**
```bash
cd /Users/ynaka/Documents/RAG-demo
vercel
```

Follow the prompts and your app will be deployed!

### 4. Access Your Deployed App

After deployment, Vercel will give you a URL like:
```
https://rag-demo-abc123.vercel.app
```

## 🏗️ Architecture Changes

### Before (Local Development)
```
Browser → Node.js (Express) → Python (Flask) → OpenAI
```

### After (Vercel)
```
Browser → Node.js (Express) → Serverless Functions → OpenAI
```

## 🔄 Local Development

For local development, you can still use the Python backend:

```bash
# Terminal 1 - Python Backend
source venv/bin/activate
python agent_api.py

# Terminal 2 - Node.js Frontend
node server.js
```

Or use the serverless functions locally with Vercel CLI:

```bash
vercel dev
```

## 📊 LangSmith Integration

LangSmith tracing works in both environments:
- The serverless functions automatically use the environment variables
- Visit https://smith.langchain.com to view traces
- Project: `pr-pertinent-bookend-77`

## ⚠️ Important Notes

### Limitations
- **Conversation Memory**: Currently uses in-memory storage which resets on each function invocation. For production, use:
  - Vercel KV (Redis)
  - Upstash Redis
  - MongoDB Atlas
  - Or any other database

### Recommended Improvements
1. Add a database for conversation persistence
2. Implement rate limiting
3. Add authentication
4. Set up monitoring

### Example: Using Vercel KV for persistence

Install Vercel KV:
```bash
npm install @vercel/kv
```

Update `api/chat.js`:
```javascript
import { kv } from '@vercel/kv';

// Store conversation
await kv.set(`conversation:${session_id}`, history);

// Retrieve conversation
const history = await kv.get(`conversation:${session_id}`) || [];
```

## 🐛 Troubleshooting

**Issue: API timeout**
- Vercel has a 10-second timeout for Hobby plan
- Upgrade to Pro for 60-second timeout
- Or optimize your prompts

**Issue: Environment variables not working**
- Redeploy after adding environment variables
- Check variable names match exactly

**Issue: Cold starts**
- First request may be slow (serverless cold start)
- This is normal behavior

**Issue: Conversation not persisting**
- Implement a database solution (see recommendations above)

## 🔐 Security

✅ Environment variables are secure in Vercel
✅ `.env` file is not deployed (in `.gitignore`)
✅ API keys are never exposed to the client

## 📚 Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Serverless Functions](https://vercel.com/docs/functions)
- [Vercel KV](https://vercel.com/docs/storage/vercel-kv)
- [OpenAI Node.js SDK](https://github.com/openai/openai-node)

## ✨ Next Steps

1. ✅ Deploy to Vercel
2. 🔄 Add database for conversation persistence
3. 🔒 Add authentication
4. 📊 Set up monitoring/analytics
5. 🚀 Add more AI features

