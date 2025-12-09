"""
Python serverless function for health check endpoint on Vercel
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model": "gpt-4o-mini",
        "runtime": "python",
        "platform": "vercel"
    })

