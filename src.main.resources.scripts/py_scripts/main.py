import json

from services import database_service as db_service
from services import rutracker_books_parser as parser


def main():
    try:
        parser.parse({
            "exclude_ids": db_service.get_book_page_ids(),
            "urls": get_urls_by_years(1990, 2022)
        }, extend_books_to_db)

        res = db_service.execute_query("select * from library.rutracker_books;")
        if isinstance(res, Exception):
            print("execute_query exception:\n" + str(res))
    except Exception as ex:
        print(ex)


def extend_books_to_db(books_data, index):
    tmp_file = f'books_data/data{index}.json'
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(books_data, f)
    with open(tmp_file, 'r', encoding='utf-8') as f:
        books_data = json.load(f)
        if len(books_data) == 0:
            return print("done!")
        res = db_service.json_to_db(books_data)
        if isinstance(res, Exception):
            print("json_to_db exception:\n" + str(res))
        else:
            print("done!")


def get_urls_by_years(year_from, year_to):
    return list(map(lambda year: f'https://rutracker.org/forum/tracker.php?f=2387&nm={year}', range(year_from, year_to)))


if __name__ == '__main__':
    main()
