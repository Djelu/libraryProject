import pickle
import time
from pathlib import Path

import bs4.element
from fake_useragent import UserAgent
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
from selenium.common.exceptions import InvalidCookieDomainException

from multiprocessing import Pool

# from proxy_auth_data import login as proxy_login, password as proxy_password, server as proxy_server
from proxy_auth_data import proxy
from rutracker_auth_data import login as tracker_login, password as tracker_password



service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={UserAgent().chrome}")
options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--headless")

auth_url = "https://rutracker.org/forum/login.php"
url = "https://rutracker.org/forum/tracker.php?f=2387"
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
drivers = []

def login_to_site(driver, url):
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
        auth(driver)
        pickle.dump(driver.get_cookies(), open(cookie_file_name, "wb"))
    if driver.current_url != url:
        driver.get(url)
    time.sleep(1)


def auth(driver):
    driver.get(auth_url)
    login_input = driver.find_element(By.XPATH, "//input[@name='login_username'][not(@id='top-login-uname')]")
    login_input.clear()
    login_input.send_keys(tracker_login)

    password_input = driver.find_element(By.XPATH, "//input[@name='login_password'][not(@id='top-login-pwd')]")
    password_input.clear()
    password_input.send_keys(tracker_password)
    password_input.send_keys(Keys.ENTER)
    time.sleep(1)


def get_search_pages(driver):
    elems = driver.find_elements(By.CLASS_NAME, "pg")
    result = remove_duplicates(list(map(lambda el: [el.text, el.get_attribute("href")], elems)))
    result["1"] = driver.current_url
    # result.append(driver.current_url)
    return result


def remove_duplicates(data):
    result = {}
    for el in data:
        if result.get(el[0]) is not None:
            result[el[0]] = el[1]
    return result


def open_new_tab(driver, page_url):
    driver.execute_script(f"window.open('{page_url}');")


def close_tab(driver):
    if len(driver.window_handles) > 1:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])


def get_rows_data(driver):
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
                for j in range(i+1, len(items)-1):
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


def get_book_data(driver, row_data):
    time.sleep(1)
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


def get_books_data(driver):
    result = []
    # driver.get(page_url)
    # for row_data in get_rows_data(driver):
    row_data = get_rows_data(driver)[0]
    driver.get(row_data["href"])
    result.append(get_book_data(driver, row_data))
    close_tab(driver)
    return result


def get_books_data_in_new_window(page_num):
    print(f"start {page_num}")
    # options = webdriver.ChromeOptions()
    # options.add_argument(f"user-agent={UserAgent().chrome}")
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")
    curr_proxy = proxy[page_num-1]
    proxy_options = {
        "proxy": {
            "https": f"http://{curr_proxy['login']}:{curr_proxy['password']}@{curr_proxy['server']}"
        }
    }
    driver = webdriver.Chrome(
        service=service,
        seleniumwire_options=proxy_options,
        options=options
    )
    drivers.append(driver)
    try:
        driver.get(auth_url)
        login_to_site(driver, url)
        if page_num != 1:
            elem = driver.find_element(By.XPATH, f"//a[contains(@class, 'pg')][text()='{page_num}']")
            driver.get(elem.get_attribute("href"))
        return get_books_data(driver)
    except Exception as ex:
        print(f"{page_num}:\n{ex}")
    finally:
        driver.close()
        driver.quit()
        print(f"finish {page_num}")
    return []


def get_all_books_data(driver):
    result = []
    # pages = get_search_pages(driver)
    pages = list(range(1, 3))
    pool = Pool(processes=len(pages))#len(pages)
    res = pool.map(get_books_data_in_new_window, pages)
    result = flatten(res)
    # for page_url in pages:
    #     result.extend(get_books_data_in_new_window(page_url))
    return result


def flatten(t):
    return [item for sublist in t for item in sublist]


def main():
    curr_proxy = proxy[0]
    proxy_options = {
        "proxy": {
            "https": f"http://{curr_proxy['login']}:{curr_proxy['password']}@{curr_proxy['server']}"
        }
    }
    main_driver = webdriver.Chrome(
        service=service,
        seleniumwire_options=proxy_options,
        options=options
    )
    drivers.append(main_driver)
    try:
        # open_new_tab(url)
        main_driver.get(url)
        login_to_site(main_driver, url)
        get_all_books_data(main_driver)
    except Exception as ex:
        print(ex)
    finally:
        main_driver.close()
        main_driver.quit()


if __name__ == '__main__':
    main()
