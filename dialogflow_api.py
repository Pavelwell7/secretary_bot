from google.cloud import dialogflow_v2 as dialogflow


def ask_dialogflow(project_id: str, session_id: str, text: str, lang_code: str = "ru"):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=lang_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    fulfillment_text = response.query_result.fulfillment_text
    is_fallback = response.query_result.intent.is_fallback

    return fulfillment_text, is_fallback
