import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from hand import router

load_dotenv()
TOKEN = getenv('TOKEN')

dp = Dispatcher()

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_router(router=router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Бот успешно запущен и готов к работе!")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
