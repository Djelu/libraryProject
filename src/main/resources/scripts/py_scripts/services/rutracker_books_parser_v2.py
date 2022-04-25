import pickle
import time
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

from configs.proxy_auth_data import login as proxy_login, password as proxy_password, server as proxy_server
from configs.rutracker_auth_data import login as tracker_login, password as tracker_password


class Parser:
    matches = {
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

    def __init__(self, book_urls=None):
        self.login_url = "https://rutracker.org/forum/login.php"
        self.book_search_url = "https://rutracker.org/forum/tracker.php?f=2387"
        self.book_urls = book_urls

        try:
            options = webdriver.ChromeOptions()
            options.add_argument(f"user-agent={UserAgent().chrome}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--headless")

            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                seleniumwire_options={
                    "proxy": {
                        "https": f"https://{proxy_login}:{proxy_password}@{proxy_server}"
                    }
                },
                options=options
            )
            self.login_to_site()
        finally:
            self.driver.close()
            self.driver.quit()

    def get_book_urls(self):
        try:
            return self.flatten(self.get_list_of_list_of_book_urls())
        finally:
            self.driver.close()
            self.driver.quit()

    def login_to_site(self):
        cookie_file_name = f"./cookies/{tracker_login}_cookies"
        cookie_path = Path(cookie_file_name)
        need_auth = False
        if Path.exists(cookie_path) and cookie_path.is_file():
            try:
                for cookie in pickle.load(open(cookie_file_name, "rb")):
                    self.driver.add_cookie(cookie)
            except InvalidCookieDomainException as ex:
                need_auth = True
        else:
            need_auth = True

        self.driver.get(self.login_url)

        if need_auth:
            login_input = self.driver.find_element(By.XPATH, "//input[@name='login_username'][not(@id='top-login-uname')]")
            login_input.clear()
            login_input.send_keys(tracker_login)

            password_input = self.driver.find_element(By.XPATH, "//input[@name='login_password'][not(@id='top-login-pwd')]")
            password_input.clear()
            password_input.send_keys(tracker_password)
            password_input.send_keys(Keys.ENTER)
            time.sleep(1)
            with open(cookie_file_name, 'wb+') as f:
                pickle.dump(self.driver.get_cookies(), f)
        time.sleep(1)

    def get_books_data(self):
        try:
            if self.book_urls is None:
                book_urls = self.flatten(self.get_list_of_list_of_book_urls())
            else:
                book_urls = self.book_urls
            return list(map(lambda book_page_url: self.get_book_data(book_page_url), book_urls))
        finally:
            self.driver.close()
            self.driver.quit()

    def flatten(self, t):
        return [item for sublist in t for item in sublist]

    def get_list_of_list_of_book_urls(self):
        urls = self.get_page_urls()
        # if self.threads_count > 1:
        #     urls = self.get_your_thread_urls(urls)
        return list(map(lambda book_list_url: self.get_book_page_urls(book_list_url), urls))

    def get_your_thread_urls(self, urls):
        urls_len = len(urls)
        if urls_len > self.threads_count:
            thread_urls_count = urls_len / self.threads_count
        else:
            if urls_len < self.threads_count and self.thread_num > urls_len:
                return []
            thread_urls_count = 1
        first_index = self.thread_num*thread_urls_count-1
        return urls[first_index:first_index+thread_urls_count]

    def get_page_urls(self):
        self.driver.get(self.book_search_url)
        elems = self.driver.find_elements(By.CLASS_NAME, "pg")
        result = list(set(map(lambda el: el.get_attribute("href"), elems)))
        result.insert(0, self.book_search_url)
        return result

    def get_book_page_urls(self, book_list_url):
        if self.driver.current_url != book_list_url:
            self.driver.get(book_list_url)
        elems = self.driver.find_elements(By.XPATH, "//tr[starts-with(@id,'trs-tr-')]/td[4]/div[1]/a")
        return list(map(lambda el: el.get_attribute("href"), elems))

    def get_book_data(self, book_page_url):
        book_data = {}
        self.driver.get(book_page_url)
        soup = bs(self.driver.page_source, features="html.parser")
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
