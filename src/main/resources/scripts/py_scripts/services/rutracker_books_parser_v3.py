import json
import os
import pickle
import time
import numpy
import asyncio
import aiohttp
from aioselenium import Remote, Keys
from pathlib import Path

import bs4.element
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from selenium.common.exceptions import InvalidCookieDomainException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from services import database_service as db_service

from configs.proxy_auth_data import login as proxy_login, password as proxy_password, server as proxy_server
from configs.rutracker_auth_data import login as tracker_login, password as tracker_password


class Parser:
    def __init__(self, book_urls=None):
        self.matches = {
            "year": "Год выпуска",
            "last_name": "Фамилия автора",
            "fist_name": "Имя автора",
            "executor": "Исполнитель",
            "cycle_name": "Цикл/серия",
            "book_number": "Номер книги",
            "genre": "Жанр",
            "edition_type": "Тип издания",
            "category": "Категория",
            "audio_codec": "Аудиокодек",
            "bitrate": "Битрейт",
            "bitrate_type": "Вид битрейта",
            "sampling_frequency": "Частота дискретизации",
            "count_of_channels": "Количество каналов (моно-стерео)",
            "book_duration": "Время звучания",
            "description": "Описание",
        }
        self.login_url = "https://rutracker.org/forum/login.php"
        self.book_search_url = "https://rutracker.org/forum/tracker.php?f=2387"
        self.book_urls = book_urls

    async def run(self):

        if self.book_urls is not None:
            book_urls_list = numpy.array_split(self.book_urls, len(self.book_urls))
        else:
            try:
                options = webdriver.ChromeOptions()
                options.add_argument(f"user-agent={UserAgent().chrome}")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--headless")

                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    seleniumwire_options={
                        "proxy": {
                            "https": f"https://{proxy_login}:{proxy_password}@{proxy_server}"
                        }
                    },
                    options=options
                )
                await self.login_to_site(driver)
                book_urls_list = list(
                    map(lambda url: [url], self.flatten(await self.get_list_of_list_of_book_urls(driver)))
                )
            finally:
                driver.close()
                driver.quit()
        await asyncio.gather(*[self.get_book_urls(book_urls) for book_urls in book_urls_list])

    async def extend_books_to_db(self, books_data):
        # self.save_to_tmp_file_and_get(f'./books_data/data{index}.json', books_data)
        if len(books_data) == 0:
            return print("done!")
        res = db_service.json_to_db(books_data)
        if isinstance(res, Exception):
            print("json_to_db exception:\n" + str(res))
        else:
            print("done!")

    def save_to_tmp_file_and_get(tmp_file, books_data):
        # with open(tmp_file, 'w', encoding='utf-8') as f:
        #     json.dump(books_data, f)
        with open(tmp_file, 'r', encoding='utf-8') as f:
            books_data = json.load(f)
        return books_data

    async def get_book_urls(self, book_urls=[]):
        capabilities = {
            "browserName": "chrome",
        }
        command_executor = os.getenv('SELENIUM_CLUSTER')
        async with aiohttp.ClientSession() as session:
            remote = await Remote.create(command_executor, capabilities, session)
            async with remote as driver:
                try:
                    await self.login_to_site(driver)
                    book_data_list = list(map(lambda book_page_url: await self.get_book_data(driver, book_page_url), book_urls))
                    await self.extend_books_to_db(book_data_list)
                finally:
                    # driver.close()
                    driver.quit()

    async def login_to_site(self, driver):
        cookie_file_name = f"./cookies/{tracker_login}_cookies"
        cookie_path = Path(cookie_file_name)
        need_auth = False
        if Path.exists(cookie_path) and cookie_path.is_file():
            try:
                for cookie in pickle.load(open(cookie_file_name, "rb")):
                    driver.add_cookie(cookie)
            except InvalidCookieDomainException as ex:
                need_auth = True
        else:
            need_auth = True

        driver.get(self.login_url)

        if need_auth:
            login_input = driver.find_element(By.XPATH, "//input[@name='login_username'][not(@id='top-login-uname')]")
            login_input.clear()
            login_input.send_keys(tracker_login)

            password_input = driver.find_element(By.XPATH, "//input[@name='login_password'][not(@id='top-login-pwd')]")
            password_input.clear()
            password_input.send_keys(tracker_password)
            password_input.send_keys(Keys.ENTER)
            time.sleep(1)
            with open(cookie_file_name, 'wb+') as f:
                pickle.dump(driver.get_cookies(), f)
        time.sleep(1)

    # def get_books_data(self):
    #     try:
    #         if self.book_urls is None:
    #             book_urls = self.flatten(self.get_list_of_list_of_book_urls())
    #         else:
    #             book_urls = self.book_urls
    #         return list(map(lambda book_page_url: self.get_book_data(book_page_url), book_urls))
    #     finally:
    #         self.driver.close()
    #         self.driver.quit()

    def flatten(self, t):
        return [item for sublist in t for item in sublist]

    async def get_list_of_list_of_book_urls(self, driver):
        urls = self.get_page_urls(driver)
        return list(map(lambda book_list_url: self.get_book_page_urls(driver, book_list_url), urls))

    def get_page_urls(self, driver):
        driver.get(self.book_search_url)
        elems = driver.find_elements(By.CLASS_NAME, "pg")
        result = list(set(map(lambda el: el.get_attribute("href"), elems)))
        result.insert(0, self.book_search_url)
        return result

    def get_book_page_urls(self, driver, book_list_url):
        if driver.current_url != book_list_url:
            driver.get(book_list_url)
        elems = driver.find_elements(By.XPATH, "//tr[starts-with(@id,'trs-tr-')]/td[4]/div[1]/a")
        return list(map(lambda el: el.get_attribute("href"), elems))

    async def get_book_data(self, driver, book_page_url):
        book_data = {}
        await driver.get(book_page_url)
        soup = bs(driver.page_source, features="html.parser")
        root_item = soup.find('div', attrs={'class': 'post_body'})
        for key in self.matches.keys():
            book_data[key] = self.get_book_data_by_type(root_item, self.matches[key])
        return book_data

    def get_book_data_by_type(self, root_item, book_data_type):
        items = root_item.contents

        def cut_off_excess(str):
            if str.startswith(":"):
                str = str.replace(":", "", 1)
            return str.strip()

        for i, item in items:
            if str.startswith(str.lstrip(item.text), book_data_type):
                if book_data_type == "Описание":
                    text = str.strip(item.text[10:])
                    if len(text) > 0:
                        val = text
                    else:
                        val = ""
                    for j in range(i + 1, len(items)):
                        it = items[j]
                        if type(it) == bs4.element.NavigableString:
                            val += it.text + "\n\n"
                        else:
                            if it.attrs.get("class") is not None and "post-hr" in it.attrs.get("class"):
                                break
                    return cut_off_excess(val)
                else:
                    return cut_off_excess(items[i + 1].text)
        return ""
