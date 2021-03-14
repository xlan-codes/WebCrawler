#!/bin/python3
# TODO: Add means of checking the last pickle save time and starting a new instance if the pickle is too old

from typing import List, Optional

from requests import Response
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire.request import Request

from crawler.browser import Browser
from crawler.feed import Feed
from crawler.sitemap import Sitemap

import os
import pickle
import requests

# Directories
working_dir: str = "working"
pickle_dir: str = os.path.join(working_dir, "pickles")
blocklists_dir: str = os.path.join(working_dir, "blocklists")
complete_blocklist: str = os.path.join(blocklists_dir, "complete-list.txt")

# Files
screenshot_file: str = os.path.join(working_dir, "webpage.png")
robots_pickle: str = os.path.join(pickle_dir, "robots.pickle")

# These lists contain content I don't want in the spider, that includes porn
# as porn is not what the spider is supposed to be crawling
blocklists: dict = {
    "abuse": "https://blocklistproject.github.io/Lists/alt-version/abuse-nl.txt",
    "ads": "https://blocklistproject.github.io/Lists/alt-version/ads-nl.txt",
    "drugs": "https://blocklistproject.github.io/Lists/alt-version/drugs-nl.txt",
    "fraud": "https://blocklistproject.github.io/Lists/alt-version/fraud-nl.txt",
    "malware": "https://blocklistproject.github.io/Lists/alt-version/malware-nl.txt",
    "phishing": "https://blocklistproject.github.io/Lists/alt-version/phishing-nl.txt",
    "piracy": "https://blocklistproject.github.io/Lists/alt-version/piracy-nl.txt",
    "porn": "https://blocklistproject.github.io/Lists/alt-version/porn-nl.txt",
    "ransomware": "https://blocklistproject.github.io/Lists/alt-version/ransomware-nl.txt",
    "redirect": "https://blocklistproject.github.io/Lists/alt-version/redirect-nl.txt",
    "scam": "https://blocklistproject.github.io/Lists/alt-version/scam-nl.txt",
    "tracking": "https://blocklistproject.github.io/Lists/alt-version/tracking-nl.txt"
}


def download_blocklists():
    # TODO: Write Down Last Download Date To Know When To Update
    with open(complete_blocklist, mode="w") as clist:
        for blocklist in blocklists.keys():
            response: Response = requests.get(url=blocklists[blocklist])

            if response.status_code != 200:
                continue

            with open(file=os.path.join(blocklists_dir, f"{blocklist}.txt"), mode="w") as f:
                f.writelines(response.text)
                f.close()

            total_list: List[str] = [x for x in response.text.split("\n") if not x.startswith("#")]  # Remove Comments
            total_list: List[str] = [x for x in total_list if not x.strip() == ""]  # Remove Blank Lines
            total_list: List[str] = [x for x in total_list if "/" not in x]  # Remove Invalid Addresses

            clist.writelines("\n".join(total_list))
        clist.close()


def import_blocklists() -> List[str]:
    with open(complete_blocklist, mode="r") as blocklist:
        blocked_domains: List[str] = [x.strip() for x in blocklist.readlines()]
        blocklist.close()

        return blocked_domains


def setup():
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    if not os.path.exists(pickle_dir):
        os.mkdir(pickle_dir)

    if not os.path.exists(blocklists_dir):
        os.mkdir(blocklists_dir)

    # TODO: Read TODO In Method!!!
    # download_blocklists()


if __name__ == "__main__":
    # TODO: Add Support For Feeds and Crawl Wait Time

    # Setup Working Files
    setup()

    # Start Browser
    browser: Browser = Browser()

    # Load Robots Class If Pickled
    if os.path.exists(robots_pickle):
        browser.robots = pickle.load(open(robots_pickle, mode='rb'))

    # Import BlockLists
    if os.path.exists(complete_blocklist):
        browser.blocklist = import_blocklists()

    browser.setup_browser()
    browser.start_browser()

    url: str = "https://www.reuters.com/"
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
        except StaleElementReferenceException as e:
            print(f"Feed Retrieval Failed Due To Page Refresh: {url}")

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
        except StaleElementReferenceException as e:
            print(f"Screenshot Page Failed Due To Page Refresh: {url}")

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
        except StaleElementReferenceException as e:
            print(f"Link Retrieval Failed Due To Page Refresh: {url}")

    browser.quit()
    pickle.dump(browser.robots, open(robots_pickle, mode="wb+"))
