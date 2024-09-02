import requests

from db_utils import my_nb_items_register, horse_tv_items_register, coffee_items_register

nb_item_links = []
horse_tv_item_links = []
coffee_item_links = []


async def scrape_all(url):
    r = requests.get(url)

    try:
        nb_response = r.json()
        return nb_response
    except Exception as e:
        print(e)
        return []


async def create_my_nb_item_links(response) -> list:
    for ads in response['ads']:
        nb_item_links.append(ads['ad_link'])

    new_items = my_nb_items_register(nb_item_links)

    return new_items


async def create_horse_tv_item_links(response) -> list:
    for ads in response['ads']:
        horse_tv_item_links.append(ads['ad_link'])

    new_items = horse_tv_items_register(horse_tv_item_links)

    return new_items


async def create_coffee_item_links(response) -> list:
    for ads in response['ads']:
        coffee_item_links.append(ads['ad_link'])

    new_items = coffee_items_register(coffee_item_links)

    return new_items
