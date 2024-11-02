import requests
import urllib.parse
from langdetect import detect

from scraper_cfg import SEARCH_URL, SEARCH_URL_POSTFIX, REGION_DICT
from db_utils import subscription_register, item_register, send_subscriptions_handler, items_checker, get_subscriptions, delete_subscription


def scrape_all(url):
    """
    Get response from given url and return it as a JSON object.

    :param url: target url
    :return: JSON object
    """
    r = requests.get(url)

    try:
        nb_response = r.json()
        return nb_response
    except Exception as e:
        print(e)
        return []


def url_builder(region: int, to_search: str) -> str:
    """
    Build url based on region code and keywords to search.

    :param region: region code
    :param to_search: keywords to search
    :return: url string
    """
    if region == 0:
        url = SEARCH_URL + f'query={to_search}' + SEARCH_URL_POSTFIX
    else:
        url = SEARCH_URL + f'query={to_search}&rgn={region}' + SEARCH_URL_POSTFIX

    return url


def encode_to_url(search_request: str) -> str:
    """
    Encode lang to URL lang.

    :param search_request: keywords to search
    :return: encoded string
    """
    encoded_string = urllib.parse.quote(search_request)
    return encoded_string


def language_detection(text: str) -> str:
    """
    Detect language of text. If isn't English, decode it to URL lang.

    :param text: text to detect
    :return: result text(decoded or as is)
    """
    detected_language = detect(text)

    if detected_language != 'en':
        result = encode_to_url(text)
        return result

    return text


async def subscription_handler(request_text: str, telegram_id: int) -> str:
    """
    Handle subscription requests. Check subscription register. Handle subscription exceptions.

    :param request_text:
    :param telegram_id:
    :return: string with handling tesult
    """
    region = 0
    if request_text.count(',') != 1:
        return 'Неправильный формат ввода'

    subscription_request = request_text.split(', ')

    for k, v in REGION_DICT.items():
        if subscription_request[0].lower() == k:
            region = v

    encoded_keyword = subscription_request[1].lower()
    to_search = language_detection(encoded_keyword)

    url = url_builder(region, to_search)

    scraped_data = scrape_all(url)

    # Обработка исключений поиска и проверка наличия подписки
    try:
        # ads = scraped_data['ads']
        check_subscription = subscription_register(region, encoded_keyword, to_search, telegram_id)
        if check_subscription == 'Такая подписка уже активна':
            return check_subscription
        result = 'Рассылка активирована'
        return result
    except KeyError as e:
        print(f'KeyError: {e}')
        result = 'Поиск не дал результата. Уточни параметры или проверь по сайту.'
        return result


def to_send_preparation():
    """
    Prepare items data for sending to Telegram.

    :return: generator object with items data for each user
    """
    subscriptions = send_subscriptions_handler()
    for k, v in subscriptions.items():
        sent_items_link_list = items_checker(k)
        for _ in v:
            url = url_builder(_[2], _[3])
            item_url_list = link_extractor(url)

            for link in item_url_list:
                if link not in sent_items_link_list:
                    item_register(tg_id=k, url=link)

                    yield [k, link]


def link_extractor(url: str) -> list:
    """
    Parsing item urls from API response for given url.
    :param url: target url

    :return: list of item urls
    """
    item_list = []
    response = scrape_all(url)
    try:
        ads = response['ads']
        for ad in ads:
            link = ad['ad_link']
            item_list.append(link)

        return item_list

    except Exception as e:
        print('link_extractor: ', e)


def subscriptions_list_handler(telegram_id: int) -> str | None:
    """
    Get list of subscriptions for given telegram id.
    :param telegram_id:

    :return: None or list of subscriptions
    """
    count = 1
    current_subscriptions_list = []
    current_subscriptions = get_subscriptions(telegram_id)

    if current_subscriptions:
        for _ in current_subscriptions:
            for k, v in REGION_DICT.items():
                if _[2] == v:
                    sub_item = [k, _[3]]
                    current_subscriptions_list.append(sub_item)
        result = ''
        for subscription in current_subscriptions_list:
            result += str(count) + ') ' + subscription[0] + ', ' + subscription[1] + '\n'
            count += 1
        return result

    return None


def subscription_del(telegram_id: int, subscription_number: int) -> str:
    """
    Delete given subscription.

    :param telegram_id:
    :param subscription_number: number of the subscription chosen by user
    :return: string with result of deleting subscription
    """
    current_subscriptions = get_subscriptions(telegram_id)
    try:
        to_del = current_subscriptions[subscription_number - 1]
    except IndexError:
        return 'Неверный формат ввода.\nЗапусти команду заново.'

    result = delete_subscription(to_del[0])

    if result:
        return 'Что-то пошло не так'

    return 'Удалена'
