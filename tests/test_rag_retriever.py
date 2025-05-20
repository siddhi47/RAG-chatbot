import pytest
from dotenv import load_dotenv

load_dotenv()

from rag_chatbot.rag_retrieval import RAGRetrieverGeneration
from langchain_chroma import Chroma
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
import warnings


warnings.filterwarnings("ignore", category=UserWarning, module="langchain")


@pytest.fixture
def pdf_file():
    return "tests/test.pdf"


def test_rag_graph(pdf_file):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",
    )
    vector_store = Chroma(
        collection_name="PDFRAG",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db",
    )

    llm = init_chat_model("gpt-3.5-turbo", model_provider="openai")
    rag_retrieval = RAGRetrieverGeneration(
        vector_store=vector_store,
        llm=llm,
    )

    rag_graph = rag_retrieval.graph_builder()
    retrieved_docs = rag_graph.invoke({"question": "Who is Santosh KC?"})
    print(retrieved_docs["answer"].content)

    retrieved_docs = rag_graph.invoke({"question": "Where does he teach"})
    print(retrieved_docs["answer"].content)
