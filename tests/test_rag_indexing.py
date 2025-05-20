import pytest
from dotenv import load_dotenv
from rag_chatbot.rag_indexing import PDFLoader, RAGIndexing
import warnings
import loguru

warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

load_dotenv()


@pytest.fixture
def pdf_file():
    return "tests/test.pdf"


def test_pdf_loader(pdf_file):
    loader = PDFLoader(pdf_file)
    documents = loader.load()
    assert len(documents) > 0, "PDF loading failed or returned no documents."
    assert all(hasattr(doc, "page_content") for doc in documents), (
        "Documents do not have 'page_content' attribute."
    )
    assert all(hasattr(doc, "metadata") for doc in documents), (
        "Documents do not have 'metadata' attribute."
    )


def test_rag_indexing(pdf_file):
    rag_indexing = RAGIndexing(
        model="text-embedding-ada-002",
        persist_directory="./chroma_langchain_db",
        logger=loguru.logger,
    )

    rag_indexing.create_index(pdf_file)
