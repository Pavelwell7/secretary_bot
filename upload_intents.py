import json
import os

from environs import Env
from google.cloud import dialogflow_v2 as dialogflow


def create_intent(project_id: str, display_name: str, training_phrases_parts: list[str],
                  message_texts: list[str]) -> None:
    intents_client = dialogflow.IntentsClient()
    parent = f"projects/{project_id}/agent"
    training_phrases = []
    for phrase_text in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=phrase_text)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    response = intents_client.create_intent(parent=parent, intent=intent)

    print(f"Интент '{response.display_name}' успешно загружен и создан!")


def main() -> None:
    env = Env()
    env.read_env()

    project_id = env("DIALOGFLOW_PROJECT_ID")
    credentials_path = env("GOOGLE_APPLICATION_CREDENTIALS")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    with open("questions.json", "r", encoding="utf-8") as file:
        intents_data = json.load(file)

    for intent_name, data in intents_data.items():
        create_intent(
            project_id=project_id,
            display_name=intent_name,
            training_phrases_parts=data["questions"],
            message_texts=[data["answer"]]
        )

if __name__ == "__main__":
    main()