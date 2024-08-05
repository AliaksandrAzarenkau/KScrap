import sqlite3

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()


def db_user_create():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    tg_id INTEGER,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    UNIQUE(id, tg_id)
    )
    ''')

    connection.commit()
    connection.close()


def db_notebooks_create():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notebook (
    id INTEGER PRIMARY KEY,
    nb_url TEXT NOT NULL,
    UNIQUE(id, nb_url)
    )
    ''')

    connection.commit()
    connection.close()


def user_register(user_data: dict) -> None:
    cursor.execute('SELECT tg_id FROM users WHERE tg_id = ?', (user_data['user_id'],))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            'INSERT OR IGNORE INTO Users (tg_id, first_name, last_name) VALUES (?, ?, ?)',
            (
                user_data['user_id'],
                user_data['user_first_name'],
                user_data['user_last_name']))

    connection.commit()


def nb_items_register(items: list) -> list:
    current_list = []
    new_items_list = []

    cursor.execute('SELECT * FROM notebook', )
    item_list = cursor.fetchall()

    for _ in item_list:
        current_list.append(_[1])

    for item in items:
        if item not in current_list:
            cursor.execute('INSERT OR IGNORE INTO notebook (nb_url) VALUES (?)',
                           (item,))
            new_items_list.append(item)

    connection.commit()

    return new_items_list
