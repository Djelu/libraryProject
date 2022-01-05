import json

from services import database_service as db_service
from services import rutracker_books_parser as parser


def main():
    try:
        book_page_ids = db_service.get_book_page_ids()
        books_data = parser.parse(book_page_ids)
        with open('./books_data/data.json', 'w+', encoding='utf-8') as f:
            json.dump(books_data, f)
            res = db_service.json_to_db(books_data)
            if isinstance(res, Exception):
                print("json_to_db exception:\n" + str(res))
        res = db_service.execute_query("select * from library.rutracker_books;")
        if isinstance(res, Exception):
            print("execute_query exception:\n" + str(res))
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()
