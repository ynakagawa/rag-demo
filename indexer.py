"""
Document Indexer for Adobe Experience Manager Documentation
Creates vector embeddings and stores them for RAG retrieval
"""
from langchain_community.document_loaders import WebBaseLoader, SitemapLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv
import os
import pickle
from urllib.parse import urljoin

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
        
        # Main AEM documentation URLs to index
        aem_urls = [
            "https://experienceleague.adobe.com/en/docs/experience-manager",
            "https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service",
            "https://experienceleague.adobe.com/en/docs/experience-manager-65",
        ]
        
        documents = []
        
        # Load web pages
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
        # In production, you'd crawl more pages or use an API
        sample_docs = [
            Document(
                page_content="""
                Adobe Experience Manager (AEM) is a comprehensive content management solution 
                for building websites, mobile apps, and forms. AEM makes it easy to manage 
                your marketing content and assets.
                
                Key Features:
                - Content Management: Create, manage, and deliver content across channels
                - Digital Asset Management: Organize and distribute assets efficiently
                - Forms: Create responsive and accessible forms
                - Sites: Build responsive websites with reusable components
                - Cloud Service: Modern cloud-native architecture
                """,
                metadata={"source": "https://experienceleague.adobe.com/en/docs/experience-manager", "type": "overview"}
            ),
            Document(
                page_content="""
                AEM as a Cloud Service is Adobe's cloud-native offering that provides:
                - Automatic scaling and updates
                - Built-in CDN and security
                - Continuous integration and deployment
                - Modern architecture with microservices
                - GraphQL APIs for headless content delivery
                """,
                metadata={"source": "https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service", "type": "cloud-service"}
            ),
            Document(
                page_content="""
                AEM Sites allows you to create responsive websites with:
                - Component-based architecture
                - Template editor for page layouts
                - Style system for design variations
                - Multi-site management
                - Personalization and targeting
                - Integration with Adobe Analytics and Target
                """,
                metadata={"source": "https://experienceleague.adobe.com/en/docs/experience-manager-sites", "type": "sites"}
            ),
            Document(
                page_content="""
                AEM Assets (DAM) provides digital asset management capabilities:
                - Centralized repository for all digital assets
                - Metadata management and tagging
                - Smart tags using AI
                - Version control and workflows
                - Integration with Creative Cloud
                - Asset sharing via Brand Portal
                """,
                metadata={"source": "https://experienceleague.adobe.com/en/docs/experience-manager-assets", "type": "assets"}
            ),
            Document(
                page_content="""
                AEM Dispatcher is a caching and load balancing tool that:
                - Improves website performance through caching
                - Provides security by filtering requests
                - Load balances across multiple publish instances
                - Invalidates cache automatically on content updates
                - Configuration via dispatcher.any file
                """,
                metadata={"source": "https://experienceleague.adobe.com/en/docs/experience-manager-dispatcher", "type": "dispatcher"}
            ),
            Document(
                page_content="""
                AEM Components are reusable building blocks:
                - Core Components: Production-ready, standardized components
                - Custom Components: Build your own using HTL (HTML Template Language)
                - Component Dialog: Configure component properties
                - Sling Models: Java backend logic for components
                - Client Libraries: Manage CSS and JavaScript dependencies
                """,
                metadata={"source": "https://experienceleague.adobe.com/en/docs/experience-manager-components", "type": "components"}
            )
        ]
        
        documents.extend(sample_docs)
        print(f"\n✅ Total documents loaded: {len(documents)}")
        return documents
    
    def create_vector_store(self, documents):
        """Create vector embeddings and store in FAISS"""
        print("\n🔨 Creating vector embeddings...")
        
        # Split documents into chunks
        split_docs = self.text_splitter.split_documents(documents)
        print(f"  Split into {len(split_docs)} chunks")
        
        # Create vector store
        print("  Creating FAISS vector store...")
        vector_store = FAISS.from_documents(split_docs, self.embeddings)
        
        # Save to disk
        os.makedirs(self.vector_store_path, exist_ok=True)
        vector_store.save_local(self.vector_store_path)
        print(f"  ✅ Vector store saved to {self.vector_store_path}")
        
        return vector_store
    
    def index_documentation(self):
        """Main indexing pipeline"""
        print("=" * 60)
        print("🚀 AEM Documentation Indexing Pipeline")
        print("=" * 60)
        
        # Step 1: Load documents
        documents = self.load_aem_documentation()
        
        # Step 2: Create embeddings and vector store
        vector_store = self.create_vector_store(documents)
        
        print("\n" + "=" * 60)
        print("✅ Indexing Complete!")
        print("=" * 60)
        print(f"📊 Total chunks indexed: {vector_store.index.ntotal}")
        print(f"💾 Vector store location: {self.vector_store_path}")
        print("\n🎯 Your RAG chatbot is now ready to answer AEM questions!")
        
        return vector_store

def main():
    """Run the indexing process"""
    indexer = AEMDocumentationIndexer()
    indexer.index_documentation()

if __name__ == "__main__":
    main()

