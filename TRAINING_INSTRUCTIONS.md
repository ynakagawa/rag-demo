# 🎓 Training Instructions: Building an AEM RAG Chatbot with MCP Integration

## Overview

This document provides step-by-step instructions for building a production-ready RAG (Retrieval-Augmented Generation) chatbot for Adobe Experience Manager (AEM) with Model Context Protocol (MCP) integration, deployed on Vercel.

## Architecture Overview

The application consists of:
- **Python Backend**: Flask API with LangChain, RAG, and MCP integration
- **Node.js Frontend**: Express server serving a beautiful chat interface
- **RAG System**: Vector store (FAISS) with AEM documentation embeddings
- **MCP Integration**: Adobe I/O Runtime MCP server with 12 AEM tools
- **Intelligent Agent**: Automatic routing between RAG, MCP tools, and conversational AI
- **Deployment**: Vercel serverless functions (Python + Node.js)

---

## Step 1: Project Initialization

### 1.1 Create Project Structure

```bash
mkdir RAG-demo
cd RAG-demo
```

### 1.2 Initialize Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Initialize Node.js Project

```bash
npm init -y
```

### 1.4 Create Directory Structure

```bash
mkdir -p api views vector_store
```

---

## Step 2: Install Dependencies

### 2.1 Python Dependencies (`requirements.txt`)

Create `requirements.txt` with:

```txt
# Core dependencies
Flask==3.1.0
flask-cors==6.0.1

# LangChain and AI
langchain==0.3.13
langchain-openai==0.2.12
langchain-core==0.3.28
langchain-community==0.3.13

# OpenAI
openai==1.59.5

# Vector stores and embeddings
faiss-cpu==1.9.0
tiktoken==0.8.0

# Document loaders and processing
beautifulsoup4==4.12.3
lxml==5.3.0

# LangSmith tracing (optional)
langsmith==0.2.11

# Other dependencies
python-dotenv==1.0.1
requests==2.31.0
```

Install:
```bash
pip install -r requirements.txt
```

### 2.2 Node.js Dependencies (`package.json`)

Create `package.json`:

```json
{
  "name": "aem-chatbot-agent",
  "version": "1.0.0",
  "description": "AEM chatbot and agent - Node.js interface for LangChain agent",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "ejs": "^3.1.9",
    "express": "^4.18.2",
    "openai": "^4.104.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

Install:
```bash
npm install
```

---

## Step 3: Environment Configuration

### 3.1 Create `.env` File

Create `.env` in project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# LangSmith Configuration (Optional)
LANGSMITH_API_KEY=your-langsmith-api-key-here
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=your-project-name

# AEM Configuration (for MCP tools)
AEM_SERVER=https://your-aem-instance.com
AEM_TOKEN=your-aem-token-here
```

### 3.2 Create `.gitignore`

```gitignore
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
.env

# Node.js
node_modules/
npm-debug.log
yarn-error.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

## Step 4: Build Basic Chatbot Backend

### 4.1 Create Flask API (`agent_api.py`)

Create `agent_api.py`:

```python
"""
Flask API wrapper for the LangChain agent with RAG and MCP support
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Store conversation history
conversation_history = {}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model": "gpt-4o-mini"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Get or create conversation history
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Add user message to history
        conversation_history[session_id].append(HumanMessage(content=user_message))
        
        # Get response from LLM
        response = llm.invoke(conversation_history[session_id])
        
        # Add AI response to history
        conversation_history[session_id].append(response)
        
        # Keep only last 10 messages
        if len(conversation_history[session_id]) > 10:
            conversation_history[session_id] = conversation_history[session_id][-10:]
        
        return jsonify({
            "response": response.content,
            "session_id": session_id,
            "mode": "conversational"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    """Reset conversation history"""
    data = request.json
    session_id = data.get('session_id', 'default')
    
    if session_id in conversation_history:
        conversation_history[session_id] = []
    
    return jsonify({"message": "Conversation reset", "session_id": session_id})

if __name__ == '__main__':
    print("🚀 Starting Flask API server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
```

---

## Step 5: Build Frontend Interface

### 5.1 Create Express Server (`server.js`)

Create `server.js`:

```javascript
/**
 * Node.js Express Server for Chatbot Interface
 */
const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const PYTHON_API_URL = process.env.API_URL || 'http://localhost:5001';

app.use(express.json());
app.use(express.static('public'));

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.get('/', (req, res) => {
    res.render('chat', { 
        title: 'AEM chatbot and agent'
    });
});

app.post('/api/chat', async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_API_URL}/chat`, req.body, {
            timeout: 30000,
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error calling API:', error.message);
        res.status(500).json({ 
            error: 'Failed to get response from agent',
            details: error.message 
        });
    }
});

app.post('/api/reset', async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_API_URL}/reset`, req.body, {
            timeout: 5000,
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error resetting conversation:', error.message);
        res.status(500).json({ 
            error: 'Failed to reset conversation',
            details: error.message 
        });
    }
});

app.get('/health', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API_URL}/health`, {
            timeout: 5000,
        });
        res.json({ 
            status: 'healthy',
            backend: response.data 
        });
    } catch (error) {
        res.status(503).json({ 
            status: 'unhealthy',
            error: 'Backend not available',
            details: error.message
        });
    }
});

app.listen(PORT, () => {
    console.log(`🚀 Node.js server running on http://localhost:${PORT}`);
    console.log(`📡 Connecting to Python backend at ${PYTHON_API_URL}`);
});
```

### 5.2 Create Chat Interface (`views/chat.ejs`)

Create `views/chat.ejs` with a beautiful, modern UI (see existing file for full implementation). Key features:
- Gradient design
- Real-time messaging
- Typing indicators
- Reset functionality
- Responsive layout

---

## Step 6: Implement RAG System

### 6.1 Create Document Indexer (`indexer.py`)

Create `indexer.py`:

```python
"""
Document Indexer for Adobe Experience Manager Documentation
Creates vector embeddings and stores them for RAG retrieval
"""
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

load_dotenv()

class AEMDocumentationIndexer:
    """Index Adobe Experience Manager documentation for RAG"""
    
    def __init__(self, vector_store_path="./vector_store"):
        self.vector_store_path = vector_store_path
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
    def load_aem_documentation(self):
        """Load Adobe Experience Manager documentation"""
        print("📚 Loading AEM documentation...")
        
        aem_urls = [
            "https://experienceleague.adobe.com/en/docs/experience-manager",
            "https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service",
            "https://experienceleague.adobe.com/en/docs/experience-manager-65",
        ]
        
        documents = []
        
        for url in aem_urls:
            try:
                print(f"  Loading: {url}")
                loader = WebBaseLoader(url)
                docs = loader.load()
                documents.extend(docs)
                print(f"  ✅ Loaded {len(docs)} documents from {url}")
            except Exception as e:
                print(f"  ⚠️  Error loading {url}: {e}")
        
        # Add sample AEM documentation content
        sample_docs = [
            Document(
                page_content="Adobe Experience Manager (AEM) is a comprehensive content management solution...",
                metadata={"source": "https://experienceleague.adobe.com/en/docs/experience-manager", "type": "overview"}
            ),
            # Add more sample documents...
        ]
        
        documents.extend(sample_docs)
        print(f"\n✅ Total documents loaded: {len(documents)}")
        return documents
    
    def create_vector_store(self, documents):
        """Create vector embeddings and store in FAISS"""
        print("\n🔨 Creating vector embeddings...")
        
        split_docs = self.text_splitter.split_documents(documents)
        print(f"  Split into {len(split_docs)} chunks")
        
        vector_store = FAISS.from_documents(split_docs, self.embeddings)
        
        os.makedirs(self.vector_store_path, exist_ok=True)
        vector_store.save_local(self.vector_store_path)
        print(f"  ✅ Vector store saved to {self.vector_store_path}")
        
        return vector_store
    
    def index_documentation(self):
        """Main indexing pipeline"""
        print("=" * 60)
        print("🚀 AEM Documentation Indexing Pipeline")
        print("=" * 60)
        
        documents = self.load_aem_documentation()
        vector_store = self.create_vector_store(documents)
        
        print("\n" + "=" * 60)
        print("✅ Indexing Complete!")
        print("=" * 60)
        print(f"📊 Total chunks indexed: {vector_store.index.ntotal}")
        print(f"💾 Vector store location: {self.vector_store_path}")
        
        return vector_store

def main():
    indexer = AEMDocumentationIndexer()
    indexer.index_documentation()

if __name__ == "__main__":
    main()
```

Run the indexer:
```bash
python indexer.py
```

### 6.2 Create RAG Agent (`rag_agent.py`)

Create `rag_agent.py`:

```python
"""
RAG Agent for Adobe Experience Manager Documentation
Uses retrieval-augmented generation to answer questions
"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os

load_dotenv()

class AEMRAGAgent:
    """RAG Agent for AEM documentation queries"""
    
    def __init__(self, vector_store_path="./vector_store"):
        self.vector_store_path = vector_store_path
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.vector_store = None
        self.qa_chain = None
        self._load_vector_store()
    
    def _load_vector_store(self):
        """Load the vector store from disk"""
        try:
            print(f"📚 Loading vector store from {self.vector_store_path}...")
            self.vector_store = FAISS.load_local(
                self.vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print("✅ Vector store loaded successfully")
            self._create_qa_chain()
        except Exception as e:
            print(f"⚠️  Warning: Could not load vector store: {e}")
    
    def _create_qa_chain(self):
        """Create the QA chain with custom prompt"""
        template = """You are an expert Adobe Experience Manager (AEM) consultant. 
Use the following context from AEM documentation to answer the question. 
If you don't know the answer based on the context, say so clearly.

Context from AEM Documentation:
{context}

Question: {question}

Provide a helpful, accurate answer based on the AEM documentation. Include relevant details and examples when appropriate.

Answer:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        self.qa_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        print("✅ RAG QA chain created")
    
    def query(self, question):
        """Query the RAG system with a question"""
        if not self.qa_chain:
            return {
                "answer": "❌ Vector store not loaded. Please run 'python indexer.py' first.",
                "sources": []
            }
        
        try:
            answer = self.qa_chain.invoke(question)
            
            source_docs = self.retriever.invoke(question)
            sources = [
                {
                    "content": doc.page_content[:200] + "...",
                    "source": doc.metadata.get("source", "Unknown")
                }
                for doc in source_docs
            ]
            
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            return {
                "answer": f"❌ Error querying RAG system: {str(e)}",
                "sources": []
            }
    
    def is_ready(self):
        """Check if RAG system is ready"""
        return self.qa_chain is not None
```

### 6.3 Integrate RAG into Backend

Update `agent_api.py` to include RAG:

```python
from rag_agent import AEMRAGAgent

# Initialize RAG agent
rag_agent = AEMRAGAgent()

# In chat endpoint, add RAG routing:
aem_keywords = ['aem', 'adobe', 'experience manager', 'dispatcher', 'component', 'sling', 'jcr', 'dam', 'assets', 'sites', 'forms']
is_aem_question = any(keyword in user_message.lower() for keyword in aem_keywords)

if is_aem_question and rag_agent.is_ready():
    result = rag_agent.query(user_message)
    response_text = result["answer"]
    
    if result.get("sources"):
        sources_text = "\n\n📚 **Sources:**\n"
        for i, source in enumerate(result["sources"][:2], 1):
            sources_text += f"{i}. {source['source']}\n"
        response_text += sources_text
    
    return jsonify({
        "response": response_text,
        "session_id": session_id,
        "mode": "rag",
        "sources": result.get("sources", [])
    })
```

---

## Step 7: Implement MCP Integration

### 7.1 Create MCP Client (`mcp_client.py`)

Create `mcp_client.py`:

```python
"""
MCP Client for Adobe I/O Runtime MCP Server
"""
import json
import requests
from typing import Dict, List, Any
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
            return []
        return result.get("result", {}).get("tools", [])
    
    def call_tool(self, tool_name: str, arguments: Dict = None) -> Any:
        """Call a specific tool on the MCP server"""
        if arguments is None:
            arguments = {}
        
        # Auto-inject AEM credentials for AEM tools
        if tool_name.startswith('aem-'):
            from dotenv import load_dotenv
            load_dotenv()
            
            aem_server = os.getenv('AEM_SERVER', '').strip()
            aem_token = os.getenv('AEM_TOKEN', '').strip()
            
            if aem_server:
                arguments['server'] = aem_server
            if aem_token:
                arguments['token'] = aem_token
        
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
    
    def is_healthy(self) -> bool:
        """Check if the MCP server is healthy"""
        try:
            response = self.session.get(self.server_url, timeout=10)
            info = response.json()
            return info.get("status") == "healthy"
        except:
            return False
```

### 7.2 Integrate MCP into Backend

Update `agent_api.py`:

```python
from mcp_client import MCPClient

# Initialize MCP client
mcp_url = "https://your-mcp-server-url.com/mcp-server"
mcp_client = MCPClient(mcp_url)

# Add MCP endpoints
@app.route('/mcp/tools', methods=['GET'])
def get_mcp_tools():
    """Get available MCP tools"""
    try:
        tools = mcp_client.list_tools()
        return jsonify({
            "tools": tools,
            "count": len(tools)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/execute', methods=['POST'])
def execute_mcp_tool():
    """Execute an MCP tool"""
    try:
        data = request.json
        tool_name = data.get('tool_name')
        arguments = data.get('arguments', {})
        
        if not tool_name:
            return jsonify({"error": "tool_name is required"}), 400
        
        result = mcp_client.call_tool(tool_name, arguments)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

---

## Step 8: Create Intelligent Agent

### 8.1 Create Intelligent Agent (`intelligent_agent.py`)

Create `intelligent_agent.py`:

```python
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
        """Use LLM to determine if the user wants to execute an MCP tool"""
        tools_description = "\n".join([
            f"- {tool['name']}: {tool.get('description', '')}"
            for tool in self.mcp_tools
        ])
        
        system_prompt = f"""You are an AI assistant that determines if a user wants to execute an MCP tool.

Available MCP tools:
{tools_description}

Given a user message, determine:
1. Does the user want to execute one of these tools? (yes/no)
2. Which tool should be executed?
3. What are the arguments?

Respond ONLY with a JSON object:
{{
    "should_execute": true/false,
    "tool_name": "tool-name" or null,
    "arguments": {{}},
    "reasoning": "why this tool was chosen"
}}"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User message: {user_message}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"should_execute": False, "tool_name": None, "arguments": {}}
        except Exception as e:
            return {"should_execute": False, "tool_name": None, "arguments": {}}
    
    def process_message(self, user_message: str) -> dict:
        """Process user message and either execute MCP tool or use RAG/chat"""
        intent = self.parse_intent(user_message)
        
        if intent.get("should_execute") and intent.get("tool_name"):
            tool_name = intent["tool_name"]
            arguments = intent.get("arguments", {})
            
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
                    "mode": "mcp_error"
                }
        
        # Check if it's an AEM knowledge question
        knowledge_keywords = ['what is', 'how does', 'explain', 'what are', 'describe']
        is_knowledge_question = any(keyword in user_message.lower() for keyword in knowledge_keywords)
        
        aem_keywords = ['aem', 'adobe', 'experience manager']
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
            "response": "I can help you with AEM actions, knowledge questions, and more. What would you like to do?",
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
        else:
            formatted += "Tool executed successfully (no output)"
        
        return formatted
```

### 8.2 Integrate Intelligent Agent

Update `agent_api.py`:

```python
from intelligent_agent import IntelligentMCPAgent

# Initialize intelligent agent
intelligent_agent = IntelligentMCPAgent(mcp_client, rag_agent)

# Update chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    # ... existing code ...
    
    # Use intelligent agent if available
    if intelligent_agent:
        result = intelligent_agent.process_message(user_message)
        return jsonify({
            "response": result.get("response"),
            "session_id": session_id,
            "mode": result.get("mode"),
            "tool_executed": result.get("tool_executed"),
            "sources": result.get("sources", [])
        })
```

---

## Step 9: Create Startup Script

### 9.1 Create `start.sh`

Create `start.sh`:

```bash
#!/bin/bash

echo "🚀 Starting RAG-demo Chatbot..."
echo ""

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Start Python backend in background
echo "📡 Starting Python backend (Flask API)..."
source venv/bin/activate && python agent_api.py &
PYTHON_PID=$!

# Wait for Python backend to start
sleep 3

# Start Node.js frontend
echo "🌐 Starting Node.js frontend..."
node server.js &
NODE_PID=$!

echo ""
echo "✅ Both servers are running!"
echo ""
echo "🌐 Open your browser and go to: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $PYTHON_PID $NODE_PID; exit" INT
wait
```

Make executable:
```bash
chmod +x start.sh
```

---

## Step 10: Deploy to Vercel

### 10.1 Create Vercel Configuration (`vercel.json`)

Create `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "server.js",
      "use": "@vercel/node",
      "config": {
        "includeFiles": ["views/**"]
      }
    },
    {
      "src": "api/**/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/chat",
      "dest": "/api/chat.py"
    },
    {
      "src": "/api/reset",
      "dest": "/api/reset.py"
    },
    {
      "src": "/api/health",
      "dest": "/api/health.py"
    },
    {
      "src": "/(.*)",
      "dest": "/server.js"
    }
  ]
}
```

### 10.2 Create Serverless Functions

Create `api/chat.py`:

```python
"""
Python serverless function for chat endpoint on Vercel
"""
from flask import Flask, request, jsonify
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client import MCPClient
from rag_agent import AEMRAGAgent
from intelligent_agent import IntelligentMCPAgent

app = Flask(__name__)

# Initialize components
MCP_SERVER_URL = "https://your-mcp-server-url.com/mcp-server"
mcp_client = MCPClient(MCP_SERVER_URL)
rag_agent = AEMRAGAgent()
intelligent_agent = IntelligentMCPAgent(mcp_client, rag_agent)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with Intelligent MCP Agent + RAG support"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        result = intelligent_agent.process_message(user_message)
        
        return jsonify({
            "response": result.get("response"),
            "session_id": session_id,
            "mode": result.get("mode"),
            "tool_executed": result.get("tool_executed"),
            "sources": result.get("sources", [])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

Create similar files for `api/reset.py` and `api/health.py`.

### 10.3 Deploy to Vercel

1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your GitHub repository
4. Add environment variables in Vercel dashboard:
   - `OPENAI_API_KEY`
   - `LANGSMITH_API_KEY` (optional)
   - `LANGSMITH_TRACING` (optional)
   - `LANGSMITH_PROJECT` (optional)
   - `AEM_SERVER` (for MCP tools)
   - `AEM_TOKEN` (for MCP tools)
5. Deploy

---

## Step 11: Testing

### 11.1 Test Locally

```bash
# Start both servers
./start.sh

# Or manually:
# Terminal 1
source venv/bin/activate
python agent_api.py

# Terminal 2
node server.js
```

### 11.2 Test RAG

```bash
python rag_agent.py
```

### 11.3 Test MCP Client

```bash
python mcp_client.py
```

### 11.4 Test Intelligent Agent

```bash
python intelligent_agent.py
```

---

## Summary

You've successfully built:

1. ✅ **Basic Chatbot**: Flask API with LangChain and OpenAI
2. ✅ **Frontend Interface**: Beautiful Express.js chat UI
3. ✅ **RAG System**: Vector store with AEM documentation
4. ✅ **MCP Integration**: Adobe I/O Runtime MCP server connection
5. ✅ **Intelligent Agent**: Automatic routing between RAG, MCP tools, and chat
6. ✅ **Vercel Deployment**: Serverless Python + Node.js deployment

The application intelligently routes user queries:
- **AEM Knowledge Questions** → RAG system (documentation)
- **Action Requests** → MCP tools (AEM operations)
- **General Chat** → Conversational AI

---

## Next Steps

- Add database for conversation persistence
- Implement streaming responses
- Add authentication
- Enhance error handling
- Add more documentation sources
- Implement tool chaining
- Add monitoring and analytics
