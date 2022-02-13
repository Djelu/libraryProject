import pymysql

from configs.db_auth_data import host, port, user, password, db_name


def exec_wrapper(execute, *args):
    try:
        if len(args) == 2:
            conn = args[0]
            args = args[1:]
        else:
            conn = create_conn()
        try:
            res = execute(conn, *args)
            conn.commit()
            return res
        finally:
            conn.close()
    except Exception as ex:
        return ex


def fix_query(query):
    query = add_semicolon(query.strip()).replace('\n', ' ')
    while '  ' in query:
        query = query.replace('  ', ' ')
    return query


def add_semicolon(query):
    if query[len(query) - 1] != ';':
        return query + ';'
    return query


def create_conn():
    return pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )


def exec_query(conn, query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        return result


def execute_query(query):
    return exec_wrapper(lambda c, q: exec_query(c, fix_query(q)), query)


def json_to_db(data):

    def get_values(book_data):
        book_page_id = book_data['url'].split("t=")[1]
        return f"""(
           default,
           '{book_page_id}',
           '{book_data['url']}', 
           '{book_data['row_name']}', 
           '{book_data['book_name']}', 
           '{book_data['year']}', 
           '{book_data['last_name']}', 
           '{book_data['fist_name']}', 
           '{book_data['executor']}', 
           '{book_data['cycle_name']}', 
           '{book_data['book_number']}', 
           '{book_data['genre']}', 
           '{book_data['edition_type']}', 
           '{book_data['category']}', 
           '{book_data['audio_codec']}', 
           '{book_data['bitrate']}', 
           '{book_data['bitrate_type']}', 
           '{book_data['sampling_frequency']}', 
           '{book_data['count_of_channels']}', 
           '{book_data['book_duration']}', 
           '{book_data['description']}'
        )"""

    values = map(get_values, data)
    query = "INSERT INTO library.rutracker_books VALUES " + ",".join(values)
    return execute_query(query)


def additional_data_to_db(data):

    def get_sql_value(book_data, key):
        if key in book_data:
            if key == "no_book":
                value = book_data[key]
            else:
                value = f"'{book_data[key]}'"
        else:
            value = "null"
        return value

    def get_values(book_data):
        return f"""
           {get_sql_value(book_data, 'id')}, 
           {get_sql_value(book_data, 'img_url')},
           {get_sql_value(book_data, 'magnet_link')},
           {get_sql_value(book_data, 'tor_size')},
           {get_sql_value(book_data, 'no_book')}
        """

    values = "),(".join(map(get_values, data))
    query = f"""INSERT INTO library.rutracker_books 
                    (id, img_url, magnet_link, tor_size, no_book) 
                VALUES  ({values})
                ON DUPLICATE KEY UPDATE 
                    img_url = VALUES(img_url),
                    magnet_link = VALUES(magnet_link),
                    tor_size = VALUES(tor_size),
                    no_book = VALUES(no_book);
            """
    return execute_query(query)


def get_book_page_ids():
    result = execute_query("SELECT book_page_id FROM library.rutracker_books ORDER BY book_page_id DESC;")
    return list(map(lambda it: it['book_page_id'], result))
