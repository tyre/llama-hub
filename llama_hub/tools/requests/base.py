"""Requests Tool."""

from typing import Optional
from urllib.parse import urlparse

import requests
from llama_index.tools.tool_spec.base import BaseToolSpec

INVALID_URL_PROMPT = "This url did not include a hostname or scheme. Please determine the complete URL and try again."


class RequestsToolSpec(BaseToolSpec):
    """Requests Tool"""

    spec_functions = ["get_request", "post_request", "patch_request"]

    def __init__(self, headers: Optional[dict] = {}):
        self.headers = headers

    def get_request(self, url: str, params: Optional[dict] = {}):
        """
        Use this to GET content from a website.

        Args:
            url ([str]): The url to make the get request against
            params (Optional[dict]): the parameters to provide with the get request

        """
        if not self._valid_url(url):
            return INVALID_URL_PROMPT

        res = requests.get(url, headers=self.headers, params=params)
        return res.json()

    def post_request(self, url: str, data: Optional[dict] = {}):
        """
        Use this to POST content to a website.

        Args:
            url ([str]): The url to make the get request against
            data (Optional[dict]): the key-value pairs to provide with the get request

        """
        if not self._valid_url(url):
            return INVALID_URL_PROMPT

        res = requests.post(url, headers=self.headers, json=data)
        return res.json()

    def patch_request(self, url: str, data: Optional[dict] = {}):
        """
        Use this to PATCH content to a website.

        Args:
            url ([str]): The url to make the get request against
            data (Optional[dict]): the key-value pairs to provide with the get request

        """
        if not self._valid_url(url):
            return INVALID_URL_PROMPT

        requests.patch(url, headers=self.headers, json=data)

    def _valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme and parsed.hostname
