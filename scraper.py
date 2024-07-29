import requests
import aiohttp
import asyncio

from scraper_cfg import NB_URL

nb_item_links = []
r = requests.get(NB_URL)
nb_response = r.json()

for ads in nb_response['ads']:
    nb_item_links.append(ads['ad_link'])


# async def task_collector(params: list) -> None:
#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         for _ in params:
#             tasks.append(asyncio.create_task(get_item_info(session, _)))
#         await asyncio.gather(*tasks)
#
#
# async def get_item_info(session, params: str) -> None:
#     async with session.get() as resp:
#
#         resp_data = await resp.json()
#
#         # Парсинг конечных категорий при их наличии
#         if resp_data['data']['filters'][0].get('items'):
#             target_dict = resp_data['data']['filters'][0]['items']
#
#             for _ in target_dict:
#                 result = [_['id'], _['name'], 99]
#                 if filters.get(params[2]):
#                     filters[params[2]] += result
#                 else:
#                     filters[params[2]] = result
#
# asincio.run(task_collector(nb_item_links))
