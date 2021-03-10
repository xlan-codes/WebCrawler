#!/bin/python3
# TODO: Add Support For All Standard Formats - https://www.google.com/sitemaps/protocol.html

import json
import enum

import requests
import xmltodict

from requests import Response
from typing import Union, List, Optional
from pyexpat import ExpatError


def _retrieve_sitemap(url: str) -> Optional[str]:
    response: Response = requests.get(url=url)

    if response.status_code == 200:
        return response.text

    return None


class SitemapType(enum.Enum):
    INDEX = "index"
    GENERAL = "general"
    UNKNOWN = "unknown"


class Sitemap:
    def __init__(self, sitemap: Union[str, dict]):
        if sitemap is dict:
            self.sitemap: dict = sitemap
        else:
            response: Optional[str] = _retrieve_sitemap(url=sitemap)

            if response is None:
                print(f"Failed Retrieving Sitemap: {sitemap}")
                return

            try:
                self.sitemap: dict = xmltodict.parse(response)
            except ExpatError as e:
                # Sitemap is Malformed, So Quit Trying To Parse It
                self.sitemap: dict = {}

    def get_type(self) -> SitemapType:
        if "sitemapindex" in self.sitemap:
            return SitemapType.INDEX
        elif "urlset" in self.sitemap:
            return SitemapType.GENERAL
        else:
            return SitemapType.UNKNOWN

    def get_entries(self) -> List[dict]:
        if self.get_type() == SitemapType.INDEX:
            return self.sitemap["sitemapindex"]["sitemap"]
        elif self.get_type() == SitemapType.GENERAL:
            return self.sitemap["urlset"]["url"]

        return []

    def get_links(self) -> List[str]:
        links: List[str] = []
        for entry in self.get_entries():
            links.append(entry["loc"])

        return links

    def get_sitemap(self) -> dict:
        return self.sitemap

    def get_sitemap_str(self) -> str:
        return json.dumps(self.sitemap)
