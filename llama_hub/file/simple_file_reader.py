import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from llama_index.readers.base import BaseReader
from llama_index.readers.download import download_loader
from llama_index.readers.schema.base import Document

from llama_hub.utils import import_loader


class SimpleFileReader(BaseReader):
    """
    A simple reader for individual files. Takes in:
        - file_path: path to a local file
        - errors: passed directly to `open`
        - metadata: extra info attached to the parsed Document(s)
        - reader: an instance of BaseReader for further reading file contents
    """

    def __init__(
        self,
        file_path: str,
        errors: str = "ignore",
        metadata: Optional[Dict] = {},
        reader: Optional[BaseReader] = None,
    ) -> None:
        """Initialize with parameters."""
        super().__init__()
        self.file_path = Path(file_path)
        self.errors = errors
        self.reader = reader
        self.metadata = metadata

    def load_data(self) -> List[Document]:
        documents = []
        if self.reader:
            documents = self.reader.load_data(
                file=self.file_path, extra_info=self.metadata
            )
        else:
            data = ""
            # do standard read
            with open(self.file_path, "r", errors=self.errors) as f:
                data = f.read()
                documents.append(Document(text=data, extra_info=self.metadata))
        return documents
