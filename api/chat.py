"""
Python serverless function for chat endpoint on Vercel
Uses LangChain with full Python support
"""
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import os

app = Flask(__name__)

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini", 
    temperature=0.7,
    openai_api_key=os.environ.get('OPENAI_API_KEY')
)

# In-memory conversation storage (in production, use a database)
conversations = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with LangChain"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Get or create conversation history
        if session_id not in conversations:
            conversations[session_id] = []
        
        # Add user message to history
        conversations[session_id].append(HumanMessage(content=user_message))
        
        # Get response from LLM (LangSmith will trace this)
        response = llm.invoke(conversations[session_id])
        
        # Add AI response to history
        conversations[session_id].append(response)
        
        # Keep only last 10 messages
        if len(conversations[session_id]) > 10:
            conversations[session_id] = conversations[session_id][-10:]
        
        return jsonify({
            "response": response.content,
            "session_id": session_id
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

