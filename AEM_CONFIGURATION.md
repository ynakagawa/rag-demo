# AEM Configuration for MCP Tools

## ✅ Automatic Credential Injection

All AEM tools (`aem-*`) automatically use credentials from your `.env` file.

### Environment Variables Required

Add these to your `.env` file:

```bash
# AEM Instance Configuration
AEM_SERVER=https://author-p18253-e46622.adobeaemcloud.com
AEM_TOKEN=your-aem-authentication-token
```

### How It Works

1. **Automatic Detection**: Any tool starting with `aem-` is detected
2. **Credential Injection**: `AEM_SERVER` and `AEM_TOKEN` are automatically added to the request
3. **No Manual Config**: You never need to pass credentials manually

### Supported Tools

All 9 AEM tools automatically use these credentials:

✅ **Site Management:**
- `aem-create-microsite` - Create microsites
- `aem-list-templates` - List templates
- `aem-list-sites` - List all sites
- `aem-get-site-info` - Get site details
- `aem-delete-site` - Delete sites

✅ **Content & Assets:**
- `aem-create-component` - Create components
- `aem-create-content-fragment` - Manage content fragments
- `aem-upload-asset` - Upload to DAM
- `aem-start-workflow` - Start workflows

### Example Usage

Just ask naturally - credentials are added automatically:

```
list sites
```
→ Automatically uses `AEM_SERVER` and `AEM_TOKEN`

```
create a microsite called MyNewSite
```
→ Automatically authenticated with your AEM instance

```
get info for diomicrosite
```
→ Credentials injected automatically

### Configuration File

**Location:** `/Users/ynaka/Documents/RAG-demo/.env`

**Current Configuration:**
```bash
AEM_SERVER=https://author-p18253-e46622.adobeaemcloud.com
AEM_TOKEN=eyJhbGc... (1346 characters)
```

### Verification

To verify credentials are loaded:

```bash
cd /Users/ynaka/Documents/RAG-demo
source venv/bin/activate
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('AEM_SERVER:', os.getenv('AEM_SERVER'))
print('AEM_TOKEN:', 'Set' if os.getenv('AEM_TOKEN') else 'Not set')
"
```

### Security Notes

✅ **Secure:**
- Credentials stored in `.env` file (gitignored)
- Never exposed to frontend/browser
- Only backend has access
- Tokens are masked in logs

⚠️ **Important:**
- Never commit `.env` to git
- Rotate tokens regularly
- Use service accounts for production

### Testing

Test that credentials work:

```bash
# Via API
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"list sites","session_id":"test"}'

# Via browser
Go to http://localhost:3000
Type: "list sites"
```

Expected result: Shows your AEM sites (not "Authentication Required")

### Troubleshooting

**Issue:** "Authentication Required" error

**Solutions:**
1. Check `.env` file has `AEM_SERVER` and `AEM_TOKEN`
2. Restart backend: `pkill -f 'python agent_api.py' && ./start.sh`
3. Verify credentials are valid (not expired)
4. Check AEM instance is accessible

**Issue:** Token expired

**Solution:**
1. Get new token from AEM Developer Console
2. Update `AEM_TOKEN` in `.env`
3. Restart backend

### For Production (Vercel)

Add environment variables in Vercel dashboard:

1. Go to Vercel project settings
2. Environment Variables section
3. Add:
   - `AEM_SERVER` = your AEM URL
   - `AEM_TOKEN` = your AEM token

The same auto-injection works on Vercel!

### Code Implementation

The automatic injection happens in `mcp_client.py`:

```python
def call_tool(self, tool_name: str, arguments: Dict = None):
    # Auto-inject for all aem-* tools
    if tool_name.startswith('aem-'):
        arguments['server'] = os.getenv('AEM_SERVER')
        arguments['token'] = os.getenv('AEM_TOKEN')
    
    # Execute tool with credentials
    return self._call_jsonrpc("tools/call", {
        "name": tool_name,
        "arguments": arguments
    })
```

### Status

✅ **Currently Configured:**
- AEM_SERVER: https://author-p18253-e46622.adobeaemcloud.com
- AEM_TOKEN: Set (1346 chars)
- Auto-injection: Enabled
- All AEM tools: Ready

### Success Example

```
User: "list sites"
System: Detects aem-list-sites tool
System: Auto-injects AEM_SERVER and AEM_TOKEN
MCP Server: Connects to AEM
Result: ✅ Found 16 sites!
```

**Your AEM tools are now fully configured and ready to use!** 🎉
