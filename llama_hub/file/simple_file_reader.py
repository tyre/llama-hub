from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from llama_index.readers.base import BaseReader
from llama_index.readers.download import download_loader
from llama_index.readers.schema.base import Document

from llama_hub.utils import import_loader

DEFAULT_FILE_EXTRACTOR: Dict[str, str] = {
    ".pdf": "PDFReader",
    ".docx": "DocxReader",
    ".pptx": "PptxReader",
    ".jpg": "ImageReader",
    ".png": "ImageReader",
    ".jpeg": "ImageReader",
    ".mp3": "AudioTranscriber",
    ".mp4": "AudioTranscriber",
    ".csv": "PagedCSVReader",
    ".epub": "EpubReader",
    ".md": "MarkdownReader",
    ".mbox": "MboxReader",
    ".eml": "UnstructuredReader",
    ".html": "UnstructuredReader",
    ".json": "JSONReader",
}

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
        file_path: Union[str, Path],
        errors: str = "ignore",
        metadata: Optional[Dict] = {},
        reader: Optional[BaseReader] = None,
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
    ) -> None:
        """Initialize with parameters."""
        super().__init__()
        self.file_path = Path(file_path)
        self.errors = errors
        self.metadata = metadata
        self.file_extractor = file_extractor or DEFAULT_FILE_EXTRACTOR
        self._reader = reader

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
    
    @property
    def reader(self) -> Optional[BaseReader]:
        if self._reader:
            return self._reader
        
        extracted_reader_type = self.file_extractor.get(self.file_path.suffix)
        if isinstance(extracted_reader_type, BaseReader):
            return extracted_reader_type()
        elif isinstance(extracted_reader_type, str):
            return import_loader(extracted_reader_type)()
        