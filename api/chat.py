"""
Python serverless function for chat endpoint on Vercel
Uses Intelligent MCP Agent with RAG for Adobe Experience Manager
"""
from flask import Flask, request, jsonify
import os
import sys

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client import MCPClient
from rag_agent import AEMRAGAgent
from intelligent_agent import IntelligentMCPAgent

app = Flask(__name__)

# Initialize MCP Client
MCP_SERVER_URL = "https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server"
mcp_client = MCPClient(MCP_SERVER_URL)

# Initialize RAG Agent
rag_agent = AEMRAGAgent()

# Initialize Intelligent Agent
intelligent_agent = IntelligentMCPAgent(mcp_client, rag_agent)

print("✅ Intelligent MCP Agent initialized")
print(f"✅ RAG ready: {rag_agent.is_ready()}")
print(f"✅ MCP tools available: {len(mcp_client.list_tools())}")

# In-memory conversation storage (in production, use a database)
conversations = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with Intelligent MCP Agent + RAG support"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Use intelligent agent to process message
        result = intelligent_agent.process_message(user_message)
        
        return jsonify({
            "response": result.get("response"),
            "session_id": session_id,
            "mode": result.get("mode"),
            "tool_executed": result.get("tool_executed"),
            "sources": result.get("sources", [])
        })
    
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

