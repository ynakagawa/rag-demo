# 🔧 MCP Integration Guide

## Overview

Your RAG chatbot is now integrated with your **Adobe I/O Runtime MCP Server**, giving it access to 12 powerful AEM tools for automated operations!

**MCP Server:** https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server

## 🛠️ Available MCP Tools

Your chatbot now has access to these 12 Adobe Experience Manager tools:

### Core Tools
1. **echo** - Test connectivity and server response
2. **calculator** - Perform mathematical calculations
3. **weather** - Get weather information for any city

### AEM Site Management
4. **aem-create-microsite** - Create new microsites using Quick Site Creation templates
5. **aem-list-templates** - List available AEM Quick Site Creation templates
6. **aem-list-sites** - List existing AEM sites
7. **aem-get-site-info** - Get detailed information about an AEM site
8. **aem-delete-site** - Delete an AEM site (use with caution!)

### AEM Content & Assets
9. **aem-create-component** - Create new AEM components with dialog and HTL template
10. **aem-create-content-fragment** - Create and manage AEM Content Fragments
11. **aem-upload-asset** - Upload digital assets to AEM DAM
12. **aem-start-workflow** - Start AEM workflows for content approval or processing

## 🏗️ Architecture

```
User Question
     ↓
┌────────────────────────────────────────┐
│   Intelligent Router                   │
├────────────────────────────────────────┤
│ 1. AEM Knowledge? → RAG (Docs)        │
│ 2. Action Request? → MCP (Tools)      │
│ 3. General Chat? → Conversational AI  │
└────────────────────────────────────────┘
     ↓                ↓              ↓
┌─────────┐    ┌──────────┐   ┌──────────┐
│   RAG   │    │   MCP    │   │   Chat   │
│ (Docs)  │    │ (Tools)  │   │   (AI)   │
└─────────┘    └──────────┘   └──────────┘
     ↓                ↓              ↓
   Answer         Action         Response
```

## 🚀 How to Use

### 1. Ask Knowledge Questions (Uses RAG)
```
User: "What is Adobe Experience Manager?"
Bot: [Answers using indexed documentation with sources]
```

### 2. Request Actions (Can Use MCP Tools)
```
User: "Create a new AEM microsite"
Bot: [Suggests available MCP tools and can execute them]
```

### 3. General Conversation
```
User: "Hello, how are you?"
Bot: [Normal conversation]
```

## 📡 API Endpoints

### Health Check with MCP Status
```bash
GET http://localhost:5001/health

Response:
{
  "status": "healthy",
  "model": "gpt-4o-mini",
  "rag_ready": true,
  "mcp_connected": true,
  "mcp_tools": 12
}
```

### List Available MCP Tools
```bash
GET http://localhost:5001/mcp/tools

Response:
{
  "tools": [...],
  "count": 12
}
```

### Execute MCP Tool
```bash
POST http://localhost:5001/mcp/execute
Content-Type: application/json

{
  "tool_name": "echo",
  "arguments": {
    "message": "Hello MCP!"
  }
}
```

## 💬 Example Conversations

### Example 1: Knowledge Query
```
You: "What are AEM components?"
Bot: [Provides detailed answer from RAG documentation]
     📚 Sources: experience-manager-docs
     
     🔧 MCP Tools Available:
     I have access to 12 Adobe I/O Runtime tools including:
     - aem-create-component
     - aem-list-sites
     - aem-create-microsite
     
     Would you like me to use any of these tools?
```

### Example 2: List AEM Sites
```
You: "List my AEM sites"
Bot: I can help you with that! I have access to the 'aem-list-sites' tool.
     [Can execute: mcp_client.call_tool("aem-list-sites", {...})]
```

### Example 3: Create Microsite
```
You: "Create a new microsite called 'Product Launch'"
Bot: I can create an AEM microsite using the 'aem-create-microsite' tool.
     [Can execute with parameters]
```

## 🔧 MCP Client Implementation

The integration is powered by `mcp_client.py`:

```python
from mcp_client import MCPClient

# Initialize client
mcp_client = MCPClient(
    "https://332794-trainingprojecty-stage.adobeioruntime.net/..."
)

# List tools
tools = mcp_client.list_tools()

# Execute a tool
result = mcp_client.call_tool("echo", {"message": "Hello!"})
```

## 📊 Integration Status

### What's Integrated
- ✅ MCP client connected to Adobe I/O Runtime
- ✅ 12 tools discovered and available
- ✅ Health check includes MCP status
- ✅ New endpoints for MCP operations
- ✅ Intelligent routing based on query type

### Current Capabilities
- ✅ List all available MCP tools
- ✅ Execute any MCP tool via API
- ✅ Detect when user might want to use tools
- ✅ Suggest relevant tools in responses

### Future Enhancements
- 🔄 Automatic tool selection based on intent
- 🔄 Tool chaining (use multiple tools in sequence)
- 🔄 Natural language to tool arguments mapping
- 🔄 Tool execution in chat interface
- 🔄 Visual feedback for tool execution

## 🧪 Testing the Integration

### Test 1: Check MCP Server Health
```bash
python mcp_client.py
```

Expected output:
```
✅ Status: healthy
✅ Found 12 tools
✅ Found 3 resources
```

### Test 2: Test via API
```bash
curl http://localhost:5001/health | jq .
```

Expected:
```json
{
  "status": "healthy",
  "mcp_connected": true,
  "mcp_tools": 12
}
```

### Test 3: List MCP Tools
```bash
curl http://localhost:5001/mcp/tools | jq .
```

### Test 4: Execute Echo Tool
```bash
curl -X POST http://localhost:5001/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"echo","arguments":{"message":"Testing!"}}'
```

## 🔐 Security Notes

1. **MCP Server is Public**
   - Your MCP server URL is accessible
   - Ensure proper authentication is in place
   - Consider adding API keys or tokens

2. **Tool Execution**
   - Some tools modify AEM content (create, delete)
   - Add confirmation flows for destructive operations
   - Log all tool executions

3. **Rate Limiting**
   - Consider adding rate limits for tool execution
   - Monitor usage via LangSmith

## 📚 Resources Available

Your MCP server also provides 3 resources:
1. **example://resource1** - Example Resource 1
2. **docs://api** - API Documentation
3. **config://settings** - Configuration Settings

Access via:
```python
resources = mcp_client.list_resources()
content = mcp_client.read_resource("docs://api")
```

## 🚀 Deployment

### Local Development
- ✅ Already configured
- MCP client loads on server start
- All tools available immediately

### Vercel Deployment
Add to your environment variables:
```bash
MCP_SERVER_URL=https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server
```

The Python serverless functions will connect to MCP automatically.

## 🎯 Next Steps

1. **Add Natural Language Tool Selection**
   - Use LLM to map user intent to tools
   - Example: "create a site" → aem-create-microsite

2. **Add Tool Execution UI**
   - Show tool parameters in chat
   - Add confirmation buttons
   - Display execution results

3. **Implement Tool Chaining**
   - Execute multiple tools in sequence
   - Example: list templates → create site → get site info

4. **Add Tool History**
   - Track tool executions
   - Show recent actions
   - Undo functionality

5. **Enhanced Error Handling**
   - Better error messages
   - Retry logic
   - Fallback strategies

## 📖 Learn More

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Adobe I/O Runtime Docs](https://developer.adobe.com/runtime/docs/)
- [Your MCP Server Health](https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server)

---

Your RAG chatbot now has **superpowers** with 12 AEM tools at its disposal! 🚀
