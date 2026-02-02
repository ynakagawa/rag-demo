"""
Enhanced agent with automatic MCP tool execution based on user intent
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from mcp_client import MCPClient
from rag_agent import AEMRAGAgent
import json
import re
import os
import urllib.parse

class IntelligentMCPAgent:
    """Agent that can intelligently execute MCP tools based on user queries"""
    
    def __init__(self, mcp_client: MCPClient, rag_agent: AEMRAGAgent):
        self.mcp_client = mcp_client
        self.rag_agent = rag_agent
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.mcp_tools = mcp_client.list_tools()
    
    def parse_intent(self, user_message: str) -> dict:
        """
        Use LLM to determine if the user wants to execute an MCP tool
        Returns: {"should_execute": bool, "tool": str, "arguments": dict}
        """
        tools_description = "\n".join([
            f"- {tool['name']}: {tool.get('description', '')}"
            for tool in self.mcp_tools
        ])
        
        system_prompt = f"""You are an AI assistant that determines if a user wants to execute an MCP tool.

Available MCP tools:
{tools_description}

IMPORTANT: The calculator tool requires "expression" as a STRING containing the math expression.
Example: {{"expression": "5 + 3"}} NOT {{"operation": "add", "operands": [5, 3]}}

CRITICAL FOR AEM TOOLS:
- ANY request to list, create, get, delete, or manage AEM content/sites/assets = should_execute: true
- Questions phrased as "can you...", "please...", "show me..." about AEM sites/content are ACTIONS, not knowledge questions
- "What is AEM?" or "How does AEM work?" = should_execute: false (conceptual/knowledge questions)
- "List sites", "Show sites", "Can you list sites", "Get sites" = should_execute: true (action requests)

CRITICAL: You MUST extract ALL required parameters from the user's message. If a required parameter is missing, you should still include it with a reasonable default or ask for clarification.

Required parameters for AEM tools:
- aem-create-microsite: REQUIRES "siteTitle" (string) - extract the site name/title from user message
- aem-list-sites: {{"path": "/content"}} (default)
- aem-get-site-info: REQUIRES "sitePath" (string) - format as "/content/<sitename>"
- aem-delete-site: REQUIRES "sitePath" (string)
- aem-create-component: REQUIRES "componentName" (string)
- aem-create-content-fragment: REQUIRES "fragmentName" (string)
- aem-upload-asset: REQUIRES "filePath" (string) and "destinationPath" (string)
- aem-list-assets: REQUIRES "folder" (string) - DAM folder path, default to "/content/dam" if not specified
- aem-search-assets: REQUIRES "query" (string) - search query for assets

Given a user message, determine:
1. Does the user want to execute one of these tools? (yes/no)
2. Which tool should be executed?
3. What are the arguments? EXTRACT ALL REQUIRED PARAMETERS from the user's message.

Respond ONLY with a JSON object in this format:
{{
    "should_execute": true/false,
    "tool_name": "tool-name" or null,
    "arguments": {{}},
    "reasoning": "why this tool was chosen"
}}

Examples:
User: "Echo hello world"
{{
    "should_execute": true,
    "tool_name": "echo",
    "arguments": {{"message": "hello world"}},
    "reasoning": "User wants to echo a message"
}}

User: "Calculate 5 + 3" or "What is 5 plus 3"
{{
    "should_execute": true,
    "tool_name": "calculator",
    "arguments": {{"expression": "5 + 3"}},
    "reasoning": "User wants to calculate a math expression"
}}

User: "What is AEM?"
{{
    "should_execute": false,
    "tool_name": null,
    "arguments": {{}},
    "reasoning": "This is a knowledge question, not a tool execution request"
}}

User: "List my AEM sites" or "Can you list my AEM sites" or "Show me my sites"
{{
    "should_execute": true,
    "tool_name": "aem-list-sites",
    "arguments": {{"path": "/content"}},
    "reasoning": "User wants to list AEM sites - this is an action request, not a knowledge question"
}}

User: "Get info for diomicrosite"
{{
    "should_execute": true,
    "tool_name": "aem-get-site-info",
    "arguments": {{"sitePath": "/content/diomicrosite"}},
    "reasoning": "User wants to get information about a specific site"
}}

User: "Create a microsite called Product Launch" or "Create microsite Product Launch" or "Create a new microsite named Product Launch"
{{
    "should_execute": true,
    "tool_name": "aem-create-microsite",
    "arguments": {{"siteTitle": "Product Launch"}},
    "reasoning": "User wants to create a microsite - extracted siteTitle from message"
}}

User: "Create microsite MyNewSite"
{{
    "should_execute": true,
    "tool_name": "aem-create-microsite",
    "arguments": {{"siteTitle": "MyNewSite"}},
    "reasoning": "User wants to create a microsite - extracted siteTitle from message"
}}

User: "List assets" or "Show me assets" or "List assets in DAM"
{{
    "should_execute": true,
    "tool_name": "aem-list-assets",
    "arguments": {{"folder": "/content/dam"}},
    "reasoning": "User wants to list assets - using default folder /content/dam"
}}

User: "List assets in /content/dam/products" or "Show assets in products folder"
{{
    "should_execute": true,
    "tool_name": "aem-list-assets",
    "arguments": {{"folder": "/content/dam/products"}},
    "reasoning": "User wants to list assets in a specific folder - extracted folder path from message"
}}

User: "Search for logo assets" or "Find images with logo"
{{
    "should_execute": true,
    "tool_name": "aem-search-assets",
    "arguments": {{"query": "logo"}},
    "reasoning": "User wants to search for assets - extracted search query from message"
}}
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User message: {user_message}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                intent = json.loads(json_match.group())
                return intent
            return {"should_execute": False, "tool_name": None, "arguments": {}}
        except Exception as e:
            print(f"Error parsing intent: {e}")
            return {"should_execute": False, "tool_name": None, "arguments": {}}
    
    def process_message(self, user_message: str) -> dict:
        """
        Process user message and either execute MCP tool or use RAG/chat
        """
        # First, check if this might be a tool execution request
        intent = self.parse_intent(user_message)
        
        if intent.get("should_execute") and intent.get("tool_name"):
            # Execute the MCP tool
            tool_name = intent["tool_name"]
            arguments = intent.get("arguments", {})
            
            # Add default values for required parameters if missing
            if tool_name == "aem-list-assets" and "folder" not in arguments:
                arguments["folder"] = "/content/dam"
                print(f"⚠️  Missing 'folder' parameter for aem-list-assets, using default: /content/dam")
            
            print(f"🔧 Executing MCP tool: {tool_name}")
            print(f"📝 Arguments: {arguments}")
            
            result = self.mcp_client.call_tool(tool_name, arguments)
            
            if result.get("success"):
                return {
                    "response": self._format_tool_result(tool_name, result),
                    "mode": "mcp_execution",
                    "tool_executed": tool_name,
                    "tool_result": result
                }
            else:
                # Parse error message for better user feedback
                error_msg = result.get('error', 'Unknown error')
                
                # Check for nested error messages (common in MCP responses)
                error_data = result.get('error_data', {})
                if error_data and isinstance(error_data, dict):
                    nested_error = error_data.get('error') or error_data.get('message')
                    if nested_error and nested_error not in error_msg:
                        error_msg = f"{error_msg}: {nested_error}"
                
                error_response = self._format_error_response(tool_name, error_msg, arguments)
                
                return {
                    "response": error_response,
                    "mode": "mcp_error",
                    "error": error_msg,
                    "error_code": result.get('error_code'),
                    "tool_name": tool_name,
                    "arguments": arguments
                }
        
        # If not a tool execution, check if it's an AEM knowledge question
        # Only use RAG for questions about concepts, not actions
        knowledge_keywords = ['what is', 'how does', 'explain', 'what are', 'describe', 'tell me about', 'what do', 'how do']
        is_knowledge_question = any(keyword in user_message.lower() for keyword in knowledge_keywords)
        
        # Expanded AEM keywords to catch more AEM-related queries
        aem_keywords = [
            # Core terms
            'aem', 'adobe', 'experience manager',
            # Capabilities
            'sites', 'assets', 'dam', 'forms', 'headless',
            # Features
            'component', 'template', 'page', 'workflow', 'dispatcher',
            'smart tag', 'smart tags', 'metadata', 'content fragment',
            'experience fragment', 'launch', 'target', 'analytics',
            # Technical terms
            'sling', 'jcr', 'osgi', 'htl', 'sightly', 'cq',
            'author', 'publish', 'dispatcher', 'replication',
            # Cloud Service terms
            'cloud service', 'cloud manager', 'edge delivery',
            'graphql', 'content api', 'sdk', 'local dev'
        ]
        mentions_aem = any(keyword in user_message.lower() for keyword in aem_keywords)
        
        # Also check if it's a general knowledge question that might be AEM-related
        # Use LLM to determine if it's AEM-related if keywords don't match
        if is_knowledge_question and not mentions_aem and self.rag_agent.is_ready():
            # Try to determine if it's AEM-related using LLM
            aem_check_prompt = f"""Is this question about Adobe Experience Manager (AEM) or related Adobe products?
Question: "{user_message}"

Respond with only "yes" or "no"."""
            
            try:
                check_messages = [
                    SystemMessage(content="You are a classifier that determines if questions are about Adobe Experience Manager."),
                    HumanMessage(content=aem_check_prompt)
                ]
                aem_check_response = self.llm.invoke(check_messages)
                is_aem_related = "yes" in aem_check_response.content.lower()
                
                if is_aem_related:
                    mentions_aem = True
            except Exception as e:
                print(f"⚠️  Error checking AEM relevance: {e}")
        
        if is_knowledge_question and mentions_aem and self.rag_agent.is_ready():
            rag_result = self.rag_agent.query(user_message)
            return {
                "response": rag_result["answer"],
                "mode": "rag",
                "sources": rag_result.get("sources", [])
            }
        
        # Fall back to conversational mode
        return {
            "response": "I can help you with:\n\n🔧 **AEM Actions**: 'list sites', 'create microsite', 'get site info', etc.\n📚 **Knowledge**: 'What is AEM?', 'How does AEM work?', etc.\n🧮 **Tools**: 'calculate', 'echo', and more.\n\nWhat would you like to do?",
            "mode": "conversational"
        }
    
    def _format_error_response(self, tool_name: str, error_msg: str, arguments: dict) -> str:
        """Format error response with helpful guidance"""
        formatted = f"❌ **Error executing `{tool_name}`**\n\n"
        
        # Extract HTTP status codes from error message
        status_code_match = re.search(r'status code (\d+)', error_msg.lower())
        status_code = status_code_match.group(1) if status_code_match else None
        
        # Check for authentication errors (401)
        if status_code == "401" or "401" in error_msg or "unauthorized" in error_msg.lower() or "authentication" in error_msg.lower():
            formatted += "**🔐 Authentication Error (401)**\n\n"
            formatted += "The AEM credentials are invalid, expired, or insufficient.\n\n"
            
            # Provide tool-specific guidance
            if "asset" in tool_name.lower() or "dam" in tool_name.lower() or "querybuilder" in error_msg.lower():
                formatted += "**For Asset Operations (QueryBuilder API):**\n"
                formatted += "The AEM QueryBuilder API may require username/password authentication instead of Bearer token.\n"
                formatted += "Your token needs `assets:read` scope, OR use username/password authentication.\n\n"
                formatted += "**Try username/password authentication:**\n"
                formatted += "1. Add to your `.env` file:\n"
                formatted += "   ```\n"
                formatted += "   AEM_USERNAME=your-aem-username\n"
                formatted += "   AEM_PASSWORD=your-aem-password\n"
                formatted += "   ```\n"
                formatted += "2. The system will automatically use username/password if available\n"
                formatted += "3. Username/password takes precedence over token for QueryBuilder API\n\n"
            elif "site" in tool_name.lower() or "microsite" in tool_name.lower():
                formatted += "**For Site Operations:**\n"
                formatted += "Your token needs `sites:read` and `sites:write` scopes.\n\n"
            elif "component" in tool_name.lower() or "content" in tool_name.lower():
                formatted += "**For Content Operations:**\n"
                formatted += "Your token needs `content:read` and `content:write` scopes.\n\n"
            
            formatted += "**Possible causes:**\n"
            formatted += "- AEM token has expired (tokens typically expire after 24 hours)\n"
            formatted += "- Invalid AEM token format\n"
            formatted += "- AEM server URL is incorrect\n"
            formatted += "- Token missing required scopes for this operation\n"
            formatted += "- AEM instance is not accessible\n\n"
            formatted += "**How to fix:**\n"
            
            # Check if QueryBuilder is mentioned (often needs username/password)
            if "querybuilder" in error_msg.lower() or ("asset" in tool_name.lower() and "401" in error_msg):
                formatted += "**Option 1: Use Username/Password (Recommended for QueryBuilder)**\n"
                formatted += "1. Add to your `.env` file:\n"
                formatted += "   ```\n"
                formatted += "   AEM_USERNAME=your-aem-username\n"
                formatted += "   AEM_PASSWORD=your-aem-password\n"
                formatted += "   ```\n"
                formatted += "2. Restart the application\n"
                formatted += "3. Username/password will be used automatically\n\n"
                formatted += "**Option 2: Fix Bearer Token**\n"
            else:
                formatted += "**Option 1: Fix Bearer Token**\n"
            
            formatted += "1. Check your `.env` file has correct `AEM_SERVER` and `AEM_TOKEN`\n"
            formatted += "2. Generate a new AEM token from Adobe Developer Console\n"
            
            if "asset" in tool_name.lower():
                formatted += "3. Ensure token includes `assets:read` scope (and `assets:write` for uploads)\n"
            elif "site" in tool_name.lower():
                formatted += "3. Ensure token includes `sites:read` and `sites:write` scopes\n"
            else:
                formatted += "3. Verify the token has permissions for this operation\n"
            
            formatted += "4. Test AEM connectivity: `./test_aem_connectivity.sh`\n"
            formatted += "5. Check token scopes: `python check_token_scopes.py`\n\n"
            formatted += "**Note:** AEM tokens typically expire after 24 hours. You may need to refresh your token.\n"
            formatted += "See `AEM_PERMISSIONS_FIX.md` for detailed instructions.\n"
        
        # Check for validation errors
        elif "validation error" in error_msg.lower() or "invalid arguments" in error_msg.lower():
            formatted += "**Missing or invalid parameters detected.**\n\n"
            
            # Try to extract missing parameter info from error
            missing_params = re.findall(r'"([^"]+)"[^"]*"Required"', error_msg)
            if missing_params:
                formatted += f"**Missing required parameters:**\n"
                for param in missing_params:
                    formatted += f"- `{param}`\n"
                formatted += "\n"
            
            # Provide guidance based on tool
            if tool_name == "aem-create-microsite":
                formatted += "💡 **To create a microsite, please specify a site title.**\n"
                formatted += "Example: \"Create a microsite called MyNewSite\" or \"Create microsite Product Launch\"\n"
            elif tool_name == "aem-get-site-info":
                formatted += "💡 **Please specify the site path.**\n"
                formatted += "Example: \"Get info for diomicrosite\" or \"Get site info for /content/mysite\"\n"
            elif tool_name == "aem-create-component":
                formatted += "💡 **Please specify the component name.**\n"
                formatted += "Example: \"Create a component called Header\"\n"
        
        # Check for other common errors
        elif status_code == "409" or "already exists" in error_msg.lower() or "409" in error_msg:
            formatted += "**⚠️ Resource Already Exists**\n\n"
            formatted += "The microsite or resource you're trying to create already exists.\n"
            formatted += "Try using a different name or delete the existing resource first.\n"
        
        elif status_code == "404" or "404" in error_msg or "not found" in error_msg.lower():
            formatted += "**🔍 Resource Not Found**\n\n"
            formatted += "The requested AEM resource could not be found.\n"
            formatted += "Verify the resource path or name is correct.\n"
        
        elif status_code == "403":
            formatted += "**🚫 Forbidden (403)**\n\n"
            formatted += "You don't have permission to perform this operation.\n"
            formatted += "Verify your AEM token has the necessary permissions.\n"
        
        elif status_code == "500" or status_code == "502" or status_code == "503":
            formatted += "**⚠️ Server Error**\n\n"
            formatted += "The AEM server encountered an error.\n"
            formatted += "This may be a temporary issue. Please try again later.\n"
        
        else:
            # Generic error handling
            formatted += "**Error Details:**\n"
        
        formatted += f"\n**Error message:** {error_msg}\n"
        
        # Only show arguments if not an auth error (for security)
        if "401" not in error_msg and "unauthorized" not in error_msg.lower():
            formatted += f"\n**Provided arguments:** {arguments}"
        
        return formatted
    
    def _format_tool_result(self, tool_name: str, result: dict) -> str:
        """Format the tool execution result for display"""
        content = result.get("result", {}).get("content", [])
        metadata = result.get("result", {}).get("metadata", {})
        
        formatted = f"✅ **Tool Executed:** `{tool_name}`\n\n"
        
        # Special handling for asset search results
        if tool_name == "aem-search-assets" and metadata.get("results"):
            assets = metadata.get("results", [])
            total = metadata.get("total", 0)
            
            formatted += f"🔍 **Found {len(assets)} asset(s) (Total: {total})**\n\n"
            formatted += "📑 **Results:**\n\n"
            formatted += "<div class='asset-grid'>\n"
            
            # Use Scene7 Dynamic Media base URL
            scene7_base = os.getenv("SCENE7_BASE_URL", "https://s7d9.scene7.com/is/image/CEM/")
            # Ensure Scene7 base URL ends with /
            if scene7_base and not scene7_base.endswith("/"):
                scene7_base += "/"
            
            for asset in assets:
                # Extract asset information - handle various possible field names
                asset_path = asset.get("path") or asset.get("jcr:path") or asset.get("dam:path") or ""
                asset_name = asset.get("name") or asset.get("jcr:name") or asset.get("dam:name") or "Unknown"
                asset_title = asset.get("title") or asset.get("jcr:title") or asset.get("dc:title") or asset_name
                thumbnail_url = asset.get("thumbnail") or asset.get("thumbnailUrl") or asset.get("rendition") or ""
                asset_type = asset.get("type") or asset.get("jcr:primaryType") or asset.get("mimeType") or ""
                
                # Build thumbnail URL if not provided
                if not thumbnail_url:
                    # Try to extract asset identifier from various fields
                    asset_id = asset.get("scene7Id") or asset.get("dynamicMediaId") or asset.get("id") or ""
                    
                    # If no explicit Scene7 ID, derive from asset name or path
                    if not asset_id:
                        # Extract filename from path or use name
                        if asset_path:
                            # Extract filename from path (e.g., /content/dam/path/to/file.jpg -> file)
                            path_parts = asset_path.split("/")
                            filename = path_parts[-1] if path_parts else asset_name
                            # Remove file extension
                            if "." in filename:
                                asset_id = filename.rsplit(".", 1)[0]
                            else:
                                asset_id = filename
                        else:
                            # Use asset name, remove extension if present
                            if "." in asset_name:
                                asset_id = asset_name.rsplit(".", 1)[0]
                            else:
                                asset_id = asset_name
                    
                    # Construct Dynamic Media thumbnail URL
                    # Format: {aem_server}/is/image/CEM/{asset_id}?$thumbnail$&fmt=jpeg,rgb
                    if asset_id:
                        # URL encode the asset ID (handle spaces, special chars)
                        encoded_id = urllib.parse.quote(asset_id, safe='')
                        # Build query string - $ characters need to be URL encoded as %24
                        # Note: The & will be HTML-escaped to &amp; when inserted into HTML
                        thumbnail_url = f"{scene7_base}{encoded_id}?%24thumbnail%24&fmt=jpeg,rgb"
                
                # Escape HTML in text fields to prevent XSS
                def escape_html(text):
                    if not text:
                        return ""
                    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
                
                formatted += "<div class='asset-thumbnail'>\n"
                if thumbnail_url:
                    # For img src in HTML, we need to HTML-escape & to &amp;
                    # The thumbnail_url already has proper URL encoding (%24 for $, etc.)
                    # When HTML-escaped, & becomes &amp; which browsers handle correctly
                    escaped_url = escape_html(thumbnail_url)
                    escaped_title = escape_html(asset_title)
                    # Use double quotes for src to avoid conflicts with single quotes
                    # Add error handler to show placeholder if image fails to load
                    formatted += f"  <img src=\"{escaped_url}\" alt=\"{escaped_title}\" class=\"asset-image\" onerror=\"this.style.display='none'; this.nextElementSibling.style.display='flex';\"/>\n"
                    formatted += f"  <div class='asset-placeholder' style='display:none;'>📄</div>\n"
                else:
                    formatted += f"  <div class='asset-placeholder'>📄</div>\n"
                formatted += "  <div class='asset-info'>\n"
                formatted += f"    <div class='asset-title'>{escape_html(asset_title)}</div>\n"
                if asset_type:
                    formatted += f"    <div class='asset-type'>{escape_html(asset_type)}</div>\n"
                if asset_path:
                    # Trim /content/dam prefix from path for display
                    display_path = asset_path
                    if display_path.startswith("/content/dam"):
                        display_path = display_path[len("/content/dam"):]
                    elif display_path.startswith("content/dam"):
                        display_path = display_path[len("content/dam"):]
                    formatted += f"    <div class='asset-path'>{escape_html(display_path)}</div>\n"
                formatted += "  </div>\n"
                formatted += "</div>\n"
            
            formatted += "</div>\n\n"
            
            # Skip content items since we've already formatted assets from metadata
            # The asset grid above contains both images and metadata, so skip any duplicate content
            # Only add non-asset-related summary text if needed
            if content:
                for item in content:
                    # Skip image items - we've already rendered them in the asset grid
                    if item.get("type") == "image":
                        continue
                    if item.get("type") == "text":
                        text = item.get('text', '')
                        # Skip content that contains asset-related information we've already formatted
                        # Only include additional context that isn't duplicate
                        text_lower = text.lower()
                        skip_patterns = ["found:", "asset", "thumbnail", "path:", "type:", "title:"]
                        is_duplicate = any(pattern in text_lower for pattern in skip_patterns)
                        if not is_duplicate and text.strip():
                            formatted += f"{text}\n"
        else:
            # Standard formatting for other tools
            if content:
                for item in content:
                    if item.get("type") == "text":
                        formatted += f"{item.get('text', '')}\n"
                    elif item.get("type") == "image":
                        formatted += f"🖼️ Image: {item.get('data', '')[:100]}...\n"
            else:
                formatted += "Tool executed successfully (no output)"
        
        return formatted

# Test the intelligent agent
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    import os
    
    print("🧪 Testing Intelligent MCP Agent")
    print("=" * 60)
    
    # Initialize clients
    mcp_url = os.getenv('MCP_SERVER_URL', 'https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server')
    mcp_client = MCPClient(mcp_url)
    rag_agent = AEMRAGAgent()
    
    # Create intelligent agent
    agent = IntelligentMCPAgent(mcp_client, rag_agent)
    
    # Test cases
    test_messages = [
        "Echo hello world",
        "What is Adobe Experience Manager?",
        "Calculate 5 + 3",
        "List my AEM sites",
    ]
    
    for message in test_messages:
        print(f"\n📤 User: {message}")
        print("-" * 60)
        
        result = agent.process_message(message)
        
        print(f"🤖 Mode: {result.get('mode')}")
        print(f"💬 Response: {result.get('response')[:200]}...")
        
        if result.get('tool_executed'):
            print(f"🔧 Tool Executed: {result['tool_executed']}")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete")
