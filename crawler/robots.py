#!/bin/python3

from urllib.parse import urlparse, ParseResult
from urllib.robotparser import RobotFileParser

import time


class Robots:
    def __init__(self):
        self.user_agent: str = "Rover"
        self.parsers: dict = {}
        self.max_age: int = 60 * 60  # 1 Hour

    def can_crawl(self, url: str) -> bool:
        result: ParseResult = urlparse(url=url)

        # Determine Hostname If Possible
        hostname: str = result.hostname
        if hostname is None:
            hostname: str = result.path.split(sep="/")[0]

        # Failed To Get Hostname, So Return False
        if hostname == "":
            return False

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
        robots: str = f"{scheme}{hostname}{port}/robots.txt"

        # If Encrypted Version Available, Use It
        if site_key != encrypted_site_key and encrypted_site_key in self.parsers:
            site_key: str = encrypted_site_key

        # Check If Already Cached
        if site_key not in self.parsers:
            self.parsers[site_key] = RobotFileParser()

        # Check If Cache Is Older Than Max Age (Modified Time is 0 If Never Downloaded)
        age: int = int(time.time() - self.parsers[site_key].mtime())
        if age >= self.max_age:
            self.parsers[site_key].set_url(robots)
            self.parsers[site_key].read()

        return self.parsers[site_key].can_fetch(self.user_agent, url=url)
