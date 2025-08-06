import os
import mimetypes
from urllib.parse import urlparse
from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredURLLoader,
    UnstructuredHTMLLoader,
    UnstructuredFileLoader,
    UnstructuredMarkdownLoader,
    UnstructuredWordDocumentLoader,
    JSONLoader,
    CSVLoader,
)


class DataLoader:
    def __init__(self, encoding="utf-8"):
        """
        Load documents from web and different file formats
        """
        self.encoding = encoding

    def load(self, path_or_url: str)-> list:
        """
        load from url or file
        Supported file types: PDF, markdown, html, json, docx
        params:
            path_or_url (str): file path or url

        """

        if self._is_url(path_or_url):
            return self._load_url(path_or_url)
        elif os.path.isfile(path_or_url):
            return self._load_file(path_or_url)
        else:
            raise ValueError(f"Invalid path or URL: {path_or_url}")

    def _is_url(self, string:str) -> bool:
        parsed = urlparse(string)
        return parsed.scheme in ["http", "https"]

    def _load_url(self, url:str) -> list:
        try:
            return UnstructuredURLLoader(urls=[url]).load()
        except Exception as e:
            raise RuntimeError(f"Failed to load URL: {e}")

    def _load_file(self, file_path:str) -> list:
        ext = os.path.splitext(file_path)[-1].lower()
        mime, _ = mimetypes.guess_type(file_path)

        try:
            if ext == ".pdf":
                return PyPDFLoader(file_path).load()
            elif ext in [".txt", ".text"]:
                return TextLoader(file_path, encoding=self.encoding).load()
            elif ext in [".md"]:
                return UnstructuredMarkdownLoader(file_path).load()
            elif ext in [".html", ".htm"]:
                return UnstructuredHTMLLoader(file_path).load()
            elif ext == ".json":
                return JSONLoader(file_path, jq_schema=".[]").load()
            elif ext == ".docx":
                return UnstructuredWordDocumentLoader(file_path).load()
            elif ext == ".csv":
                return CSVLoader(file_path, encoding=self.encoding).load()
            else:
                # Fallback for unknown types (e.g. .csv, .xml, etc.)
                return UnstructuredFileLoader(file_path).load()
        except Exception as e:
            raise RuntimeError(f"Failed to load file: {file_path} — {e}")
