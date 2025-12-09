"""
Python serverless function for reset endpoint on Vercel
"""
from flask import Flask, request, jsonify

app = Flask(__name__)

# Shared conversation storage
conversations = {}

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset conversation history"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id in conversations:
            conversations[session_id] = []
        
        return jsonify({
            "message": "Conversation reset",
            "session_id": session_id
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

