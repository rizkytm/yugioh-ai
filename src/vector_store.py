from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings

# Set environment variable to avoid tokenizer parallelism warning
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from dotenv import load_dotenv
load_dotenv()

class VectorStoreBuilder:
    def __init__(self,csv_path:str,persist_dir:str="chroma_db"):
        self.csv_path = csv_path
        self.persist_dir = persist_dir
        self.embedding = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
    
    def build_and_save_vectorstore(self):
        loader = CSVLoader(
            file_path=self.csv_path,
            encoding='utf-8',
            metadata_columns=[]
        )

        data = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Smaller chunks for better context preservation
            chunk_overlap=200,  # Add overlap to maintain context between chunks
            separators=["\n\n", "\n", " ", ""]  # Better separators for card data
        )
        texts = splitter.split_documents(data)

        db = Chroma.from_documents(texts,self.embedding,persist_directory=self.persist_dir)
        # ChromaDB automatically persists when persist_directory is specified

    def load_vector_store(self):
        return Chroma(persist_directory=self.persist_dir,embedding_function=self.embedding)



