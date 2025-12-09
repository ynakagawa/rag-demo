/**
 * Vercel Serverless Function for Chat API
 * This replaces the Python backend when deployed to Vercel
 */

// Import OpenAI SDK
const OpenAI = require('openai');

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// In-memory conversation storage (use a database in production)
const conversations = new Map();

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message, session_id = 'default' } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'No message provided' });
    }

    // Get or create conversation history
    if (!conversations.has(session_id)) {
      conversations.set(session_id, []);
    }

    const history = conversations.get(session_id);

    // Add user message to history
    history.push({
      role: 'user',
      content: message,
    });

    // Call OpenAI API
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: history,
      temperature: 0.7,
    });

    const assistantMessage = completion.choices[0].message.content;

    // Add assistant response to history
    history.push({
      role: 'assistant',
      content: assistantMessage,
    });

    // Keep only last 10 messages
    if (history.length > 10) {
      conversations.set(session_id, history.slice(-10));
    }

    return res.status(200).json({
      response: assistantMessage,
      session_id,
    });
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({
      error: 'Failed to get response from AI',
      details: error.message,
    });
  }
}

