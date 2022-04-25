import json
import numpy
import asyncio
import aiohttp
from multiprocessing import Pool


from services import database_service as db_service
from services import rutracker_books_parser_v3 as rutracker
from configs.db_auth_data import table_name


url = 'https://rutracker.org/forum/tracker.php?f=2387'
view_topic_url = 'https://rutracker.org/forum/viewtopic.php'


def main():
    try:
        # parser.parse({
        #     "exclude_ids": db_service.get_book_page_ids(),
        #     "urls": get_urls_by_years(1990, 2022)
        # }, extend_books_to_db)

        # res = db_service.execute_query("select id, book_page_id, url from library.rutracker_books;")
        # result = parser.parse_additional_data(res)
        # extend_additional_data_to_db([])
        # if isinstance(res, Exception):
        #     print("execute_query exception:\n" + str(res))


        # result = foo()
        # while not result:
        #     result = foo()

        def get_ids():
            return list(map(
                lambda data: data['book_page_id'],
                db_service.execute_query(f"""
                    SELECT book_page_id
                    FROM rutracker_books;
                """)
            ))
        parser = rutracker.Parser(get_ids())
        asyncio.run(parser.run())
        iii = 3
    except Exception as ex:
        print(ex)


# def foo():
#     try:
#         update_data("description")
#         return True
#     except Exception as ex:
#         print(ex)
#         return False


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
    return list(map(lambda year: f'{url}&nm={year}', range(year_from, year_to)))


# def update_data(par_name):
#     def get_empty_value_rows():
#         return db_service.execute_query(f"""
#             SELECT id, book_page_id
#             FROM {table_name}
#             WHERE {par_name} = '';
#         """)
#     if par_name == "description":
#         rows = get_empty_value_rows()
#         print(f"all rows: {len(rows)}")
#         i = 1
#         queries = []
#         parser.first_login()
#         for row in rows:
#             book_page_url = f"{view_topic_url}?t={row['book_page_id']}"
#             value = parser.get_book_data_value_by_par_name(book_page_url, f"{par_name}")
#             if value is not None and str.strip(value) != "":
#                 query = db_service.get_update_book_data_query(row['id'], f"{par_name}", f"'{value}'")
#                 queries.append(str.strip(query))
#             else:
#                 i = i
#             print(f"row i={i} finished")
#             i = i + 1
#             if i == 100:
#                 break
#         db_service.execute_queries(queries)
#
#     return None
#

if __name__ == '__main__':
    main()
