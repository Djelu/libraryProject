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

urls = []

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

db_book_ids = []
curr_book_ids = []


def login_to_site(url):
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

    if need_auth:
        auth()
        with open(cookie_file_name, 'wb+') as f:
            pickle.dump(driver.get_cookies(), f)

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
    return list(set(map(lambda el: el.get_attribute("href"), elems)))


def open_new_tab(page_url):
    driver.execute_script(f"window.open('{page_url}');")


def close_current_tab():
    if len(driver.window_handles) < 2:
        open_new_tab("")
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def get_rows_data(page_url):
    if page_url is not None:
        driver.get(page_url)
    elems = driver.find_elements(By.XPATH, "//tr[starts-with(@id,'trs-tr-')]/td[4]/div[1]/a")
    result = list(map(lambda el: {
        "book_page_id": el.get_attribute("href").split("t=")[1],
        "href": el.get_attribute("href"),
        "row_name": el.text
    }, elems))
    return exclude_existing_books(result)


def get_book_data_by_type(root_item, book_data_type):
    items = root_item.contents
    i = 0
    for item in items:
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


def exclude_existing_books(rows_data):
    def foo(row_data):
        book_page_id = row_data["book_page_id"]
        return book_page_id not in curr_book_ids and book_page_id not in db_book_ids
    return list(filter(foo, rows_data))


def get_books_data(page_url=None):
    result = []
    rows_data = get_rows_data(page_url)
    curr_book_ids.extend(list(map(lambda it: it["book_page_id"], rows_data)))
    count = len(rows_data)
    for row_data in rows_data:
        driver.get(row_data["href"])
        books_data = get_book_data(row_data)
        result.append(books_data)
        print(f"book: {len(result)}/{count}")
    close_current_tab()
    return result


def get_all_books_data():
    search_pages = get_search_pages()
    count = len(search_pages) + 1
    print(f"page: {1}/{count}")
    result = get_books_data()
    i = 2
    for page_url in search_pages:
        print(f"page: {i}/{count}")
        result.extend(get_books_data(page_url))
        i = i + 1
    return result


def parse(pars, extend_books_to_db=None):
    prepare_pars(pars)
    result = []
    i = 1
    for url in urls:
        print(f"url: {url}")
        books_data = get_books_from_url(url)
        if extend_books_to_db is not None:
            extend_books_to_db(books_data, i)
        result.extend(books_data)
        i = i + 1
    return result


def parse_additional_data(books_data):
    login_url = "https://rutracker.org/forum/login.php"
    driver.get(login_url)
    login_to_site(login_url)
    result = []
    try:
        lll = len(books_data)
        i = 1
        for book_data in books_data:
            # if i < 599:
            #     print(f"{i}/{lll}")
            #     i = i + 1
            #     continue
            book_id = book_data['id']
            url = book_data['url']
            book_page_id = book_data['book_page_id']
            driver.get(url)
            soup = bs(driver.page_source, features="html.parser")
            post_body = soup.find("div", {"class": "post_body"})
            data = {
                "id": book_id
            }

            if post_body is None:
                result.append({
                    "id": book_id,
                    "no_book": "true"
                })
                i = i + 1
                continue
            else:
                data["no_book"] = "false"

            img = post_body.find("img", {"class": "postImg"})
            if img is not None:

                if "post-img-broken" in img.attrs['class']:
                    img_url = img.attrs['title']
                else:
                    img_url = img.attrs['src']
                data["img_url"] = img_url

            table = soup.find("div", {"class": "post_wrap"}).find("table")
            if table is not None:
                a = table.find("a", {"data-topic_id": book_page_id})
                if a is not None:
                    magnet_link = a.attrs['href']
                    tor_size = table.find("span", {"id": "tor-size-humn"}).text
                    data["magnet_link"] = magnet_link
                    data["tor_size"] = tor_size

            result.append(data)
            print(f"{i}/{lll}")
            i = i + 1
    except Exception:
        print("пум")

    return result


def get_books_from_url(url):
    driver.get(url)
    login_to_site(url)
    return get_all_books_data()


def prepare_pars(pars=None):
    if pars is not None:
        if pars['urls'] is not None:
            urls.extend(pars['urls'])
        else:
            urls.append("https://rutracker.org/forum/tracker.php?f=2387")
        if pars['exclude_ids'] is not None:
            db_book_ids.extend(pars['exclude_ids'])


def flatten(t):
    return [item for sublist in t for item in sublist]


def first_login():
    login_url = "https://rutracker.org/forum/login.php"
    driver.get(login_url)
    login_to_site(login_url)


def get_book_data_value_by_par_name(book_url, par_name):
    driver.get(book_url)
    soup = bs(driver.page_source, features="html.parser")
    root_item = soup.find('div', attrs={'class': 'post_body'})
    if par_name == "description":
        return get_book_data_by_type(root_item, matches[par_name])
    return None
