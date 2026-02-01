# 🔐 AEM Username/Password Authentication

## Overview

Some AEM APIs (particularly the QueryBuilder API used for asset search) may require **username/password authentication** instead of Bearer token authentication. The chatbot now supports both methods.

## When to Use Username/Password

**Use username/password when:**
- ✅ QueryBuilder API returns 401 errors with Bearer token
- ✅ Asset search operations fail with authentication errors
- ✅ Your AEM instance requires basic authentication
- ✅ Token-based authentication is not working for certain operations

**Use Bearer token when:**
- ✅ Token has proper scopes (`assets:read`, `sites:write`, etc.)
- ✅ Token is not expired
- ✅ Token works for most operations

## Setup

### Step 1: Add Credentials to `.env`

Add these variables to your `.env` file:

```bash
# AEM Authentication (choose one method)

# Option 1: Username/Password (Recommended for QueryBuilder)
AEM_USERNAME=your-aem-username
AEM_PASSWORD=your-aem-password

# Option 2: Bearer Token (if token has proper scopes)
AEM_TOKEN=your-aem-token

# Both can be set - username/password takes precedence
```

### Step 2: Priority Order

The system uses credentials in this order:

1. **Username/Password** (if both `AEM_USERNAME` and `AEM_PASSWORD` are set)
2. **Bearer Token** (if `AEM_TOKEN` is set and username/password not available)

### Step 3: Restart Application

After updating `.env`, restart your application:

```bash
# Stop current servers (Ctrl+C)
# Then restart
./start.sh
```

## Example Configuration

**Full `.env` example:**

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...

# LangSmith
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=rag demo

# AEM Configuration
AEM_SERVER=https://author-p18253-e46622.adobeaemcloud.com

# AEM Authentication - Username/Password (for QueryBuilder)
AEM_USERNAME=admin
AEM_PASSWORD=your-password

# AEM Authentication - Bearer Token (alternative)
# AEM_TOKEN=eyJhbGc...

# MCP Server
MCP_SERVER_URL=https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server
```

## How It Works

### Automatic Credential Injection

When calling AEM tools (`aem-*`), the MCP client automatically:

1. Checks for `AEM_USERNAME` and `AEM_PASSWORD`
2. If both exist → Uses username/password authentication
3. If not → Falls back to `AEM_TOKEN` (Bearer token)
4. Passes credentials to the MCP server
5. MCP server uses them to call AEM APIs

### Code Flow

```
User Request: "Search for assets"
     ↓
MCP Client (mcp_client.py)
     ↓
Checks .env:
  - AEM_USERNAME + AEM_PASSWORD? → Use basic auth
  - AEM_TOKEN? → Use Bearer token
     ↓
Sends to MCP Server with credentials
     ↓
MCP Server calls AEM QueryBuilder API
     ↓
Returns results
```

## Troubleshooting

### Still Getting 401 Errors?

1. **Verify credentials are correct:**
   ```bash
   # Test username/password
   curl -u username:password \
     https://author-p18253-e46622.adobeaemcloud.com/bin/querybuilder.json?type=dam:Asset&path=/content/dam&p.limit=10
   ```

2. **Check if username/password is being used:**
   - Look for log messages: `🔑 Using AEM_USERNAME: ...`
   - If you see `🔑 Using AEM_TOKEN` instead, username/password is not set

3. **Ensure both variables are set:**
   - Both `AEM_USERNAME` AND `AEM_PASSWORD` must be set
   - If only one is set, it will fall back to token

### Security Notes

⚠️ **Important:**
- Never commit `.env` file to version control
- Username/password credentials are stored in `.env` (gitignored)
- Credentials are passed securely to MCP server via HTTPS
- MCP server uses credentials only for AEM API calls

### For Vercel Deployment

Add these environment variables in Vercel dashboard:

```
AEM_SERVER=https://author-p18253-e46622.adobeaemcloud.com
AEM_USERNAME=your-username
AEM_PASSWORD=your-password
```

Or use Bearer token:

```
AEM_SERVER=https://author-p18253-e46622.adobeaemcloud.com
AEM_TOKEN=your-token
```

## Testing

### Test Username/Password Authentication

```bash
# Test QueryBuilder API with username/password
curl -u your-username:your-password \
  "https://author-p18253-e46622.adobeaemcloud.com/bin/querybuilder.json?type=dam:Asset&path=/content/dam&p.limit=10"
```

**Expected:** JSON response with asset list

### Test in Chatbot

After setting credentials in `.env` and restarting:

```
User: "Search for assets with ford"
Bot: [Should work with username/password authentication]
```

## Summary

- ✅ Username/password authentication is now supported
- ✅ Automatically used if `AEM_USERNAME` and `AEM_PASSWORD` are set
- ✅ Takes precedence over Bearer token
- ✅ Recommended for QueryBuilder API operations
- ✅ Secure credential handling (stored in `.env`, gitignored)
