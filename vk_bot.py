import random
import logging

from environs import Env
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


def main() -> None:
    env = Env()
    env.read_env()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    vk_token = env("VK_BOT_TOKEN")
    group_id = env.int("VK_GROUP_ID")

    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            text = event.obj.message['text']

            if not text:
                continue

            logging.info(f"Пришло сообщение от ID {user_id}: {text}")
            vk.messages.send(
                user_id=user_id,
                message=text,
                random_id=random.randint(1, 1000)
            )


if __name__ == "__main__":
    main()