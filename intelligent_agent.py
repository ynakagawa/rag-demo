"""
Enhanced agent with automatic MCP tool execution based on user intent
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from mcp_client import MCPClient
from rag_agent import AEMRAGAgent
import json
import re

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
        knowledge_keywords = ['what is', 'how does', 'explain', 'what are', 'describe', 'tell me about']
        is_knowledge_question = any(keyword in user_message.lower() for keyword in knowledge_keywords)
        
        aem_keywords = ['aem', 'adobe', 'experience manager', 'dispatcher', 'component']
        mentions_aem = any(keyword in user_message.lower() for keyword in aem_keywords)
        
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
            if "asset" in tool_name.lower() or "dam" in tool_name.lower():
                formatted += "**For Asset Operations:**\n"
                formatted += "Your token needs `assets:read` scope for searching assets.\n\n"
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
        
        formatted = f"✅ **Tool Executed:** `{tool_name}`\n\n"
        
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
    
    print("🧪 Testing Intelligent MCP Agent")
    print("=" * 60)
    
    # Initialize clients
    mcp_url = "https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server"
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
