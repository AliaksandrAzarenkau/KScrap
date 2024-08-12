import asyncio

from telebot.async_telebot import AsyncTeleBot

from scraper import scrape_all, create_my_nb_item_links, create_horse_tv_item_links, create_coffee_item_links
from db_utils import user_register, db_user_create, db_my_notebooks_create, db_horse_tv_create, db_my_coffee_create
from cfg import TG_TOKEN
from scraper_cfg import MY_NB_URL, HORSE_TV_URL, NIVONA_COFFEE_URL, MELITTA_COFFEE_URL

API_TOKEN = TG_TOKEN

bot = AsyncTeleBot(TG_TOKEN)


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.reply_to(message, 'хуярт')
    user_info = {
        'user_id': message.from_user.id,
        'user_first_name': message.from_user.first_name,
        'user_last_name': message.from_user.last_name}
    user_register(user_info)


async def bot_send_items_to_me(item: str):
    await bot.send_message(770325923, item)


async def bot_send_items_to_horse(item: str):
    await bot.send_message(772495588, item)


def on_startup():
    db_user_create()
    db_my_notebooks_create()
    db_my_coffee_create()
    db_horse_tv_create()


async def scraping_task():
    resp = await scrape_all(MY_NB_URL)
    to_send_for_me = await create_my_nb_item_links(resp)

    resp = await scrape_all(HORSE_TV_URL)
    to_send_for_horse = await create_horse_tv_item_links(resp)

    resp = await scrape_all(NIVONA_COFFEE_URL)
    to_send_about_nivona = await create_coffee_item_links(resp)
    resp = await scrape_all(MELITTA_COFFEE_URL)
    to_send_about_melitta = await create_coffee_item_links(resp)

    for _ in to_send_for_me:
        await bot_send_items_to_me(_)

    for _ in to_send_about_nivona:
        await bot_send_items_to_me(_)
    for _ in to_send_about_melitta:
        await bot_send_items_to_me(_)

    for _ in to_send_for_horse:
        await bot_send_items_to_horse(_)


async def periodic():
    while True:
        await scraping_task()
        await asyncio.sleep(60)


async def main():
    await asyncio.gather(bot.infinity_polling(), periodic())


if __name__ == '__main__':
    on_startup()
    asyncio.run(main())
