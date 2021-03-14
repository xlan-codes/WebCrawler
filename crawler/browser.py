#!/bin/python3

# Bot Testing Site
# https://bot.sannysoft.com/
from typing import Optional, List
from urllib.parse import urlparse

from easyprocess import EasyProcessError
from seleniumwire import webdriver
from pyvirtualdisplay import Display
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire.request import Request

from crawler.robots import Robots

import os


class Browser:
    def __init__(self):
        self.user_agent: str = "Rover/0.1 (https://alexisevelyn.me/) - Page Not Setup Yet"
        self.headless: bool = False
        self.display: Optional[Display] = None
        self.options: Optional[Options] = None
        self.browser: Optional[WebDriver] = None
        self.robots: Robots = Robots()
        self.script_timeout: int = 40  # 40 Seconds
        self.page_timeout: int = 20  # 20 Seconds
        self.width: int = 1920
        self.height: int = 1080

        # Domains To Block
        self.blocklist: List[str] = []

    def setup_browser(self):
        # Start Headless Display
        try:
            self.display = Display(visible=False, size=(self.width, self.height))
            self.display.start()
        except EasyProcessError as e:
            self.headless: bool = True

        # Setup Chrome/Chromium - https://peter.sh/experiments/chromium-command-line-switches/
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--disable-blink-features=AutomationControlled')  # Disable WebDriver Detection
        self.options.add_argument(f'--user-agent={self.user_agent}')  # To Identify Bot To Server Owners

        # Disable Code That Might Take CPU Cycles
        self.options.add_argument('--disable-extensions')  # Chrome Apps/Extensions
        # self.options.add_argument('--disable-plugins')  # No Longer Exists (Used To Be For Flash/Java/etc...)
        self.options.add_argument('--disable-notifications')  # Disable Website Notification Capabilities
        self.options.add_argument('--disable-sync')  # Disable Syncing Chrome Account Data

        # Force Lite Mode Pages
        # self.options.add_argument('--force-enable-lite-pages')  # Force Lite Mode Pages

        # To Disable Accidental Audio Playing
        self.options.add_argument('--mute-audio')  # Disables Audio Playing

        # self.options.add_argument('--incognito')  # Incognito Mode
        # self.options.add_argument('--no-referrers')  # Hide Referral Websites
        # self.options.add_argument('--no-experiments')  # Disable Chrome Flags
        # self.options.add_argument('--remote-debugging-port=9222')  # For Debugging

        if self.headless:
            # print("No V-Screen Available!!! Starting Headless!!!")
            self.options.add_argument('--headless')

    def start_browser(self):
        undetectable_driver_path: str = "./chromedriver"
        normal_driver_path: str = "chromedriver"

        if os.path.exists(undetectable_driver_path):
            # Undetectable Driver
            driver_path: str = undetectable_driver_path
        else:
            # Regular Driver
            driver_path: str = normal_driver_path

        self.browser = webdriver.Chrome(executable_path=driver_path, options=self.options)

        # Set Default Page Size
        self.browser.set_window_size(width=self.width, height=self.height)

        # Set Timeout To Prevent Hanging On Page
        self.browser.set_page_load_timeout(time_to_wait=self.page_timeout)
        self.browser.set_script_timeout(time_to_wait=self.script_timeout)

        # Intercept Requests To Decide Blocking
        self.browser.request_interceptor = self._intercept_requests

    def quit(self):
        self.browser.quit()

    def retrieve_feeds(self) -> dict:
        rss: List[WebElement] = self.browser.find_elements_by_css_selector('link[type="application/rss+xml"]')
        atom: List[WebElement] = self.browser.find_elements_by_css_selector('link[type="application/atom+xml"]')

        return {
            "rss": rss,
            "atom": atom
        }

    def retrieve_links(self) -> List[WebElement]:
        return self.browser.find_elements_by_tag_name(name="a")

    def retrieve_sitemaps(self, url: str) -> Optional[List[str]]:
        return self.robots.get_sitemaps(url=url)

    def retrieve_code(self) -> str:
        return self.browser.page_source

    def screenshot(self, file: str):
        # From: https://stackoverflow.com/a/52572919/6828099
        original_size = self.browser.get_window_size()
        required_width = self.browser.execute_script('return document.body.parentNode.scrollWidth')
        required_height = self.browser.execute_script('return document.body.parentNode.scrollHeight')

        try:
            self.browser.set_window_size(required_width, required_height)

            body: WebElement = self.browser.find_element_by_tag_name('body')
            body.screenshot(filename=file)
        except NoSuchElementException as e:
            print("Failed To Find Body!!!")
            self.browser.save_screenshot(filename=file)
        finally:
            # To Ensure Size Is Reset Even On Failure Of Finding Body Element
            self.browser.set_window_size(original_size['width'], original_size['height'])

    def can_crawl_now(self, url: str) -> bool:
        return self.robots.can_crawl_now(url=url) and not self.should_block_request(url=url)

    def get_requests(self) -> List[Request]:
        return self.browser.requests

    def _intercept_requests(self, request: Request):
        # Intercept Network Requests - E.g. Block Ads/Malware
        if self.should_block_request(url=request.url):
            request.abort()

    def should_block_request(self, url: str):
        # Deny Request General Method
        # I May Add More Advanced Blocking Patterns Later - Potentially To Match AdblockPlus
        # For Now, We Just Block At The Domain Level
        if urlparse(url=url).hostname in self.blocklist:
            return True

        return False

    def get(self, url: str) -> bool:
        if self.robots.can_crawl_now(url=url):
            # Get Page
            self.browser.get(url=url)

            # Mark Attempt At Retrieving Page
            self.robots.set_site_last_crawl(url=url)
            return True
        return False
