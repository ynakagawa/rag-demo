#!/bin/bash

# Quick status checker for the chatbot app

echo "🔍 Checking RAG-demo Chatbot Status..."
echo ""

# Check Python Backend (port 5001)
echo "📡 Python Backend (port 5001):"
if lsof -i :5001 | grep -q LISTEN; then
    echo "   ✅ Running"
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo "   ✅ Responding to requests"
    else
        echo "   ⚠️  Port open but not responding"
    fi
else
    echo "   ❌ Not running"
    echo "   💡 Start it with: source venv/bin/activate && python agent_api.py"
fi

echo ""

# Check Node.js Frontend (port 3000)
echo "🌐 Node.js Frontend (port 3000):"
if lsof -i :3000 | grep -q LISTEN; then
    echo "   ✅ Running"
    echo "   💡 Access at: http://localhost:3000"
else
    echo "   ❌ Not running"
    echo "   💡 Start it with: node server.js"
fi

echo ""

# Check full API chain
echo "🔗 Testing full API chain:"
if response=$(curl -s -X POST http://localhost:3000/api/chat -H "Content-Type: application/json" -d '{"message":"test","session_id":"status-check"}' 2>&1); then
    if echo "$response" | grep -q "response"; then
        echo "   ✅ Chat API working perfectly!"
    else
        echo "   ⚠️  API responded but with unexpected format"
        echo "   Response: $response"
    fi
else
    echo "   ❌ API not responding"
    echo "   Error: $response"
fi

echo ""
echo "📊 Summary:"
echo "   • Python Backend: http://localhost:5001"
echo "   • Node.js Frontend: http://localhost:3000"
echo "   • Chat Interface: http://localhost:3000"
echo ""

