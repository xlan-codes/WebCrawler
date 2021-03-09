#!/bin/python3

# Bot Testing Site
# https://bot.sannysoft.com/
from typing import Optional, List

from easyprocess import EasyProcessError
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from crawler.robots import Robots


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

    def setup_browser(self):
        # Start Headless Display
        try:
            self.display = Display(visible=False, size=(self.width, self.height))
            self.display.start()
        except EasyProcessError as e:
            self.headless: bool = True

        # Setup Chrome/Chromium
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--disable-blink-features=AutomationControlled')  # Disable WebDriver Detection
        self.options.add_argument(f'--user-agent={self.user_agent}')  # To Identify Bot To Server Owners
        # self.options.add_argument('--remote-debugging-port=9222')  # For Debugging

        if self.headless:
            # print("No V-Screen Available!!! Starting Headless!!!")
            self.options.add_argument('--headless')

    def start_browser(self):
        self.browser = webdriver.Chrome(executable_path='chromedriver', options=self.options)
        self.browser.set_window_size(width=self.width, height=self.height)
        self.browser.set_page_load_timeout(time_to_wait=self.page_timeout)
        self.browser.set_script_timeout(time_to_wait=self.script_timeout)

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

            self.browser.set_window_size(original_size['width'], original_size['height'])
        except NoSuchElementException as e:
            print("Failed To Find Body!!!")
            self.browser.save_screenshot(filename=file)

    def get(self, url: str) -> bool:
        if self.robots.can_crawl(url=url) and not self.robots.hit_rate_limit(url=url):
            # Get Page
            self.browser.get(url=url)

            # Mark Attempt At Retrieving Page
            self.robots.set_site_last_crawl(url=url)
            return True
        return False
