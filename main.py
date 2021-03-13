#!/bin/python3
# TODO: Add means of checking the last pickle save time and starting a new instance if the pickle is too old

from typing import List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire.request import Request

from crawler.browser import Browser
from crawler.feed import Feed
from crawler.sitemap import Sitemap

import os
import pickle

# Directories
working_dir: str = "working"
pickle_dir: str = os.path.join(working_dir, "pickles")

# Files
screenshot_file: str = os.path.join(working_dir, "webpage.png")
robots_pickle: str = os.path.join(pickle_dir, "robots.pickle")


def setup():
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    if not os.path.exists(pickle_dir):
        os.mkdir(pickle_dir)


if __name__ == "__main__":
    # TODO: Add Support For Feeds and Crawl Wait Time

    # Setup Working Files
    setup()

    # Start Browser
    browser: Browser = Browser()

    # Load Robots Class If Pickled
    if os.path.exists(robots_pickle):
        browser.robots = pickle.load(open(robots_pickle, mode='rb'))

    browser.setup_browser()
    browser.start_browser()

    url: str = "https://example.com"
    successful: bool = False

    try:
        successful: bool = browser.get(url=url)
    except TimeoutException as e:
        print(f"Retrieving Page Timed Out: {url}")

    if successful:
        network_requests: List[Request] = browser.get_requests()

        # There will always be at least 1 request if successful (which it is if we are here)
        if len(network_requests) > 1:
            print(f"Found {len(network_requests)} Network Requests")
            for request in network_requests:
                if request.response:
                    print(f"{request.url} - {request.method} - {request.response.status_code} - {request.response.headers['Content-Type']}")
                    # print(f"{request.response.body}")  # For Later As Documentation Is Wrong

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

                        if browser.can_crawl_now(url=href):
                            print("RSS Feed Links:")
                            feed = Feed(feed=href)
                            print(feed.get_links())

            if len(atom) > 0:
                print(f"Found {len(atom)} Atom Feed(s)")

                for feed in atom:
                    href: Optional[str] = feed.get_attribute(name="href")

                    if href is not None:
                        print(href)

                        if browser.can_crawl_now(url=href):
                            print("Atom Feed Links:")
                            feed = Feed(feed=href)
                            print(feed.get_links())
        except TimeoutException as e:
            print(f"Feed Retrieval Timed Out: {url}")

        # TODO: Decide If I Should Pull URL Internally
        sitemaps: Optional[List[str]] = browser.retrieve_sitemaps(url=url)

        if sitemaps is not None and len(sitemaps) > 0:
            print(f"Found {len(sitemaps)} Sitemap(s)")

            for url in sitemaps:
                print(url)

                if browser.can_crawl_now(url=url):
                    sitemap: Sitemap = Sitemap(sitemap=url)
                    links: List[str] = sitemap.get_links()

                    for link in links:
                        print(link)

        try:
            browser.screenshot(file=screenshot_file)
        except TimeoutException as e:
            print(f"Screenshot Page Timed Out: {url}")

        try:
            links: List[WebElement] = browser.retrieve_links()
            if len(links) > 0:
                print(f"Found {len(links)} Link(s)")

                for link in links:
                    href: Optional[str] = link.get_attribute(name="href")

                    if href is not None:
                        print(href)
        except TimeoutException as e:
            print(f"Link Retrieval Timed Out: {url}")

    browser.quit()
    pickle.dump(browser.robots, open(robots_pickle, mode="wb+"))
