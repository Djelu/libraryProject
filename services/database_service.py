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
            execute(conn, *args)
            conn.commit()
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
    data = data[:1]

    def get_values(book_data):
        page_id = book_data['url'].split("t=")[1]
        return f"""(
           default,
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
           '{book_data['description']}',
           '{book_data['url']}', 
           '{page_id}'
        )"""

    values = map(get_values, data)
    query = "INSERT INTO library.rutracker_books VALUES " + ",".join(values)
    execute_query(query)
