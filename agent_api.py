"""
Flask API wrapper for the LangChain agent with RAG support
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from rag_agent import AEMRAGAgent
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

# Store conversation history (in production, use a proper database)
conversation_history = {}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "model": "gpt-4o-mini"})

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
        
        # Check if question is AEM-related
        aem_keywords = ['aem', 'adobe', 'experience manager', 'dispatcher', 'component', 'sling', 'jcr', 'dam', 'assets', 'sites', 'forms']
        is_aem_question = any(keyword in user_message.lower() for keyword in aem_keywords)
        
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
            
            return jsonify({
                "response": response_text,
                "session_id": session_id,
                "mode": "rag",
                "sources": result.get("sources", [])
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

