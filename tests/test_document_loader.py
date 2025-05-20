import pytest
from dotenv import load_dotenv

load_dotenv()
from rag_chatbot.data_loader import DataLoader


@pytest.fixture
def url():
    return "https://www.uscis.gov/green-card/how-to-apply-for-a-green-card"


@pytest.fixture
def pdf_path():
    return "tests/test.pdf"


def test_load_url(url):
    dataloader = DataLoader()
    document = dataloader.load(url)


def test_pdf(pdf_path):
    dataloader = DataLoader()
    document = dataloader.load(pdf_path)
