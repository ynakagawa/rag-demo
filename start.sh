#!/bin/bash

# Startup script for RAG-demo chatbot

echo "🚀 Starting RAG-demo Chatbot..."
echo ""

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Start Python backend in background
echo "📡 Starting Python backend (Flask API)..."
source venv/bin/activate && python agent_api.py &
PYTHON_PID=$!

# Wait for Python backend to start
sleep 3

# Start Node.js frontend
echo "🌐 Starting Node.js frontend..."
node server.js &
NODE_PID=$!

echo ""
echo "✅ Both servers are running!"
echo ""
echo "🌐 Open your browser and go to: http://localhost:3000"
echo "📊 LangSmith tracing: https://smith.langchain.com"
echo "   Project: $LANGSMITH_PROJECT"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for Ctrl+C
trap "kill $PYTHON_PID $NODE_PID; exit" INT
wait

