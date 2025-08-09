import os
from dotenv import load_dotenv

load_dotenv()
from typing import List
from langchain.schema import Document
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from rag_chatbot.data_loader import DataLoader
from hashlib import sha256
import loguru


class PDFLoader:
    """
        Loader for PDF files using PyMuPDFLoader.
    """
    def __init__(self, file_path:str):
        self.file_path = file_path
        self.loader = PyMuPDFLoader(file_path)

    def load(self)-> list[Document]:
        return self.loader.load()


class RAGIndexing:
    """
        Indexing class for creating a vector store from PDF documents.
    """
    def __init__(self, *args, **kwargs):
        """
            param args: Additional arguments for customization
            param kwargs: Keyword arguments for customization

        """
            
        self.args = args
        self.kwargs = kwargs
        self.dataloader = DataLoader()
        self.logger = kwargs.get("logger", loguru.logger)
        self.__create_embeddings()
        self.__init_vector_store()

    def __create_embeddings(self)-> None:
        """
            Create embeddings using OpenAI's text-embedding-ada-002 model.
        """
        model = self.kwargs.get("model", "text-embedding-ada-002")
        try:
            self.embeddings = OpenAIEmbeddings(
                model=model,
            )
        except Exception as e:
            raise Exception(f"Error creating embeddings using model : {model}: {e}")

    def __init_vector_store(self)-> None:
        """
            Initialize the vector store using Chroma.

        """
        persist_directory = self.kwargs.get(
            "persist_directory", "./chroma_langchain_db"
        )

        try:
            self.vector_store = Chroma(
                collection_name="PDFRAG",
                embedding_function=self.embeddings,
                persist_directory=persist_directory,
            )
        except Exception as e:
            raise Exception(
                f"Error initializing vector store at {persist_directory}: {e}"
            )

    def load_documents(self, file_path:str)-> list[Document]:

        """
            Load documents from a file or URL.
        """
        try:
            self.loader = self.dataloader.load(file_path)
            return self.loader
        except Exception as e:
            raise Exception(f"Error loading PDF (at {file_path}) document: {e}")

    def split_documents(self, documents):
        """
            Split documents into smaller chunks for better indexing.
            param documents: List of Document objects to split.
        """
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
            )

            all_splits = text_splitter.split_documents(documents)
            return all_splits
        except Exception as e:
            raise Exception(f"Error splitting documents: {e}")

    def create_index(self, file_path:str)-> None:
        """
            Create an index for the given file path.

            param file_path: Path to the file or URL to index.
        """
        try:
            # Create hash for uniqueness
            doc_hash = sha256(file_path.encode()).hexdigest()
            self.logger.info(f"Document hash: {doc_hash}")

            # Check if document already exists
            result = self.vector_store.get(where={"file_hash": doc_hash})
            if result and len(result.get("documents", [])) > 0:
                self.logger.info(f"Document with hash {doc_hash} already exists.")
                return

            # Load documents
            original_docs = self.load_documents(file_path)

            # Create new documents with updated metadata
            updated_docs = []
            for i, doc in enumerate(original_docs):
                updated_docs.append(
                    Document(
                        page_content=doc.page_content,
                        metadata={
                            **doc.metadata,
                            "file_hash": doc_hash,
                            "chunk_index": i,
                        },
                    )
                )

            # Add to vector store
            self.vector_store.add_documents(updated_docs)
            self.logger.info(f"Indexed {len(updated_docs)} chunks for {file_path}")

        except Exception as e:
            raise Exception(f"Error creating index: {e}")
