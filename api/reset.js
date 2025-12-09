/**
 * Vercel Serverless Function for Reset API
 */

// In-memory conversation storage (shared with chat.js in theory, but in practice each function is isolated)
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
    const { session_id = 'default' } = req.body;

    if (conversations.has(session_id)) {
      conversations.delete(session_id);
    }

    return res.status(200).json({
      message: 'Conversation reset',
      session_id,
    });
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({
      error: 'Failed to reset conversation',
      details: error.message,
    });
  }
}

