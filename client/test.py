import os
import time

from datetime import datetime

from openai import OpenAI
from openai.types.chat import ChatCompletion

from chat.api import API_KEY, MODEL, URL
from chat.history import History
from chat.story import SYSTEM_PROMPT, SYSTEM_PROMPT_END, SUSPECTS_DATA
from logs import log_info, log_warn

QUESTIONS = [
    "Who are you?",
    "What were you doing tonight?",
    "Did you see anything suspicious?",
    "Do you know the victim?",
    "Where were you when it happened?",
    "Did you notice anyone acting strange?",
    "What do you know about the victim?",
    "Who else was here?",
    "What happened exactly?",
    "Why were you at the bar?",
    "Did you talk to the victim?",
    "What time did you arrive?",
    "Did you notice anything unusual before the body was found?",
    "Do you know any of the other customers?",
    "What were you drinking?",
    "Did you hear or see anything odd?",
    "What's your relationship to the victim?",
    "Did anyone argue with the victim?",
    "What did you do after the body was found?",
    "Did you notice the man in the long coat?",
]


def run(client: OpenAI) -> None:
    history = History(True, True)

    suspect = 0

    for suspect_data in SUSPECTS_DATA:
        log_info(f"new chat with suspect {suspect + 1}")

        suspect += 1

        description = suspect_data["description"]
        events = "\n".join(f"- {event}" for event in suspect_data["events"])

        prompt = f"{SYSTEM_PROMPT}\n{description}\nEvents you have noticed:\n{events}\n{SYSTEM_PROMPT_END}"

        conversation = [{"role": "system", "content": prompt}]

        history.log_new_chat(suspect)

        for question in QUESTIONS:
            conversation.append({"role": "user", "content": question})

            history.log_chat_user(question)

            response_text = ""

            start_time = time.time()

            latency = None

            try:
                stream = client.chat.completions.create(
                    model=MODEL,
                    messages=conversation,
                    stream=True
                    ) # ty: ignore[no-matching-overload]

                log_info("llm response awaiting stream")

                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content

                        if latency is None:
                            latency = time.time() - start_time

                        response_text += token
                
                log_info("last payload received from llm")

            except Exception as e:
                log_warn(f"llm response failed: {e}")
                log_warn("skipping question")
                continue

            total_time = time.time() - start_time

            history.log_chat_response(response_text)
            history.log_response_time(latency, total_time)

            conversation.append({"role": "assistant", "content": response_text})


def main() -> None:
    client = OpenAI(base_url=URL, api_key=API_KEY)

    for _ in range(3):
        run(client)


if __name__ == "__main__":
    main()
