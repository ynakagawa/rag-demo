#!/bin/bash

# Quick script to update LangSmith credentials in .env

echo "🔑 LangSmith Credentials Update Script"
echo "========================================"
echo ""
echo "After you get your credentials from LangSmith:"
echo "https://smith.langchain.com"
echo ""

read -p "Enter your LangSmith API Key (Personal Access Token): " LANGSMITH_KEY
read -p "Enter your LangSmith Project Name: " LANGSMITH_PROJECT

echo ""
echo "Updating .env file..."

# Backup current .env
cp .env .env.backup
echo "✅ Backed up current .env to .env.backup"

# Update LANGSMITH_API_KEY
sed -i '' "s|LANGSMITH_API_KEY=.*|LANGSMITH_API_KEY=$LANGSMITH_KEY|" .env

# Update LANGSMITH_PROJECT
sed -i '' "s|LANGSMITH_PROJECT=.*|LANGSMITH_PROJECT=$LANGSMITH_PROJECT|" .env

# Ensure LANGSMITH_TRACING is true
sed -i '' "s|LANGSMITH_TRACING=.*|LANGSMITH_TRACING=true|" .env

echo "✅ Updated .env file"
echo ""
echo "Your new configuration:"
cat .env | grep LANGSMITH
echo ""
echo "🧪 Test the connection:"
echo "   python test_langsmith.py"
echo ""
echo "🔄 Restart servers:"
echo "   pkill -f 'python agent_api.py' && pkill -f 'node server.js'"
echo "   ./start.sh"
