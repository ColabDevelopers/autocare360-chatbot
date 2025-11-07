"""
Data loader for static content (text files, PDFs, etc.)
"""
import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DataLoader:
    """Loads and processes static data files."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.supported_extensions = [".txt", ".md", ".json", ".pdf"]

    def load_all_documents(self) -> str:
        """
        Load all documents from the data directory and return as formatted string.

        Returns:
            str: Concatenated content from all documents
        """
        if not self.data_dir.exists():
            logger.warning(f"Data directory {self.data_dir} does not exist")
            return ""

        content_parts = []

        for file_path in self.data_dir.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.supported_extensions
            ):
                try:
                    content = self._load_file(file_path)
                    if content:
                        content_parts.append(f"File: {file_path.name}\n{content}\n")
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")

        return "\n".join(content_parts)

    def _load_file(self, file_path: Path) -> str:
        """Load content from a single file based on its extension."""
        suffix = file_path.suffix.lower()

        if suffix == ".json":
            return self._load_json(file_path)
        elif suffix in [".txt", ".md"]:
            return self._load_text(file_path)
        elif suffix == ".pdf":
            return self._load_pdf(file_path)
        else:
            logger.warning(f"Unsupported file type: {suffix}")
            return ""

    def _load_json(self, file_path: Path) -> str:
        """Load and format JSON content."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            # Handle array of objects
            content_parts = []
            for item in data:
                if isinstance(item, dict):
                    title = item.get("title", "Unknown")
                    content = item.get("content", str(item))
                    content_parts.append(f"Title: {title}\nContent: {content}")
                else:
                    content_parts.append(str(item))
            return "\n\n".join(content_parts)
        elif isinstance(data, dict):
            # Handle single object
            return json.dumps(data, indent=2)
        else:
            return str(data)

    def _load_text(self, file_path: Path) -> str:
        """Load plain text or markdown content."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _load_pdf(self, file_path: Path) -> str:
        """Load PDF content using PyPDF2."""
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
            return ""

        try:
            reader = PdfReader(file_path)
            content = []
            for page in reader.pages:
                content.append(page.extract_text())
            return "\n".join(content)
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return ""
