import requests

from scraper_cfg import KUFAR_URL, ONLINER_URL
from db_utils import item_register, items_checker, get_all_users


def scrape_all(url):
    """
    Get response from given url and return it as a JSON object.

    :param url: target url
    :return: JSON object
    """
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        print('Request to API error: ', e)
        return []

    try:
        nb_response = r.json()
        return nb_response
    except Exception as e:
        print('JSON convertion error: ', e)
        return []


def to_send_preparation():
    """
    Prepare items data for sending to Telegram.

    :return: generator object with items data for each user
    """
    kufar_response = scrape_all(KUFAR_URL)
    onliner_response = scrape_all(ONLINER_URL)

    kufar_ads = link_extractor(kufar_response, 'k')
    onliner_ads = link_extractor(onliner_response, 'o')
    ads = kufar_ads + onliner_ads
    print(ads)

    items = items_checker()
    users = get_all_users()

    if users:
        for user in users:
            for add in ads:
                if add and add not in items:
                    item_register(url=add)

                    yield user, add


def link_extractor(response: dict, flag: str) -> list:
    """
    Parsing item urls from API response for given url.
    :param flag: o = onliner, k = kufar
    :param response: kufar API response

    :return: list of item urls
    """
    item_list = []

    if flag == 'k':
        try:
            ads = response['ads']
            for ad in ads:
                link = ad['ad_link']
                item_list.append(link)

        except Exception as e:
            print('link_extractor: ', e)
    else:
        try:
            ads = response['apartments']
            for ad in ads:
                link = ad['url']
                item_list.append(link)

        except Exception as e:
            print('link_extractor: ', e)

    return item_list
