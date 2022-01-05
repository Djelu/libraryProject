import json

from services import database_service as db_service


def main():
    try:
        # books_data = parser.parse()
        # with open('./books_data/data.json', 'w', encoding='utf-8') as f:
        #     json.dump(books_data, f)

        with open('./books_data/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            db_service.json_to_db(data)

        result = db_service.execute_query("select * from rutracker_books;")
        if isinstance(result, Exception):
            print("execute_query exception:\n" + str(result))
        else:
            print(result)

    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()
