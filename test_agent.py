"""
Simple test agent to verify LangChain and LangSmith setup
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Verify environment variables are set
print("🔍 Checking environment variables...")
print(f"LANGSMITH_TRACING: {os.getenv('LANGSMITH_TRACING')}")
print(f"LANGSMITH_PROJECT: {os.getenv('LANGSMITH_PROJECT')}")
print(f"OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
print(f"LANGSMITH_API_KEY: {'✅ Set' if os.getenv('LANGSMITH_API_KEY') else '❌ Not set'}")
print()

# Define a simple tool
@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

# Create the tools list
tools = [multiply, add]

# Initialize the LLM with tools
print("🤖 Initializing ChatOpenAI with tools...")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# Test the agent
print("\n" + "="*50)
print("🚀 Running test query...")
print("="*50 + "\n")

# First call - get tool calls
messages = [HumanMessage(content="What is 25 multiplied by 4, and then add 10 to the result?")]
response = llm_with_tools.invoke(messages)

print(f"🔧 Model response with tool calls:")
print(f"   Content: {response.content}")
if hasattr(response, 'tool_calls') and response.tool_calls:
    print(f"   Tool calls: {response.tool_calls}")
    
    # Execute the tools manually for demonstration
    results = []
    for tool_call in response.tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        
        if tool_name == 'multiply':
            result = multiply.invoke(tool_args)
            results.append(f"multiply({tool_args['a']}, {tool_args['b']}) = {result}")
        elif tool_name == 'add':
            result = add.invoke(tool_args)
            results.append(f"add({tool_args['a']}, {tool_args['b']}) = {result}")
    
    print(f"\n📊 Tool Results:")
    for r in results:
        print(f"   {r}")

print("\n" + "="*50)
print("✅ Test Complete!")
print("="*50)
print("\n💡 Check your LangSmith project at: https://smith.langchain.com")
print(f"   Project: {os.getenv('LANGSMITH_PROJECT')}")
print("\n✨ LangSmith will show the full trace of this interaction!")

