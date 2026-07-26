import asyncio
import logging
import os
import time
import traceback

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from environs import Env

from dialogflow_api import ask_dialogflow


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot_token, chat_id):
        super().__init__()
        self.tg_bot_token = tg_bot_token
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        url = f"https://api.telegram.org/bot{self.tg_bot_token}/sendMessage"
        requests.post(url, data={"chat_id": self.chat_id, "text": log_entry}, timeout=10)


async def greet_user(message: types.Message) -> None:
    await message.answer("Здоров!\n")


async def answer_user_question(message: types.Message, project_id: str) -> None:
    if not message.text:
        await message.answer("Я умею обрабатывать только текстовые вопросы.")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    ai_response, is_fallback = await asyncio.to_thread(
        ask_dialogflow,
        project_id=project_id,
        session_id=message.from_user.id,
        text=message.text
    )
    await message.answer(text=ai_response)


async def main() -> None:
    env = Env()
    env.read_env()

    tg_bot_token = env("TG_BOT_TOKEN")
    project_id = env("DIALOGFLOW_PROJECT_ID")
    credentials_path = env("GOOGLE_APPLICATION_CREDENTIALS")
    admin_chat_id = env("ADMIN_CHAT_ID")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    bot = Bot(token=tg_bot_token)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.addHandler(TelegramLogsHandler(tg_bot_token, admin_chat_id))

    await bot.send_message(chat_id=admin_chat_id, text="Бот запущен")
    logger.info("Бот запущен")

    dp = Dispatcher()
    dp.message.register(greet_user, CommandStart())
    dp.message.register(answer_user_question)

    while True:
        try:
            await dp.start_polling(bot, project_id=project_id)
        except Exception:
            logger.error(f"Бот упал с ошибкой:\n{traceback.format_exc()}")
            time.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())