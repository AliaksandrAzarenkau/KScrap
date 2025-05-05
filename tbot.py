import asyncio

from telebot.async_telebot import AsyncTeleBot, asyncio_filters
from telebot.asyncio_storage import StateMemoryStorage
from telebot.states import State, StatesGroup

from cfg import TG_TOKEN
from db_utils import db_user_create, db_items_create, user_register

from scraper import to_send_preparation

API_TOKEN = TG_TOKEN

state_storage = StateMemoryStorage()
bot = AsyncTeleBot(TG_TOKEN, state_storage=state_storage)


class MyStates(StatesGroup):
    choice = State()
    end = State()


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    """
    Start and register user(or ignore)
    """
    await bot.reply_to(message, 'Ok', parse_mode='Markdown')
    user_info = message.from_user.id
    user_register(user_info)


@bot.message_handler(func=lambda message: True)
async def bot_send_items(message: str, user_info: int):
    """
    Send item to user
    """
    await bot.send_message(text=message, chat_id=user_info)


def on_startup():  # Create tables on startup if not exists
    db_user_create()
    db_items_create()


async def scraping_task():
    """
    Tasks for scraping data
    """
    ads = to_send_preparation()
    for ad in ads:
        await bot_send_items(user_info=ad[0], message=ad[1])


async def periodic():
    while True:
        await scraping_task()
        await asyncio.sleep(30)


async def main():
    bot.add_custom_filter(asyncio_filters.StateFilter(bot))  # Need to States

    from telebot.states.asyncio.middleware import StateMiddleware  # Need to States
    bot.setup_middleware(StateMiddleware(bot))

    await asyncio.gather(bot.infinity_polling(), periodic())


if __name__ == '__main__':
    on_startup()
    asyncio.run(main())
