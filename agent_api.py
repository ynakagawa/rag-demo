"""
Flask API wrapper for the LangChain agent with RAG and MCP support
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from rag_agent import AEMRAGAgent
from mcp_client import MCPClient, MCPIntegratedAgent
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for Node.js frontend

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Initialize RAG agent
print("🚀 Initializing RAG agent...")
rag_agent = AEMRAGAgent()
if rag_agent.is_ready():
    print("✅ RAG agent ready for AEM questions!")
else:
    print("⚠️  RAG agent not available. Run 'python indexer.py' to enable RAG.")

# Initialize MCP client
print("🔧 Initializing MCP client...")
mcp_url = "https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server"
mcp_client = MCPClient(mcp_url)

# Check MCP server health
if mcp_client.is_healthy():
    print("✅ MCP server connected successfully!")
    mcp_tools = mcp_client.list_tools()
    print(f"✅ Loaded {len(mcp_tools)} MCP tools")
else:
    print("⚠️  MCP server not available")
    mcp_tools = []

# Store conversation history (in production, use a proper database)
conversation_history = {}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model": "gpt-4o-mini",
        "rag_ready": rag_agent.is_ready(),
        "mcp_connected": mcp_client.is_healthy(),
        "mcp_tools": len(mcp_tools)
    })

@app.route('/mcp/tools', methods=['GET'])
def get_mcp_tools():
    """Get available MCP tools"""
    try:
        return jsonify({
            "tools": mcp_tools,
            "count": len(mcp_tools)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/execute', methods=['POST'])
def execute_mcp_tool():
    """Execute an MCP tool"""
    try:
        data = request.json
        tool_name = data.get('tool_name')
        arguments = data.get('arguments', {})
        
        if not tool_name:
            return jsonify({"error": "tool_name is required"}), 400
        
        result = mcp_client.call_tool(tool_name, arguments)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint with RAG support"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        use_rag = data.get('use_rag', True)
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Check if question is AEM-related or MCP tool request
        aem_keywords = ['aem', 'adobe', 'experience manager', 'dispatcher', 'component', 'sling', 'jcr', 'dam', 'assets', 'sites', 'forms']
        mcp_keywords = ['create', 'delete', 'list', 'upload', 'workflow', 'site', 'microsite', 'template']
        
        is_aem_question = any(keyword in user_message.lower() for keyword in aem_keywords)
        is_mcp_request = any(keyword in user_message.lower() for keyword in mcp_keywords)
        
        # Use RAG for AEM questions if available
        if use_rag and is_aem_question and rag_agent.is_ready():
            result = rag_agent.query(user_message)
            response_text = result["answer"]
            
            # Add sources if available
            if result.get("sources"):
                sources_text = "\n\n📚 **Sources:**\n"
                for i, source in enumerate(result["sources"][:2], 1):
                    sources_text += f"{i}. {source['source']}\n"
                response_text += sources_text
            
            # Add MCP tools suggestion if relevant
            if is_mcp_request and mcp_tools:
                response_text += f"\n\n🔧 **MCP Tools Available:**\n"
                response_text += f"I have access to {len(mcp_tools)} Adobe I/O Runtime tools including:\n"
                for tool in mcp_tools[:3]:
                    response_text += f"- `{tool['name']}`: {tool.get('description', '')[:60]}...\n"
                response_text += f"\nWould you like me to use any of these tools?"
            
            return jsonify({
                "response": response_text,
                "session_id": session_id,
                "mode": "rag",
                "sources": result.get("sources", []),
                "mcp_tools_available": len(mcp_tools) > 0
            })
        
        # Fall back to conversational mode
        # Get or create conversation history for this session
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Add user message to history
        conversation_history[session_id].append(HumanMessage(content=user_message))
        
        # Get response from LLM (LangSmith will trace this)
        response = llm.invoke(conversation_history[session_id])
        
        # Add AI response to history
        conversation_history[session_id].append(response)
        
        # Keep only last 10 messages to avoid token limits
        if len(conversation_history[session_id]) > 10:
            conversation_history[session_id] = conversation_history[session_id][-10:]
        
        return jsonify({
            "response": response.content,
            "session_id": session_id,
            "mode": "conversational"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    """Reset conversation history"""
    data = request.json
    session_id = data.get('session_id', 'default')
    
    if session_id in conversation_history:
        conversation_history[session_id] = []
    
    return jsonify({"message": "Conversation reset", "session_id": session_id})

if __name__ == '__main__':
    print("🚀 Starting Flask API server...")
    print(f"📊 LangSmith Project: {os.getenv('LANGSMITH_PROJECT')}")
    print(f"🔍 Tracing: {os.getenv('LANGSMITH_TRACING')}")
    app.run(host='0.0.0.0', port=5001, debug=True)

