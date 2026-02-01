# 🔗 How the Chatbot Connects to Adobe App Builder

## Overview

Your chatbot connects to **Adobe App Builder** (specifically **Adobe I/O Runtime**) through an **MCP (Model Context Protocol) Server** that's deployed as an Adobe I/O Runtime action. This allows the chatbot to execute AEM operations and other Adobe services.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Chatbot Application                       │
│  (Python Flask API + Node.js Frontend)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTP POST (JSON-RPC 2.0)
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Client (mcp_client.py)                     │
│  - Makes JSON-RPC calls                                     │
│  - Handles authentication                                   │
│  - Manages AEM credentials                                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTPS Request
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         Adobe I/O Runtime (Adobe App Builder)              │
│  URL: *.adobeioruntime.net                                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         MCP Server Action                           │  │
│  │  /api/v1/web/my-mcp-server/mcp-server               │  │
│  │                                                      │  │
│  │  - Receives JSON-RPC requests                        │  │
│  │  - Executes AEM operations                           │  │
│  │  - Returns results                                   │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                   │
│                          │ AEM API Calls                     │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   AEM Cloud Service  │
                │   (author instance)  │
                └──────────────────────┘
```

## Connection Flow

### 1. **Initialization** (On Server Start)

When the chatbot starts (`agent_api.py` or `api/chat.py`):

```python
# Initialize MCP client with Adobe I/O Runtime URL
mcp_url = "https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server"
mcp_client = MCPClient(mcp_url)

# Check server health
if mcp_client.is_healthy():
    print("✅ MCP server connected successfully!")
    mcp_tools = mcp_client.list_tools()
```

### 2. **MCP Client** (`mcp_client.py`)

The `MCPClient` class handles all communication:

```python
class MCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url  # Adobe I/O Runtime URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        })
```

**Key Methods:**
- `list_tools()` - Gets available tools from MCP server
- `call_tool()` - Executes a tool on Adobe I/O Runtime
- `is_healthy()` - Checks if server is accessible

### 3. **JSON-RPC Protocol**

The chatbot uses **JSON-RPC 2.0** to communicate with Adobe I/O Runtime:

```python
def _call_jsonrpc(self, method: str, params: Dict = None) -> Dict:
    payload = {
        "jsonrpc": "2.0",
        "method": method,        # e.g., "tools/call"
        "params": params or {},  # Tool name and arguments
        "id": 1
    }
    
    response = self.session.post(
        self.server_url,  # Adobe I/O Runtime endpoint
        json=payload,
        timeout=30
    )
    return response.json()
```

### 4. **Tool Execution Flow**

When a user requests an AEM operation:

```
User: "List my AEM sites"
     ↓
Intelligent Agent (intelligent_agent.py)
     ↓
Detects: Tool = "aem-list-sites"
     ↓
MCP Client (mcp_client.py)
     ↓
1. Auto-injects AEM credentials from .env
2. Makes JSON-RPC call to Adobe I/O Runtime
     ↓
Adobe I/O Runtime MCP Server
     ↓
1. Receives request
2. Uses AEM credentials to call AEM API
3. Returns results
     ↓
MCP Client receives response
     ↓
Intelligent Agent formats response
     ↓
User sees: List of AEM sites
```

## Connection Details

### Adobe I/O Runtime URL

**Current MCP Server:**
```
https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server
```

**URL Structure:**
- `332794-trainingprojecty-stage` - Your Adobe I/O Runtime namespace
- `adobeioruntime.net` - Adobe I/O Runtime domain
- `/api/v1/web/my-mcp-server/mcp-server` - Your MCP server action path

### Authentication

**No Authentication Required for MCP Server:**
- The MCP server on Adobe I/O Runtime is **publicly accessible**
- No API keys or tokens needed to connect to the MCP server itself

**AEM Credentials (Injected Automatically):**
- When calling AEM tools (`aem-*`), credentials are automatically injected:
  - `AEM_SERVER` - From `.env` file
  - `AEM_TOKEN` - From `.env` file
- These are passed to the MCP server, which then uses them to call AEM APIs

### Request Format

**Example: List AEM Sites**

```json
POST https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "aem-list-sites",
    "arguments": {
      "server": "https://author-p18253-e46622.adobeaemcloud.com",
      "token": "eyJhbGc...",
      "path": "/content"
    }
  },
  "id": 1
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "List of sites..."
      }
    ]
  },
  "id": 1
}
```

## Configuration

### Environment Variables

**Required (for AEM operations):**
```bash
AEM_SERVER=https://author-p18253-e46622.adobeaemcloud.com
AEM_TOKEN=your-aem-token-here
```

**Optional (for MCP server URL):**
```bash
MCP_SERVER_URL=https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server
```

Currently, `MCP_SERVER_URL` is hardcoded in the code but can be moved to `.env` for flexibility.

### Code Locations

**MCP Server URL is defined in:**
1. `agent_api.py` (line 33) - Local development
2. `api/chat.py` (line 19) - Vercel serverless function
3. `intelligent_agent.py` (line 318) - Test code

## How Adobe I/O Runtime Works

### Adobe App Builder Components

1. **Adobe I/O Runtime** - Serverless platform (where your MCP server runs)
2. **MCP Server Action** - Your deployed action that handles tool execution
3. **AEM Integration** - The MCP server calls AEM APIs on your behalf

### Deployment Model

Your MCP server is deployed as an **Adobe I/O Runtime action**:

```
Adobe I/O Runtime Action
├── Name: my-mcp-server
├── Endpoint: /mcp-server
├── Runtime: Node.js (or Python)
└── Capabilities:
    - List available tools
    - Execute tools
    - Handle AEM API calls
    - Return results
```

## Testing the Connection

### 1. Check MCP Server Health

```bash
curl https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server
```

**Expected Response:**
```json
{
  "status": "healthy",
  "server": "my-mcp-server",
  "version": "1.0.0"
}
```

### 2. List Available Tools

```bash
curl -X POST \
  https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }'
```

### 3. Test from Python

```python
from mcp_client import MCPClient

mcp_url = "https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server"
client = MCPClient(mcp_url)

# Check health
print(client.is_healthy())

# List tools
tools = client.list_tools()
print(f"Available tools: {len(tools)}")
```

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to MCP server
- **Check:** Adobe I/O Runtime action is deployed and running
- **Verify:** URL is correct
- **Test:** `curl` the MCP server endpoint

**Problem:** 401/403 errors from AEM
- **Check:** AEM credentials in `.env` file
- **Verify:** Token has correct scopes (`sites:read`, `assets:read`, etc.)
- **Test:** Run `./test_aem_connectivity.sh`

**Problem:** Timeout errors
- **Check:** Network connectivity
- **Verify:** Adobe I/O Runtime action timeout settings
- **Increase:** Timeout in `mcp_client.py` (currently 30 seconds)

### Debugging

**Enable verbose logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check MCP server logs:**
- View logs in Adobe I/O Runtime dashboard
- Check action invocations and errors

## Security Considerations

1. **MCP Server is Public**
   - No authentication required to access MCP server
   - Consider adding authentication if needed

2. **AEM Credentials**
   - Stored securely in `.env` file (gitignored)
   - Automatically injected for AEM tools
   - Never exposed to client-side code

3. **HTTPS Only**
   - All communication uses HTTPS
   - Adobe I/O Runtime enforces HTTPS

## Summary

**Connection Path:**
```
Chatbot → MCP Client → Adobe I/O Runtime → MCP Server Action → AEM Cloud Service
```

**Key Points:**
- ✅ Uses JSON-RPC 2.0 protocol
- ✅ No authentication needed for MCP server
- ✅ AEM credentials injected automatically
- ✅ Serverless architecture (Adobe I/O Runtime)
- ✅ Public endpoint (no API keys required)

**Benefits:**
- 🚀 Serverless scaling
- 🔒 Secure credential handling
- 🛠️ Easy tool execution
- 📊 Centralized AEM operations
