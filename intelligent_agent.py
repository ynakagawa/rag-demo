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

Given a user message, determine:
1. Does the user want to execute one of these tools? (yes/no)
2. Which tool should be executed?
3. What are the arguments?

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

User: "List my AEM sites"
{{
    "should_execute": true,
    "tool_name": "aem-list-sites",
    "arguments": {{"path": "/content"}},
    "reasoning": "User wants to list AEM sites"
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
                return {
                    "response": f"❌ Error executing {tool_name}: {result.get('error')}",
                    "mode": "mcp_error",
                    "error": result.get("error")
                }
        
        # If not a tool execution, check if it's an AEM knowledge question
        aem_keywords = ['aem', 'adobe', 'experience manager', 'dispatcher', 'component', 'what is', 'how does', 'explain']
        is_aem_question = any(keyword in user_message.lower() for keyword in aem_keywords)
        
        if is_aem_question and self.rag_agent.is_ready():
            rag_result = self.rag_agent.query(user_message)
            return {
                "response": rag_result["answer"],
                "mode": "rag",
                "sources": rag_result.get("sources", [])
            }
        
        # Fall back to conversational mode
        return {
            "response": "I can help you with AEM questions or execute AEM tools. Try asking about AEM or requesting an action like 'list my sites' or 'create a component'.",
            "mode": "conversational"
        }
    
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
