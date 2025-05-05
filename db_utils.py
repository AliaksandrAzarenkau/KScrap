import sqlite3


connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()


def db_user_create():
    """
    Creates the users table
    """
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY,
    tg_id INTEGER,
    UNIQUE(id, tg_id)
    )
    ''')

    connection.commit()


def db_items_create():
    """
    Creates the items(url to items) table
    """
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS item (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    UNIQUE(id)
    )
    ''')

    connection.commit()


def user_register(user_data: int) -> None:
    """
    Users register or ignore existing user
    """
    cursor.execute('SELECT tg_id FROM user WHERE tg_id = ?', (user_data,))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            'INSERT OR IGNORE INTO user (tg_id) VALUES (?)',
            (user_data,))

    connection.commit()


def item_register(url: str) -> None:
    """
    Register or ignore existing item
    :param url: item url
    :param tg_id: telegram id
    :return: None
    """
    cursor.execute(
        'INSERT OR IGNORE INTO item (url) VALUES (?)',
        (url,))

    connection.commit()


def items_checker() -> list:
    """
    :return: user's items(all urls)
    """
    items_url_list = []

    cursor.execute('SELECT (url) FROM item')
    items = cursor.fetchall()

    try:
        for _ in items:
            items_url_list.append(_[0])
    except Exception as e:
        print('items_checker: ', e)

    return items_url_list


def get_all_users() -> list:
    """
    :return: all users
    """
    users_list = []

    cursor.execute('SELECT (tg_id) FROM user')
    items = cursor.fetchall()

    try:
        for _ in items:
            users_list.append(_[0])
    except Exception as e:
        print('items_checker: ', e)

    return users_list
