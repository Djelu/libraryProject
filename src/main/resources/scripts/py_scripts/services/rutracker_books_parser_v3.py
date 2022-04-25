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
    def __init__(self, ids=None):
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
        self.book_urls = self.get_urls(ids)

    async def run(self):
        if self.book_urls is not None:
            book_urls_list = numpy.array_split(self.book_urls, len(self.book_urls))
        else:
            book_urls_list = await self.get_book_url_list()

        book_urls_list = book_urls_list[0:1]
        async def foo(driver):
            await asyncio.gather(*[self.export_books_to_db(driver, book_urls) for book_urls in book_urls_list])

        await self.get_driver_and_do_async(foo)

    def get_urls(self, ids):
        return list(map(
            lambda id: f"https://rutracker.org/forum/viewtopic.php?t={id}",
            ids
        ))

    async def get_driver_and_do_async(self, func, *args):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument(f"user-agent={UserAgent().chrome}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            # options.add_argument("--headless")

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                seleniumwire_options={
                    "proxy": {
                        "https": f"https://{proxy_login}:{proxy_password}@{proxy_server}"
                    }
                },
                options=options
            )
            result = await func(driver, *args)
        finally:
            driver.close()
            driver.quit()
        return result

    def get_driver_and_do(self, func, *args):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument(f"user-agent={UserAgent().chrome}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            # options.add_argument("--headless")

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                seleniumwire_options={
                    "proxy": {
                        "https": f"https://{proxy_login}:{proxy_password}@{proxy_server}"
                    }
                },
                options=options
            )
            result = func(driver, *args)
        finally:
            driver.close()
            driver.quit()
        return result

    async def get_book_url_list(self):
        async def foo(driver):
            await self.login_to_site(driver)
            return list(map(
                lambda url: [url],
                self.flatten(
                    await self.get_list_of_list_of_book_urls(driver)
                )
            ))
        return await self.get_driver_and_do(foo)

    async def extend_books_to_db(self, books_data):
        # self.save_to_tmp_file_and_get(f'./books_data/data{index}.json', books_data)
        if len(books_data) == 0:
            return print("done!")
        res = db_service.json_to_db(books_data)
        if isinstance(res, Exception):
            print("json_to_db exception:\n" + str(res))
        else:
            print("done!")

    def save_to_tmp_file_and_get(self, tmp_file, books_data):
        # with open(tmp_file, 'w', encoding='utf-8') as f:
        #     json.dump(books_data, f)
        with open(tmp_file, 'r', encoding='utf-8') as f:
            books_data = json.load(f)
        return books_data

    async def export_books_to_db(self, d, book_urls=[]):
        capabilities = {
            "browserName": "chrome",
        }
        # d.session_id
        command_executor = d.service.service_url
        async with aiohttp.ClientSession() as session:
            remote = await Remote.create(command_executor, capabilities, session)
            async with remote as driver:
                try:
                    await self.login_to_site(driver)
                    book_data_list = [await self.get_book_data(driver, url) for url in book_urls]
                    await self.extend_books_to_db(book_data_list)
                finally:
                    # driver.close()
                    await driver.quit()

    async def login_to_site(self, driver):
        cookie_file_name = f"./cookies/{tracker_login}_cookies"
        cookie_path = Path(cookie_file_name)
        if Path.exists(cookie_path) and cookie_path.is_file():
            try:
                for cookie in pickle.load(open(cookie_file_name, "rb")):
                    await driver.add_cookie(cookie)
                need_auth = False
            except InvalidCookieDomainException as ex:
                need_auth = True
        else:
            need_auth = True

        await driver.get(self.login_url)

        if need_auth:
            login_input = await driver.find_element_by_xpath("//input[@name='login_username'][not(@id='top-login-uname')]")
            await login_input.clear()
            await login_input.send_keys(tracker_login)

            password_input = await driver.find_element_by_xpath("//input[@name='login_password'][not(@id='top-login-pwd')]")
            await password_input.clear()
            await password_input.send_keys(tracker_password)
            await password_input.send_keys(Keys.ENTER)
            time.sleep(1)
            with open(cookie_file_name, 'wb+') as f:
                pickle.dump(await driver.get_cookies(), f)
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
        book_list_urls = await self.get_page_urls(driver)
        return [await self.get_book_page_urls(driver, url) for url in book_list_urls]

    async def get_page_urls(self, driver):
        await driver.get(self.book_search_url)
        elems = await driver.find_elements(By.CLASS_NAME, "pg")
        result = list(set(map(lambda el: el.get_attribute("href"), elems)))
        result.insert(0, self.book_search_url)
        return result

    async def get_book_page_urls(self, driver, book_list_url):
        if driver.current_url != book_list_url:
            await driver.get(book_list_url)
        elems = await driver.find_elements(By.XPATH, "//tr[starts-with(@id,'trs-tr-')]/td[4]/div[1]/a")
        return list(map(lambda el: el.get_attribute("href"), elems))

    async def get_book_data(self, driver, book_page_url):
        book_data = {}
        await driver.get(book_page_url)
        soup = bs(await driver.source(), features="html.parser")
        root_item = soup.find("div", {"class": "post_body"})
        if root_item is None:
            book_data["no_book"] = True
            return book_data
        book_data["no_book"] = False

        img = root_item.find("img", {"class": "postImg"})
        if "post-img-broken" in img.attrs['class']:
            img_url = img.attrs['title']
        else:
            img_url = img.attrs['src']
        book_data["img_url"] = img_url

        book_page_id = book_page_url.split("?t=")[1]
        book_data["book_page_id"] = book_page_id

        table = soup.find("div", {"class": "post_wrap"}).find("table")
        if table is not None:
            a = table.find("a", {"data-topic_id": book_page_id})
            if a is not None:
                magnet_link = a.attrs['href']
                tor_size = table.find("span", {"id": "tor-size-humn"}).text
                book_data["magnet_link"] = magnet_link
                book_data["tor_size"] = tor_size

        for key in self.matches.keys():
            book_data[key] = self.get_book_data_by_type(root_item, self.matches[key])

        return book_data

    def get_book_data_by_type(self, root_item, book_data_type):
        items = root_item.contents

        def cut_off_excess(str):
            if str.startswith(":"):
                str = str.replace(":", "", 1)
            return str.strip()

        for i in range(len(items)):
            item = items[i]
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
