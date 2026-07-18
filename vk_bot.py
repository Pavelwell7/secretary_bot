import logging
import os
import random

from environs import Env
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from google.cloud import dialogflow_v2 as dialogflow



def ask_dialogflow(project_id: str, session_id: str, text: str, lang_code: str = "ru") -> str:
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=lang_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    fulfillment_text = response.query_result.fulfillment_text
    is_fallback = response.query_result.intent.is_fallback

    return fulfillment_text, is_fallback

def main() -> None:
    env = Env()
    env.read_env()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    vk_token = env("VK_BOT_TOKEN")
    group_id = env("VK_GROUP_ID")
    project_id = env("DIALOGFLOW_PROJECT_ID")
    credentials_path = env("GOOGLE_APPLICATION_CREDENTIALS")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id)

    logging.info("бот для ВКонтакте запущен!")

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
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

if __name__ == "__main__":
    main()