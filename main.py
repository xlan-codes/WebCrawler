#!/bin/python3
from typing import List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from crawler.browser import Browser

import os

working_dir: str = "working"
screenshot_file: str = os.path.join(working_dir, "webpage.png")


def setup():
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)


if __name__ == "__main__":
    # TODO: Add Support For Feeds and Crawl Wait Time

    # Setup Working Files
    setup()

    # Start Browser
    browser: Browser = Browser()
    browser.setup_browser()
    browser.start_browser()

    url: str = "https://foxnews.com/"
    successful: bool = False

    try:
        successful: bool = browser.get(url=url)
    except TimeoutException as e:
        print(f"Retrieving Page Timed Out: {url}")

    if successful:
        try:
            feeds: dict = browser.retrieve_feeds()

            rss: List[WebElement] = feeds["rss"]
            atom: List[WebElement] = feeds["atom"]

            if len(rss) > 0:
                print(f"Found {len(rss)} RSS Feed(s)")

                for feed in rss:
                    href: Optional[str] = feed.get_attribute(name="href")

                    if href is not None:
                        print(href)

            if len(atom) > 0:
                print(f"Found {len(atom)} Atom Feed(s)")

                for feed in atom:
                    href: Optional[str] = feed.get_attribute(name="href")

                    if href is not None:
                        print(href)
        except TimeoutException as e:
            print(f"Feed Retrieval Timed Out: {url}")

        # try:
        #     browser.screenshot(file=screenshot_file)
        # except TimeoutException as e:
        #     print(f"Screenshot Page Timed Out: {url}")

        # try:
        #     links: List[WebElement] = browser.retrieve_links()
        #     if len(links) > 0:
        #         print(f"Found {len(links)} Link(s)")
        #
        #         for link in links:
        #             href: Optional[str] = link.get_attribute(name="href")
        #
        #             if href is not None:
        #                 print(href)
        # except TimeoutException as e:
        #     print(f"Link Retrieval Timed Out: {url}")

    browser.quit()
