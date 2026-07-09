import asyncio
import logging

from environs import Env
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart



async def command_start_handler(message: types.Message) -> None:
    await message.answer(
        "Здоров!\n"
    )

async def echo_handler(message: types.Message) -> None:
    await message.answer(text=message.text)




async def main() -> None:
    env = Env()
    env.read_env()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    tg_bot_token = env("TG_BOT_TOKEN")
    bot = Bot(token=tg_bot_token)
    dp = Dispatcher()
    dp.message.register(command_start_handler, CommandStart())
    dp.message.register(echo_handler)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())