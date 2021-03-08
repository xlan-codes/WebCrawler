#!/bin/python3

from crawler.browser import Browser

import os

working_dir: str = "working"
screenshot_file: str = os.path.join(working_dir, "webpage.png")


def setup():
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)


if __name__ == "__main__":
    # Setup Working Files
    setup()

    # Start Browser
    browser: Browser = Browser()
    browser.setup_browser()
    browser.start_browser()

    successful = browser.get(url="https://sqa.stackexchange.com/questions/35338/fetch-all-the-links-on-a-page-that-are-within-the-same-class")

    if successful:
        browser.screenshot(file=screenshot_file)
