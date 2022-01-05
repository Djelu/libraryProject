import pymysql

from configs.db_auth_data import host, port, user, password, db_name


def execute_query(query):
    try:
        if query[len(query) - 1] != ';':
            query = query + ';'

        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        # connection = psycopg2.connect(
        #     host=host,
        #     port=5432,
        #     user=user,
        #     password=password,
        #     database=db_name
        # )

        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        finally:
            connection.close()
    except Exception as ex:
        return ex


def json_to_db(data):
    book = data[0]
    print(book)
