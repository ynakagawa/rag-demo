"""
Python serverless function for chat endpoint on Vercel
Uses LangChain with RAG for Adobe Experience Manager documentation
"""
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.messages import HumanMessage, AIMessage
import os

app = Flask(__name__)

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini", 
    temperature=0.7,
    openai_api_key=os.environ.get('OPENAI_API_KEY')
)

# Initialize RAG components
embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('OPENAI_API_KEY'))
vector_store = None
qa_chain = None

# Try to load vector store
try:
    vector_store = FAISS.load_local(
        "./vector_store",
        embeddings,
        allow_dangerous_deserialization=True
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    print("✅ RAG system loaded successfully")
except Exception as e:
    print(f"⚠️  RAG not available: {e}")

# In-memory conversation storage (in production, use a database)
conversations = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with RAG support for AEM documentation"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        use_rag = data.get('use_rag', True)  # Enable RAG by default
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Check if question is AEM-related and use RAG
        aem_keywords = ['aem', 'adobe', 'experience manager', 'dispatcher', 'component', 'sling', 'jcr', 'dam', 'assets']
        is_aem_question = any(keyword in user_message.lower() for keyword in aem_keywords)
        
        if use_rag and is_aem_question and qa_chain:
            # Use RAG for AEM questions
            result = qa_chain.invoke({"query": user_message})
            response_text = result["result"]
            
            # Add sources information
            if result.get("source_documents"):
                sources = [doc.metadata.get("source", "AEM Docs") for doc in result["source_documents"][:2]]
                response_text += f"\n\n📚 Sources: {', '.join(set(sources))}"
            
            return jsonify({
                "response": response_text,
                "session_id": session_id,
                "mode": "rag"
            })
        else:
            # Use conversational mode for general questions
            # Get or create conversation history
            if session_id not in conversations:
                conversations[session_id] = []
            
            # Add user message to history
            conversations[session_id].append(HumanMessage(content=user_message))
            
            # Get response from LLM (LangSmith will trace this)
            response = llm.invoke(conversations[session_id])
            
            # Add AI response to history
            conversations[session_id].append(response)
            
            # Keep only last 10 messages
            if len(conversations[session_id]) > 10:
                conversations[session_id] = conversations[session_id][-10:]
            
            return jsonify({
                "response": response.content,
                "session_id": session_id,
                "mode": "conversational"
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

