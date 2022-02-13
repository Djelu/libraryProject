import json

from services import database_service as db_service
from services import rutracker_books_parser as parser


def main():
    try:
        # parser.parse({
        #     "exclude_ids": db_service.get_book_page_ids(),
        #     "urls": get_urls_by_years(1990, 2022)
        # }, extend_books_to_db)

        # res = db_service.execute_query("select id, book_page_id, url from library.rutracker_books;")
        # result = parser.parse_additional_data(res)
        extend_additional_data_to_db([])
        # if isinstance(res, Exception):
        #     print("execute_query exception:\n" + str(res))
    except Exception as ex:
        print(ex)


def extend_books_to_db(books_data, index):
    save_to_tmp_file_and_get(f'./books_data/data{index}.json', books_data)
    if len(books_data) == 0:
        return print("done!")
    res = db_service.json_to_db(books_data)
    if isinstance(res, Exception):
        print("json_to_db exception:\n" + str(res))
    else:
        print("done!")


def extend_additional_data_to_db(books_data):
    books_data = save_to_tmp_file_and_get(f'./books_data/add_data.json', books_data)
    res = db_service.additional_data_to_db(books_data)
    if isinstance(res, Exception):
        print("additional_data_to_db exception:\n" + str(res))
    else:
        print("done!")


def save_to_tmp_file_and_get(tmp_file, books_data):
    # with open(tmp_file, 'w', encoding='utf-8') as f:
    #     json.dump(books_data, f)
    with open(tmp_file, 'r', encoding='utf-8') as f:
        books_data = json.load(f)
    return books_data


def get_urls_by_years(year_from, year_to):
    return list(map(lambda year: f'https://rutracker.org/forum/tracker.php?f=2387&nm={year}', range(year_from, year_to)))


if __name__ == '__main__':
    main()
