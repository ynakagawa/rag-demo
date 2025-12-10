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
            
            # Create retrieval QA chain
            self._create_qa_chain()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load vector store: {e}")
            print("💡 Run 'python indexer.py' first to create the vector store")
    
    def _create_qa_chain(self):
        """Create the QA chain with custom prompt"""
        
        # Custom prompt template
        template = """You are an expert Adobe Experience Manager (AEM) consultant. 
Use the following context from AEM documentation to answer the question. 
If you don't know the answer based on the context, say so clearly.

Context from AEM Documentation:
{context}

Question: {question}

Provide a helpful, accurate answer based on the AEM documentation. Include relevant details and examples when appropriate.

Answer:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Create retriever
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}  # Return top 4 most relevant chunks
        )
        
        # Create RAG chain using LCEL
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
                "answer": "❌ Vector store not loaded. Please run 'python indexer.py' first to index the AEM documentation.",
                "sources": []
            }
        
        try:
            # Get answer from RAG
            answer = self.qa_chain.invoke(question)
            
            # Get source documents
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

# Test the RAG agent
if __name__ == "__main__":
    print("🧪 Testing RAG Agent...")
    
    agent = AEMRAGAgent()
    
    if agent.is_ready():
        # Test queries
        test_questions = [
            "What is Adobe Experience Manager?",
            "What are AEM Components?",
            "How does AEM Dispatcher work?",
            "What is AEM as a Cloud Service?"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            result = agent.query(question)
            print(f"💡 Answer: {result['answer']}")
            if result['sources']:
                print(f"📚 Sources: {len(result['sources'])} documents")
    else:
        print("❌ RAG agent not ready. Run 'python indexer.py' first.")

