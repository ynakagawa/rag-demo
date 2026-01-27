"""
MCP Client for Adobe I/O Runtime MCP Server
Integrates with the RAG chatbot to provide additional tools and resources
"""
import json
import requests
from typing import Dict, List, Any, Optional
import os

class MCPClient:
    """Client for interacting with MCP servers"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        })
        
    def _call_jsonrpc(self, method: str, params: Dict = None) -> Dict:
        """Make a JSON-RPC call to the MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        
        try:
            response = self.session.post(
                self.server_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }
    
    def list_tools(self) -> List[Dict]:
        """List all available tools from the MCP server"""
        result = self._call_jsonrpc("tools/list")
        if "error" in result:
            print(f"⚠️  Error listing tools: {result['error']['message']}")
            return []
        return result.get("result", {}).get("tools", [])
    
    def call_tool(self, tool_name: str, arguments: Dict = None) -> Any:
        """Call a specific tool on the MCP server
        
        Automatically injects AEM credentials for all aem-* tools from environment variables:
        - AEM_SERVER: Your AEM instance URL
        - AEM_TOKEN: Your AEM authentication token
        """
        # Initialize arguments if None
        if arguments is None:
            arguments = {}
        
        # Auto-inject AEM credentials for all AEM tools
        if tool_name.startswith('aem-'):
            import os
            from dotenv import load_dotenv
            load_dotenv()  # Ensure .env is loaded
            
            aem_server = os.getenv('AEM_SERVER')
            aem_token = os.getenv('AEM_TOKEN')
            
            # Always add credentials for AEM tools
            if aem_server:
                arguments['server'] = aem_server
                print(f"🔧 Using AEM_SERVER: {aem_server}")
            else:
                print("⚠️  AEM_SERVER not set in .env file")
                
            if aem_token:
                arguments['token'] = aem_token
                print(f"🔑 Using AEM_TOKEN: ***{aem_token[-10:]}")
            else:
                print("⚠️  AEM_TOKEN not set in .env file")
        
        result = self._call_jsonrpc("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "error" in result:
            return {
                "success": False,
                "error": result["error"]["message"]
            }
        
        return {
            "success": True,
            "result": result.get("result", {})
        }
    
    def list_resources(self) -> List[Dict]:
        """List all available resources from the MCP server"""
        result = self._call_jsonrpc("resources/list")
        if "error" in result:
            print(f"⚠️  Error listing resources: {result['error']['message']}")
            return []
        return result.get("result", {}).get("resources", [])
    
    def read_resource(self, uri: str) -> Any:
        """Read a specific resource from the MCP server"""
        result = self._call_jsonrpc("resources/read", {
            "uri": uri
        })
        
        if "error" in result:
            return {
                "success": False,
                "error": result["error"]["message"]
            }
        
        return {
            "success": True,
            "contents": result.get("result", {}).get("contents", [])
        }
    
    def get_server_info(self) -> Dict:
        """Get server information"""
        try:
            response = self.session.get(self.server_url, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def is_healthy(self) -> bool:
        """Check if the MCP server is healthy"""
        info = self.get_server_info()
        return info.get("status") == "healthy"


class MCPIntegratedAgent:
    """Agent that can use both RAG and MCP tools"""
    
    def __init__(self, mcp_server_url: str, rag_agent):
        self.mcp_client = MCPClient(mcp_server_url)
        self.rag_agent = rag_agent
        self.available_tools = []
        self._load_mcp_tools()
    
    def _load_mcp_tools(self):
        """Load available tools from MCP server"""
        print("🔧 Loading MCP tools...")
        self.available_tools = self.mcp_client.list_tools()
        if self.available_tools:
            print(f"✅ Loaded {len(self.available_tools)} MCP tools:")
            for tool in self.available_tools:
                print(f"   - {tool.get('name')}: {tool.get('description', 'No description')}")
        else:
            print("⚠️  No MCP tools available")
    
    def query_with_mcp(self, question: str, use_mcp_tools: bool = True) -> Dict:
        """
        Query the agent with optional MCP tool usage
        First checks if MCP tools might be useful, then falls back to RAG
        """
        # Check if question might benefit from MCP tools
        tool_keywords = ["adobe", "runtime", "action", "function", "api", "service"]
        might_use_mcp = any(keyword in question.lower() for keyword in tool_keywords)
        
        if use_mcp_tools and might_use_mcp and self.available_tools:
            # Try to match question to available tools
            print(f"🔧 Checking MCP tools for: {question}")
            # For now, return RAG answer with note about MCP tools
            rag_result = self.rag_agent.query(question)
            rag_result["mcp_tools_available"] = [t["name"] for t in self.available_tools]
            return rag_result
        
        # Fall back to standard RAG
        return self.rag_agent.query(question)
    
    def execute_mcp_tool(self, tool_name: str, arguments: Dict = None) -> Dict:
        """Execute a specific MCP tool"""
        print(f"🔧 Executing MCP tool: {tool_name}")
        return self.mcp_client.call_tool(tool_name, arguments)
    
    def get_mcp_resources(self) -> List[Dict]:
        """Get available MCP resources"""
        return self.mcp_client.list_resources()


# Test the MCP integration
if __name__ == "__main__":
    print("🧪 Testing MCP Client Integration")
    print("=" * 60)
    
    # Initialize MCP client
    mcp_url = "https://332794-trainingprojecty-stage.adobeioruntime.net/api/v1/web/my-mcp-server/mcp-server"
    client = MCPClient(mcp_url)
    
    # Test server health
    print("\n1. Testing server health...")
    info = client.get_server_info()
    print(f"   Status: {info.get('status')}")
    print(f"   Server: {info.get('server')}")
    print(f"   Version: {info.get('version')}")
    print(f"   Transport: {info.get('transport')}")
    
    # Test listing tools
    print("\n2. Testing tools/list...")
    tools = client.list_tools()
    if tools:
        print(f"   ✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"      - {tool.get('name')}: {tool.get('description', 'No description')}")
    else:
        print("   ℹ️  No tools available or server requires SSE connection")
    
    # Test listing resources
    print("\n3. Testing resources/list...")
    resources = client.list_resources()
    if resources:
        print(f"   ✅ Found {len(resources)} resources:")
        for resource in resources:
            print(f"      - {resource.get('uri')}: {resource.get('name', 'No name')}")
    else:
        print("   ℹ️  No resources available or server requires SSE connection")
    
    print("\n" + "=" * 60)
    print("✅ MCP Client Test Complete")
