"""Remote file reader.

A loader that fetches an arbitrary remote page or file by URL and parses its contents.

"""

import math
import random
import tempfile
from hashlib import md5
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse
from urllib.request import Request, _UrlopenRet, urlopen

from llama_index import SimpleDirectoryReader, download_loader
from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document

from llama_hub.file.audio import AudioTranscriber
from llama_hub.youtube_transcript.base import (YoutubeTranscriptReader,
                                               is_youtube_video)


class RemoteReader(BaseReader):
    """General reader for any remote page or file."""

    def __init__(
        self,
        *args: Any,
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)

        self.file_extractor = file_extractor

    def load_data(self, url: str) -> List[Document]:
        extra_info = {"Source": url}

        response = self._load_from_url(url)
        url_type = response.info().get_content_type()
        documents = []
        match self._normalize_url_type(url=url, url_type=url_type):
            case "text/html" | "text/plain":
                text = "\n\n".join([str(el.decode("utf-8-sig")) for el in response])
                documents = [Document(text=text, extra_info=extra_info)]
            case "audio/mp3" | "audio/mp4":
                with self._local_file_from_response(url, response) as (filepath, _):
                    documents = AudioTranscriber(filepath)
            case "video/youtube":
                # TODO should we have another langauge, like english / french?
                documents = YoutubeTranscriptReader().load_data([url])
            case _:
                with self._local_file_from_remote_url(response) as (_, directory):
                    file_reader = None
                    if self.file_extractor:
                        file_extractor
                    loader = SimpleDirectoryReader(
                        directory,
                        file_metadata=(lambda _: extra_info),
                        file_extractor=self.file_extractor,
                    )
                    documents = loader.load_data()
        return documents

    @staticmethod
    def _load_from_url(url: str) -> Any:
        req = Request(url, headers={"User-Agent": "Magic Browser"})
        return urlopen(req)

    @staticmethod
    def _local_file_from_remote_url(url: str, response: Any):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = f"{temp_dir}/{RemoteReader._temp_filename_for_url(url)}"
            with open(filepath, "wb") as output:
                output.write(response.read())
                yield filepath, temp_dir

    @classmethod
    def _generate_filename_for_url(url: str) -> str:
        suffix = Path(urlparse(url).path).suffix
        # Include url hash and random number to guard against collisions
        url_hash = md5(url, usedforsecurity=False)
        random_int = math.floor(random.random() * 100000)
        return f"llama-hub-remote-{url_hash}-{random_int}{suffix}"

    @staticmethod
    def _normalize_url_type(url: str, url_type: str) -> str:
        """
        Normalizes an HTTP response Content-Type to include custom
        overrides.
        """
        if is_youtube_video(url):
            url_type = "video/youtube"
        return url_type
