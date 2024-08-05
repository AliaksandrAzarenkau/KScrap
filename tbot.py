import asyncio

from telebot.async_telebot import AsyncTeleBot

from scraper import scrape_all, create_nb_item_links
from db_utils import user_register
from cfg import TG_TOKEN
from scraper_cfg import NB_URL

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


async def scraping_task():
    resp = await scrape_all(NB_URL)
    to_send = await create_nb_item_links(resp)

    for _ in to_send:
        await bot_send_items_to_me(_)


async def periodic():
    while True:
        await scraping_task()
        await asyncio.sleep(60)


async def main():
    await asyncio.gather(bot.infinity_polling(), periodic())

if __name__ == '__main__':
    asyncio.run(main())
