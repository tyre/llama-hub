"""Simple Reader that reads transcript of youtube video."""
import re
from typing import Any, List, Optional

from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document

# regular expressions to match the different syntax of YouTube links
YOUTUBE_URL_PATTERNS = [
    r"^https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)",
    r"^https?://(?:www\.)?youtube\.com/embed/([\w-]+)",
    r"^https?://youtu\.be/([\w-]+)",  # youtu.be does not use www
]


class YoutubeTranscriptReader(BaseReader):
    """Youtube Transcript reader."""

    def __init__(self) -> None:
        try:
            import youtube_transcript_api
        except ImportError:
            raise ImportError(
                "Missing package: youtube_transcript_api.\n"
                "Please `pip install youtube_transcript_api` to use this Reader"
            )
        super().__init__()

    @staticmethod
    def _extract_video_id(yt_link) -> Optional[str]:
        for pattern in YOUTUBE_URL_PATTERNS:
            match = re.search(pattern, yt_link)
            if match:
                return match.group(1)

        # return None if no match is found
        return None

    def load_data(
        self,
        ytlinks: List[str],
        languages: Optional[List[str]] = ["en"],
        **load_kwargs: Any,
    ) -> List[Document]:
        """Load data from the input directory.

        Args:
            pages (List[str]): List of youtube links \
                for which transcripts are to be read.

        """
        from youtube_transcript_api import YouTubeTranscriptApi

        results = []
        for link in ytlinks:
            video_id = self._extract_video_id(link)
            if not video_id:
                raise ValueError(
                    f"Supplied url {link} is not a supported youtube URL."
                    "Supported formats include:"
                    "  youtube.com/watch?v=\{video_id\} "
                    "(with or without 'www.')\n"
                    "  youtube.com/embed?v=\{video_id\} "
                    "(with or without 'www.')\n"
                    "  youtu.be/{video_id\} (never includes www subdomain)"
                )
            transcript_chunks = YouTubeTranscriptApi.get_transcript(
                video_id, languages=languages
            )
            transcript = ""
            for chunk in transcript_chunks:
                transcript = transcript + chunk["text"] + "\n"
            results.append(Document(text=transcript, extra_info={"video_id": video_id}))
        return results


def is_youtube_video(url: str) -> bool:
    """
    Returns whether the passed in `url` matches the various YouTube URL formats
    """
    for pattern in YOUTUBE_URL_PATTERNS:
        if re.search(pattern, url):
            return True
    return False
