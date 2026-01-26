# 🎯 RAG Implementation Guide - Adobe Experience Manager Documentation

## Overview

Your chatbot now uses **RAG (Retrieval-Augmented Generation)** to answer questions about Adobe Experience Manager using indexed documentation from [https://experienceleague.adobe.com/en/docs/experience-manager](https://experienceleague.adobe.com/en/docs/experience-manager).

## 🏗️ Architecture

```
User Question
     ↓
Question Analysis (Is it AEM-related?)
     ↓
   ┌─────────────────┐
   │   RAG Mode      │ ← AEM Questions
   │  ┌───────────┐  │
   │  │ Retriever │  │ → Searches vector store
   │  └───────────┘  │
   │       ↓         │
   │  Top 4 docs     │
   │       ↓         │
   │    ChatGPT      │ → Generates answer with context
   └─────────────────┘
           OR
   ┌─────────────────┐
   │ Conversational  │ ← General Questions
   │     Mode        │
   │    ChatGPT      │ → Direct conversation
   └─────────────────┘
```

## 📁 New Files

### 1. `indexer.py`
- **Purpose**: Indexes AEM documentation and creates vector embeddings
- **What it does**:
  - Loads AEM documentation from web sources
  - Splits documents into chunks
  - Creates embeddings using OpenAI's embedding model
  - Stores in FAISS vector database

### 2. `rag_agent.py`
- **Purpose**: RAG agent for querying indexed documentation
- **What it does**:
  - Loads the vector store
  - Performs similarity search
  - Generates context-aware answers
  - Returns sources for transparency

### 3. Updated `agent_api.py` and `api/chat.py`
- **Purpose**: Integrated RAG into chat endpoints
- **What changed**:
  - Detects AEM-related questions
  - Routes to RAG for AEM questions
  - Falls back to conversation mode for general questions

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd /Users/ynaka/Documents/RAG-demo
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Index AEM Documentation

```bash
python indexer.py
```

This will:
- Load AEM documentation
- Create embeddings
- Save vector store to `./vector_store/`
- Takes ~2-5 minutes

**Output:**
```
====================================================
🚀 AEM Documentation Indexing Pipeline
====================================================
📚 Loading AEM documentation...
  Loading: https://experienceleague.adobe.com/en/docs/experience-manager
  ✅ Loaded documents
...
🔨 Creating vector embeddings...
  Split into X chunks
  Creating FAISS vector store...
  ✅ Vector store saved to ./vector_store
====================================================
✅ Indexing Complete!
====================================================
```

### Step 3: Test the RAG Agent

```bash
python rag_agent.py
```

This will run test queries to verify RAG is working.

### Step 4: Start the Chatbot

```bash
# Option 1: Use startup script
./start.sh

# Option 2: Manual start
# Terminal 1
python agent_api.py

# Terminal 2
node server.js
```

### Step 5: Ask AEM Questions!

Go to [http://localhost:3000](http://localhost:3000) and try:

**AEM Questions (uses RAG):**
- "What is Adobe Experience Manager?"
- "How do AEM components work?"
- "What is AEM Dispatcher?"
- "Explain AEM as a Cloud Service"
- "What is DAM in AEM?"

**General Questions (uses conversation):**
- "Hello, how are you?"
- "Tell me a joke"
- "What's the weather like?"

## 🎯 How It Works

### 1. Document Indexing

```python
# indexer.py process:
Documents → Text Splitting → Embeddings → Vector Store
                ↓              ↓             ↓
            Chunks (1000)  OpenAI API    FAISS DB
```

### 2. Question Answering

```python
# When user asks AEM question:
Question → Embedding → Similarity Search → Top K Docs → LLM → Answer
             ↓            ↓                   ↓         ↓
         Vector     Vector Store         Context    ChatGPT
```

### 3. Smart Routing

```python
if "aem" in question.lower():
    # Use RAG mode
    answer = rag_agent.query(question)
else:
    # Use conversational mode
    answer = llm.invoke(conversation_history)
```

## 📊 Vector Store Details

### Technology: FAISS
- **FAISS** = Facebook AI Similarity Search
- Ultra-fast similarity search
- Runs locally (no external DB needed)
- Perfect for prototypes and production

### Storage Location
```
./vector_store/
├── index.faiss      # Vector index
└── index.pkl        # Metadata
```

### Size
- Depends on documentation size
- Current setup: ~10-20 MB
- Scales to millions of documents

## 🔧 Configuration

### Chunk Size (in `indexer.py`)
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Characters per chunk
    chunk_overlap=200,    # Overlap between chunks
)
```

**Adjust for:**
- Smaller chunks (500): More precise but more API calls
- Larger chunks (2000): More context but less precise

### Number of Retrieved Documents (in `rag_agent.py`)
```python
retriever = self.vector_store.as_retriever(
    search_kwargs={"k": 4}  # Return top 4 chunks
)
```

**Adjust for:**
- More documents (k=6): More context but slower
- Fewer documents (k=2): Faster but might miss context

### AEM Keywords Detection
```python
aem_keywords = [
    'aem', 'adobe', 'experience manager', 
    'dispatcher', 'component', 'sling', 
    'jcr', 'dam', 'assets', 'sites', 'forms'
]
```

Add more keywords to improve detection.

## 🌐 Deploying to Vercel

### Challenge
Vector store needs to be included in deployment.

### Solution Options

#### Option 1: Include in Git (Simple)
```bash
# Add vector store to git
git add vector_store/
git commit -m "Add vector store"
git push
```

**Pros:** Simple, works immediately  
**Cons:** Increases repo size

#### Option 2: Generate on Build (Better)
Add to `vercel.json`:
```json
{
  "buildCommand": "python indexer.py && npm install"
}
```

**Pros:** Always fresh, smaller repo  
**Cons:** Slower builds

#### Option 3: External Storage (Production)
Use Pinecone, Weaviate, or Qdrant:
- Cloud-hosted vector databases
- Better for production
- Scalable

## 📈 Expanding the Knowledge Base

### Add More AEM Documentation

Edit `indexer.py`:

```python
aem_urls = [
    "https://experienceleague.adobe.com/en/docs/experience-manager",
    "https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service",
    "https://experienceleague.adobe.com/en/docs/experience-manager-65",
    # Add more URLs:
    "https://experienceleague.adobe.com/en/docs/experience-manager-sites",
    "https://experienceleague.adobe.com/en/docs/experience-manager-assets",
    # ... etc
]
```

### Add PDF Documentation

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("path/to/aem-guide.pdf")
documents.extend(loader.load())
```

### Add Custom Content

```python
custom_doc = Document(
    page_content="Your custom AEM knowledge...",
    metadata={"source": "internal-docs", "type": "custom"}
)
documents.append(custom_doc)
```

## 🐛 Troubleshooting

### Error: "Vector store not loaded"
**Solution:** Run `python indexer.py` to create the vector store

### Error: "No module named 'faiss'"
**Solution:** 
```bash
pip install faiss-cpu
```

### RAG not working for AEM questions
**Check:**
1. Vector store exists: `ls -la vector_store/`
2. Keywords detected: Add more AEM terms
3. Logs: Check terminal for "RAG agent ready"

### Answers not relevant
**Improve:**
1. Index more documentation
2. Increase `k` value (more retrieved docs)
3. Adjust chunk size
4. Refine prompts

## 📚 Resources

- [Adobe Experience Manager Documentation](https://experienceleague.adobe.com/en/docs/experience-manager)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)

## 🎯 Next Steps

1. ✅ Index AEM documentation
2. ✅ Test RAG locally
3. 🔄 Add more documentation sources
4. 🔄 Deploy to Vercel with vector store
5. 🔄 Switch to cloud vector DB (Pinecone/Weaviate)
6. 🔄 Add source citations in UI
7. 🔄 Implement feedback loop
8. 🔄 Add document upload feature

## 💡 Pro Tips

1. **Re-index regularly**: Run `python indexer.py` when AEM docs update
2. **Monitor costs**: Embeddings API calls add up
3. **Cache embeddings**: Don't re-embed same content
4. **Test queries**: Keep a test set of questions
5. **Track sources**: Always show where answers come from

Your RAG system is now ready to answer Adobe Experience Manager questions with accuracy and context! 🎉


