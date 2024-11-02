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


def db_subscription_create():
    """
    Creates the subscriptions table
    """
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscription (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER,
    region INTEGER NOT NULL,
    decode_keywords TEXT NOT NULL,
    keywords TEXT NOT NULL,
    UNIQUE(id)
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
    telegram_id INTEGER,
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


def subscription_register(reg: str, dkw: str, kw: str, tg_id: int) -> None | str:
    """
    Register or ignore existing subscription
    :param reg: region
    :param dkw: keyword to search
    :param kw: keyword in URL_lang
    :param tg_id: telegram id
    :return: None
    """
    try:
        cursor.execute('SELECT (keywords) FROM subscription WHERE (telegram_id = ?)',
                       (tg_id,))
        subscription = cursor.fetchall()
        for _ in subscription:
            if kw in _:
                return 'Такая подписка уже активна'

        cursor.execute('INSERT OR IGNORE INTO subscription (telegram_id, region, decode_keywords, keywords) '
                       'VALUES (?, ?, ?, ?)',
                       (tg_id, reg, dkw, kw))

    except sqlite3.IntegrityError as e:
        print('subscription_register: ', e)

    connection.commit()


def item_register(url: str, tg_id: int) -> None:
    """
    Register or ignore existing item
    :param url: item url
    :param tg_id: telegram id
    :return: None
    """
    cursor.execute(
        'INSERT OR IGNORE INTO item (telegram_id, url) VALUES (?, ?)',
        (tg_id, url,))

    connection.commit()


def send_subscriptions_handler():
    """
    :return: Dictionary with subscriptions {user(telegram id): subscriptions}
    """
    subscription_dict = {}

    cursor.execute('SELECT tg_id FROM user')
    users = cursor.fetchall()

    for user in users:
        subscription_dict.update({user[0]: []})
        cursor.execute('SELECT * FROM subscription WHERE telegram_id = ?', (user[0],))
        subscriptions = cursor.fetchall()
        subscription_dict[user[0]] += subscriptions

    return subscription_dict


def items_checker(tg_id: int) -> list:
    """
    :return: user's items(all urls)
    """
    items_url_list = []

    cursor.execute('SELECT (url) FROM item WHERE (telegram_id = ?)',
                   (tg_id,))
    items = cursor.fetchall()

    try:
        for _ in items:
            items_url_list.append(_[0])
    except Exception as e:
        print('items_checker: ', e)

    return items_url_list


def get_subscriptions(tg_id: int) -> list:
    """
    :return: all user's subscriptions
    """
    try:
        cursor.execute('SELECT * FROM subscription WHERE (telegram_id = ?)',
                       (tg_id,))
        subscription = cursor.fetchall()

    except Exception as e:
        print('get_subscriptions: ', e)

    return subscription


def delete_subscription(subscription_id: int) -> None | str:
    """
    Delete subscription
    :return: None or exception
    """
    try:
        cursor.execute('DELETE FROM subscription WHERE (id = ?)',
                       (subscription_id,))
        connection.commit()
    except Exception as e:
        print('delete_subscription: ', e)
        return '504'
