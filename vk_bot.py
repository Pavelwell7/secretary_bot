import logging
import os
import random
import time
import traceback

import requests
import vk_api
from environs import Env
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

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


def main() -> None:
    env = Env()
    env.read_env()

    vk_token = env("VK_BOT_TOKEN")
    group_id = env("VK_GROUP_ID")
    project_id = env("DIALOGFLOW_PROJECT_ID")
    credentials_path = env("GOOGLE_APPLICATION_CREDENTIALS")
    tg_bot_token = env("TG_BOT_TOKEN")
    admin_chat_id = env("ADMIN_CHAT_ID")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.addHandler(TelegramLogsHandler(tg_bot_token, admin_chat_id))

    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id)

    logger.info("VK-бот запущен")

    while True:
        try:
            for event in longpoll.listen():
                if event.type != VkBotEventType.MESSAGE_NEW:
                    continue

                user_id = event.obj.message['from_id']
                text = event.obj.message['text']
                if not text:
                    continue

                logging.info(f"Запрос от vk-{user_id}: {text}")
                ai_response, is_fallback = ask_dialogflow(
                    project_id=project_id,
                    session_id=f"vk-{user_id}",
                    text=text
                )

                if is_fallback:
                    continue

                vk.messages.send(
                    user_id=user_id,
                    message=ai_response,
                    random_id=random.randint(1, 1000000)
                )
        except Exception:
            logger.error(f"VK-бот упал с ошибкой:\n{traceback.format_exc()}")
            time.sleep(5)


if __name__ == "__main__":
    main()