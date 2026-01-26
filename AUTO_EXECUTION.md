# 🚀 Automatic MCP Tool Execution - NOW ENABLED!

## ✅ What's New

Your chatbot now **automatically executes MCP tools** based on user intent! No more manual tool selection - just ask naturally and the bot will execute the right tool.

## 🎯 How It Works

```
User: "Echo hello world"
     ↓
Intent Parser (LLM)
     ↓
Detects: Tool=echo, Args={message: "hello world"}
     ↓
Auto-Execute MCP Tool
     ↓
✅ Response: "Echo: hello world"
```

## 💬 Example Conversations

### ✅ Tool Execution (Automatic!)

**User:** "Echo hello world"
**Bot:** ✅ **Tool Executed:** `echo`
      Echo: hello world

**User:** "Calculate 5 + 3"
**Bot:** ✅ **Tool Executed:** `calculator`
      Result: 8

**User:** "What's the weather in San Francisco?"
**Bot:** ✅ **Tool Executed:** `weather`
      Current weather: Sunny, 72°F

### 📚 Knowledge Questions (RAG)

**User:** "What is Adobe Experience Manager?"
**Bot:** [Detailed answer from documentation with sources]

### 🔧 AEM Operations

**User:** "List my AEM sites"
**Bot:** ✅ **Tool Executed:** `aem-list-sites`
      [Lists sites from AEM]

**User:** "Create a new AEM component called Header"
**Bot:** ✅ **Tool Executed:** `aem-create-component`
      [Creates component]

## 🛠️ Available Auto-Execution Tools

All 12 MCP tools can be auto-executed:

### Core Tools
- ✅ **echo** - Test messages
- ✅ **calculator** - Math calculations
- ✅ **weather** - Weather information

### AEM Site Management
- ✅ **aem-create-microsite** - Create microsites
- ✅ **aem-list-templates** - List templates
- ✅ **aem-list-sites** - List sites
- ✅ **aem-get-site-info** - Get site details
- ✅ **aem-delete-site** - Delete sites

### AEM Content & Assets
- ✅ **aem-create-component** - Create components
- ✅ **aem-create-content-fragment** - Manage content
- ✅ **aem-upload-asset** - Upload assets
- ✅ **aem-start-workflow** - Start workflows

## 🧠 Intelligent Routing

The system uses an LLM-powered intent parser that:

1. **Analyzes** your message
2. **Determines** if you want to execute a tool
3. **Selects** the right tool
4. **Extracts** arguments from your message
5. **Executes** the tool automatically
6. **Formats** the response nicely

## 📡 API Usage

### With Auto-Execution (Default)

```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Echo testing!",
    "session_id": "user123"
  }'

Response:
{
  "response": "✅ **Tool Executed:** echo\n\nEcho: testing!",
  "mode": "mcp_execution",
  "tool_executed": "echo",
  "session_id": "user123"
}
```

### Without Auto-Execution (Manual Mode)

```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Echo testing!",
    "session_id": "user123",
    "auto_execute": false
  }'
```

## 🎨 Response Modes

The system automatically switches between 3 modes:

| Mode | When | Example |
|------|------|---------|
| **mcp_execution** | Tool execution request | "Echo hello" → Runs echo tool |
| **rag** | AEM knowledge question | "What is AEM?" → Returns docs |
| **conversational** | General chat | "Hello!" → Chat response |

## 🔧 Configuration

### Enable/Disable Auto-Execution

In chat interface or API:
```javascript
// Enable (default)
{
  "message": "your message",
  "auto_execute": true
}

// Disable
{
  "message": "your message",
  "auto_execute": false
}
```

## 🧪 Testing

### Test via Chat Interface
1. Go to http://localhost:3000
2. Try these commands:
   - "Echo hello world"
   - "Calculate 15 + 27"
   - "What is AEM Dispatcher?"

### Test via API
```bash
# Test echo
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Echo automated execution works!","session_id":"test"}'

# Test calculator  
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Calculate 42 / 6","session_id":"test"}'

# Test RAG
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What are AEM components?","session_id":"test"}'
```

## 📊 Response Format

### Tool Execution Success
```json
{
  "response": "✅ **Tool Executed:** `echo`\n\nEcho: your message",
  "mode": "mcp_execution",
  "tool_executed": "echo",
  "session_id": "user123",
  "sources": []
}
```

### RAG Knowledge Response
```json
{
  "response": "Adobe Experience Manager is...",
  "mode": "rag",
  "tool_executed": null,
  "session_id": "user123",
  "sources": [...]
}
```

### Tool Execution Error
```json
{
  "response": "❌ Error executing tool: ...",
  "mode": "mcp_error",
  "error": "error details"
}
```

## ⚠️ Important Notes

### Authentication for AEM Tools
Some AEM tools require authentication:
- **aem-list-sites** - Requires AEM credentials
- **aem-create-microsite** - Requires AEM credentials
- **aem-upload-asset** - Requires AEM credentials

You'll need to provide:
- AEM server URL
- Username/password or token

### Tool Limitations
- **calculator** - Requires `expression` as string format
- **weather** - Uses mock data (no real API key)
- **AEM tools** - Need valid AEM instance

## 🎯 Best Practices

1. **Be specific**: "Echo hello" works better than "say hello"
2. **Use action verbs**: "Calculate", "List", "Create", "Upload"
3. **Provide context**: "Calculate 5 + 3" includes the expression
4. **Check responses**: Tool execution results show in formatted output

## 🚀 Try It Now!

Go to **http://localhost:3000** and try:

1. **"Echo testing automatic execution!"**
   - Should execute echo tool automatically

2. **"Calculate 10 * 5 + 2"**
   - Should execute calculator tool

3. **"What is Adobe Experience Manager?"**
   - Should use RAG documentation

4. **"List my AEM sites"**
   - Should attempt aem-list-sites tool
   - May require auth credentials

---

**Your MCP tools are now fully automated!** 🎉

The chatbot intelligently decides whether to:
- 🔧 Execute a tool
- 📚 Answer from documentation
- 💬 Have a conversation

All automatically, with no manual intervention needed!
