#!/bin/python3

import json
import feedparser

from typing import Union, List
from feedparser import FeedParserDict


class Feed:
    def __init__(self, feed: Union[str, dict]):
        if feed is dict:
            self.feed: dict = feed
        else:
            self.feed: FeedParserDict = feedparser.parse(feed)

    def get_entries(self) -> List[dict]:
        return self.get_feed()["entries"]

    def get_links(self) -> List[str]:
        links: List[str] = []
        for entry in self.get_entries():
            links.append(entry["link"])

        return links

    def get_feed(self) -> Union[FeedParserDict, dict]:
        return self.feed

    def get_feed_str(self) -> str:
        return json.dumps(self.feed)
