#!/bin/python3

from typing import Optional, List
from urllib.parse import urlparse, ParseResult
from urllib.robotparser import RobotFileParser, RequestRate

import time
import collections

LastCrawl: collections.namedtuple = collections.namedtuple("LastCrawl", ["requests", "seconds"])


class Robots:
    def __init__(self):
        self.user_agent: str = "Rover"
        self.parsers: dict = {}
        self.crawl_time: dict = {}
        self.max_age: int = 60 * 60  # 1 Hour
        self.default_rate: RequestRate = RequestRate(2, 1)  # One Request Every Half A Second (2 Requests Per Second)

    def get_site_key(self, url: str) -> Optional[str]:
        result: ParseResult = urlparse(url=url)

        # Determine Hostname If Possible
        hostname: str = result.hostname
        if hostname is None:
            hostname: str = result.path.split(sep="/")[0]

        # Failed To Get Hostname, So Return False
        if hostname == "":
            return None

        # Determine If URL Has Scheme
        scheme: str = "http://"  # Default To HTTP For 302 Redirect
        if result.scheme != "":
            scheme: str = f"{result.scheme}://"

        # Determine If URL Has Port Number
        port: str = ""
        if result.port is not None:
            port: str = f":{result.port}"

        encrypted_site_key: str = f"https://{hostname}{port}"
        site_key: str = f"{scheme}{hostname}{port}"

        # If Encrypted Version Available, Use It
        if site_key != encrypted_site_key and encrypted_site_key in self.parsers:
            site_key: str = encrypted_site_key

        return site_key

    def get_parser(self, url: str) -> Optional[RobotFileParser]:
        site_key: Optional[str] = self.get_site_key(url=url)
        robots: str = f"{site_key}/robots.txt"

        # If No Site Key, No Way To Responsibly Crawl
        if site_key is None:
            return None

        # Check If Already Cached
        if site_key not in self.parsers:
            self.parsers[site_key] = RobotFileParser()

        # Check If Cache Is Older Than Max Age (Modified Time is 0 If Never Downloaded)
        age: int = int(time.time() - self.parsers[site_key].mtime())
        if age >= self.max_age:
            self.parsers[site_key].set_url(robots)
            self.parsers[site_key].read()

        return self.parsers[site_key]

    def get_site_last_crawl(self, url: str) -> Optional[LastCrawl]:
        site_key: Optional[str] = self.get_site_key(url=url)

        # If No Site Key, No Way To Responsibly Crawl
        if site_key is None:
            return None

        # If Not Set, Return None
        if site_key not in self.crawl_time:
            return None

        return self.crawl_time[site_key]

    def set_site_last_crawl(self, url: str, crawl_time: Optional[int] = None, crawls: Optional[int] = None):
        site_key: Optional[str] = self.get_site_key(url=url)

        # If No Site Key, No Way To Responsibly Crawl
        if site_key is None:
            return

        # If Time Not Specified, Assume Crawled Now
        if crawl_time is None:
            crawl_time = int(time.time())

        if crawls is None and site_key in self.crawl_time:
            # Assuming Adding One Crawl
            crawls, _ = self.crawl_time[site_key]
            crawls += 1
        elif crawls is None:
            # Assume First Crawl
            crawls: int = 1

        self.crawl_time[site_key] = LastCrawl(crawls, crawl_time)

    def hit_rate_limit(self, url: str) -> bool:
        rate: Optional[RequestRate] = self.get_crawl_rate(url=url)

        # If Site Does Not Specify A Rate, Get Our Default
        if rate is None:
            rate: RequestRate = self.default_rate

        last_crawl: Optional[LastCrawl] = self.get_site_last_crawl(url=url)

        # No Last Crawl Means Rate Limit Is Fine
        if last_crawl is None:
            return False

        last_crawl_seconds: int = int(time.time()-last_crawl.seconds)

        if last_crawl_seconds < rate.seconds and last_crawl.requests >= rate.requests:
            # Hit Rate Limit, Alert Caller
            return True
        elif last_crawl_seconds > rate.seconds:
            # Reset The Crawl Count If Past Rate Limit Time
            self.set_site_last_crawl(url=url, crawl_time=last_crawl.seconds, crawls=0)

        # Didn't Hit Rate Limit Yet, Continue
        return False

    def can_crawl(self, url: str) -> bool:
        parser: Optional[RobotFileParser] = self.get_parser(url=url)

        if parser is None:
            return False

        return parser.can_fetch(self.user_agent, url=url)

    def can_crawl_now(self, url: str) -> bool:
        return self.can_crawl(url=url) and not self.hit_rate_limit(url=url)

    def get_crawl_rate(self, url: str) -> Optional[RequestRate]:
        parser: Optional[RobotFileParser] = self.get_parser(url=url)

        return parser.request_rate(self.user_agent)

    def get_sitemaps(self, url: str) -> Optional[List[str]]:
        parser: Optional[RobotFileParser] = self.get_parser(url=url)

        return parser.site_maps()
