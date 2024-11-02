import asyncio

from telebot.async_telebot import AsyncTeleBot, asyncio_filters, types
from telebot.asyncio_storage import StateMemoryStorage
from telebot.states import State, StatesGroup
from telebot.states.asyncio.context import StateContext
from telebot.types import ReplyParameters

from cfg import TG_TOKEN
from db_utils import db_user_create, db_subscription_create, db_items_create, user_register
from scraper import subscription_handler, to_send_preparation, subscriptions_list_handler, subscription_del

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
    await bot.reply_to(message,
                       '*Формат запроса поиска: "город, ключевое слово(фраза)".*\nОбязательно через одну '
                       'запятую после города\n*пример:* ***брест, гладильная доска*** или ***беларусь, '
                       'блоки газосиликатные*** (на регистр пофиг)\n \n Доступные регионы: Областные центры, Беларусь\n'
                       '\nДоступные команды: /start, /list, /del\n'
                       'start - запуск, он же help\n list - список активных подписок \n del - удаление подписки',
                       parse_mode='Markdown')
    user_info = message.from_user.id
    user_register(user_info)


@bot.message_handler(commands=['list'])
async def get_subscription_list(message):
    """
    Add subscription if not exist
    """
    user_info = message.from_user.id
    current_subscriptions = subscriptions_list_handler(user_info)

    if current_subscriptions:
        await bot.reply_to(message, current_subscriptions)

    else:
        await bot.reply_to(message, 'Нет активных подписок')


@bot.message_handler(commands=['del'])
async def delete_subscription_handler(message: types.Message, state: StateContext):
    """
    Delete subscription(start point of dialog chain
    """
    await state.set(MyStates.choice)

    user_info = message.from_user.id
    current_subscriptions = subscriptions_list_handler(user_info)

    if current_subscriptions:
        text = '\n Отправь номер подписки чтобы удалить (тупо цыфра)'
        await bot.send_message(
            user_info,
            current_subscriptions + text,
            reply_parameters=ReplyParameters(message_id=message.message_id))
    else:
        await bot.reply_to(message, 'Нет активных подписок')


@bot.message_handler(state=MyStates.choice)
async def delete_subscription(message: types.Message, state: StateContext):
    """
    Result of deleting subscription
    """
    text = message.text
    result = ''

    try:
        choice = int(text)
        result = subscription_del(message.from_user.id, choice)
    except ValueError as e:
        print('Delete error: ', e)

    await bot.send_message(
        message.from_user.id,
        result,
        reply_parameters=ReplyParameters(message_id=message.message_id))
    await state.delete()


@bot.message_handler(func=lambda message: True)
async def add_subscription(message):
    """
    add subscription
    """
    user_info = message.from_user.id
    message_text = message.text

    result = await subscription_handler(message_text, user_info)
    await bot.reply_to(message, result)


@bot.message_handler(func=lambda message: True)
async def bot_send_items(message: str, user_info: int):
    """
    Send item to user
    """
    await bot.send_message(text=message, chat_id=user_info)


def on_startup(): # Create tables on startup if not exists
    db_user_create()
    db_subscription_create()
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
        await asyncio.sleep(60)


async def main():
    bot.add_custom_filter(asyncio_filters.StateFilter(bot))  # Need to States

    from telebot.states.asyncio.middleware import StateMiddleware  # Need to States
    bot.setup_middleware(StateMiddleware(bot))

    await asyncio.gather(bot.infinity_polling(), periodic())


if __name__ == '__main__':
    on_startup()
    asyncio.run(main())
