"""
Test script to verify LangSmith tracing is working
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

print("🔍 Checking LangSmith Configuration...")
print(f"LANGSMITH_TRACING: {os.getenv('LANGSMITH_TRACING')}")
print(f"LANGSMITH_PROJECT: {os.getenv('LANGSMITH_PROJECT')}")
print(f"LANGSMITH_ENDPOINT: {os.getenv('LANGSMITH_ENDPOINT')}")
print(f"LANGSMITH_API_KEY: {'✅ Set' if os.getenv('LANGSMITH_API_KEY') else '❌ Not Set'}")
print()

# Verify langsmith is installed
try:
    import langsmith
    print(f"✅ LangSmith version: {langsmith.__version__}")
except ImportError:
    print("❌ LangSmith not installed")
    exit(1)

print("\n🧪 Testing LangSmith Tracing...")
print("=" * 60)

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)

# Test message
print("\n📤 Sending test message to OpenAI with LangSmith tracing...")
messages = [HumanMessage(content="Say 'Hello, LangSmith is working!' in one sentence.")]

try:
    response = llm.invoke(messages)
    print(f"✅ Response: {response.content}")
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)
    print("\n💡 If tracing is enabled, you should see this interaction at:")
    print(f"   https://smith.langchain.com/o/YOUR-ORG/projects/p/{os.getenv('LANGSMITH_PROJECT')}")
    print("\n📝 Note: It may take 10-30 seconds for traces to appear in LangSmith")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Check your LANGSMITH_API_KEY is valid")
    print("2. Verify you have access to the project in LangSmith")
    print("3. Make sure langsmith package is installed: pip install langsmith")
