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
            browser.screenshot(file=screenshot_file)
        except TimeoutException as e:
            print(f"Screenshot Page Timed Out: {url}")

        links: List[WebElement] = browser.retrieve_links()
        if len(links) > 0:
            print(f"Found {len(links)} Link(s)")

            for link in links:
                href: Optional[str] = link.get_attribute(name="href")

                if href is not None:
                    print(href)

    browser.quit()
