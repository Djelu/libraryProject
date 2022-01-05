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

from chromeDriver.configs.proxy_auth_data import login as proxy_login, password as proxy_password, server as proxy_server
from chromeDriver.configs.rutracker_auth_data import login as tracker_login, password as tracker_password

url = "https://rutracker.org/forum/tracker.php?f=2387"

proxy_options = {
    "proxy": {
        "https": f"http://{proxy_login}:{proxy_password}@{proxy_server}"
    }
}

service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={UserAgent().chrome}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")

driver = webdriver.Chrome(
    service=service,
    seleniumwire_options=proxy_options,
    options=options
)

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

results = []


def login_to_site():
    cookie_file_name = f"{tracker_login}_cookies"
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

    if need_auth:
        auth()
        pickle.dump(driver.get_cookies(), open(cookie_file_name, "wb"))
    if driver.current_url != url:
        driver.get(url)
    time.sleep(1)


def auth():
    login_input = driver.find_element(By.XPATH, "//input[@name='login_username'][not(@id='top-login-uname')]")
    login_input.clear()
    login_input.send_keys(tracker_login)

    password_input = driver.find_element(By.XPATH, "//input[@name='login_password'][not(@id='top-login-pwd')]")
    password_input.clear()
    password_input.send_keys(tracker_password)
    password_input.send_keys(Keys.ENTER)
    time.sleep(1)


def get_search_pages():
    elems = driver.find_elements(By.CLASS_NAME, "pg")
    return set(map(lambda el: el.get_attribute("href"), elems))


def open_new_tab(page_url):
    driver.execute_script(f"window.open('{page_url}');")


def close_current_tab():
    if len(driver.window_handles) < 2:
        open_new_tab("")
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def get_rows_data():
    elems = driver.find_elements(By.XPATH, "//tr[starts-with(@id,'trs-tr-')]/td[4]/div[1]/a")
    return list(map(lambda el: {
        "href": el.get_attribute("href"),
        "row_name": el.text
    }, elems))


def get_book_data_by_type(root_item, book_data_type):
    items = root_item.contents
    i = 0
    for item in items:
        if item.text == book_data_type:
            if book_data_type == "Описание":
                val = ""
                for j in range(i + 1, items.__len__() - 1):
                    if type(items[j]) == bs4.element.NavigableString:
                        val += items[j].text + "\n\n"
                    else:
                        if items[j].attrs.get("class") is not None and "post-hr" in items[j].attrs.get("class"):
                            return cut_off_excess(val)

            else:
                return cut_off_excess(items[i + 1].text)
        i = i + 1
    return ""


def cut_off_excess(val):
    if val.startswith(":"):
        val = val.replace(":", "", 1)
    return val.strip()


def get_book_data(row_data):
    soup = bs(driver.page_source, features="html.parser")
    root_item = soup.find('div', attrs={'class': 'post_body'})
    book_data = {
        "url": row_data["href"],
        "row_name": row_data["row_name"],
        "book_name": root_item.find("span").text
    }
    for key in matches.keys():
        book_data[key] = get_book_data_by_type(root_item, matches[key])
    return book_data


def get_books_data(page_url):
    result = []
    if page_url is not None:
        driver.get(page_url)
    for row_data in get_rows_data():
        driver.get(row_data["href"])
        books_data = get_book_data(row_data)
        result.append(books_data)
    close_current_tab()
    return result


def get_all_books_data():
    search_pages = get_search_pages()
    result = get_books_data(None)
    for page_url in search_pages:
        result.extend(get_books_data(page_url))
    return result


def parse():
    driver.get(url)
    login_to_site()
    return get_all_books_data()


def flatten(t):
    return [item for sublist in t for item in sublist]
