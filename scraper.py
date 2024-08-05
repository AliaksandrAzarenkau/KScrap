import requests

from db_utils import nb_items_register

nb_item_links = []


async def scrape_all(url):
    r = requests.get(url)
    nb_response = r.json()

    return nb_response


async def create_nb_item_links(response) -> list:
    for ads in response['ads']:
        nb_item_links.append(ads['ad_link'])

    new_items = nb_items_register(nb_item_links)

    return new_items

