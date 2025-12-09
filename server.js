/**
 * Node.js Express Server for Chatbot Interface
 */
const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Use environment variable for API URL (for Vercel deployment)
// In Vercel, this will be the same domain; locally it's the Python backend
const PYTHON_API_URL = process.env.API_URL || 'http://localhost:5001';

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Set views directory explicitly for Vercel
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// Routes
app.get('/', (req, res) => {
    res.render('chat', { 
        title: 'LangChain AI Chatbot'
    });
});

// Proxy endpoint to Python API (or local Vercel functions)
app.post('/api/chat', async (req, res) => {
    try {
        // If running on Vercel, the API routes are handled by serverless functions
        // This proxy is mainly for local development with Python backend
        const response = await axios.post(`${PYTHON_API_URL}/chat`, req.body, {
            timeout: 30000, // 30 second timeout
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error calling API:', error.message);
        res.status(500).json({ 
            error: 'Failed to get response from agent',
            details: error.message 
        });
    }
});

app.post('/api/reset', async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_API_URL}/reset`, req.body, {
            timeout: 5000,
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error resetting conversation:', error.message);
        res.status(500).json({ 
            error: 'Failed to reset conversation',
            details: error.message 
        });
    }
});

// Health check
app.get('/health', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API_URL}/health`, {
            timeout: 5000,
        });
        res.json({ 
            status: 'healthy',
            backend: response.data 
        });
    } catch (error) {
        res.status(503).json({ 
            status: 'unhealthy',
            error: 'Backend not available',
            details: error.message
        });
    }
});

app.listen(PORT, () => {
    console.log(`🚀 Node.js server running on http://localhost:${PORT}`);
    console.log(`📡 Connecting to Python backend at ${PYTHON_API_URL}`);
    console.log(`\n💡 Make sure to start the Python backend first:`);
    console.log(`   cd ${__dirname} && source venv/bin/activate && python agent_api.py`);
});

