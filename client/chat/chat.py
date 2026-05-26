import queue
import threading
import time

from abc import abstractmethod

from openai import OpenAI

from .api import *
from .history import History
from .story import SYSTEM_PROMPT, SYSTEM_PROMPT_END, TOTAL_SUSPECTS, SUSPECTS_DATA, REQUIRED_EVIDENCE
from logs import log_info, log_warn


class NPC:
    def __init__(self, use_llm):
        self._counter = 0
        self._history = History(use_llm)
        self._response = ""

    def get_clue_counter(self) -> int:
        return self._counter


class ChatLLM(NPC):
    def __init__(self):
        super().__init__(True)
        self.__client = OpenAI(base_url=URL, api_key=API_KEY)
        self.__conversation = []

        for suspect_data in SUSPECTS_DATA:
            description = suspect_data["description"]
            events = "\n".join(f"- {event}" for event in suspect_data["events"])

            prompt = f"{SYSTEM_PROMPT}\n{description}\nEvents you have noticed:\n{events}\n{SYSTEM_PROMPT_END}"

            self.__conversation.append([{"role": "system", "content": prompt}])

    def new_chat(self, suspect: int) -> None:
        self.__suspect = suspect
        self.__busy = False
        self.__queue_text = queue.Queue()
        self.__placeholder = False
        self._response = ""

        self._history.log_new_chat(suspect)

        log_info(f"new chat with suspect {suspect}")

    def send_question(self, text: str) -> None:
        if self.__busy:
            return

        log_info("preparing message for llm")
        self._counter += 1
        self._history.log_chat_user(text)

        self.__busy = True

        self.__conversation[self.__suspect - 1].append({"role": "user", "content": text})

        args = (self.__client, self.__conversation[self.__suspect - 1], self.__queue_text)
        thread = threading.Thread(target=get_llm_response, args=args)

        self.__latency = None
        self.__total_time = None
        self.__start_time = time.time()

        thread.start()

        self._response = "..."
        self.__placeholder = True
        log_info(f"requested llm response to: {text}")

    def get_response(self) -> str:
        while not self.__queue_text.empty():
            event = self.__queue_text.get_nowait()
            payload = event.get("payload")

            match event.get("type"):
                case "token":
                    if self.__latency is None:
                        self.__latency = time.time() - self.__start_time

                    if self.__placeholder:
                        self._response = payload
                        self.__placeholder = False
                    else:
                        self._response += payload

                case "error":
                    self.__conversation[self.__suspect - 1].pop()

                case "done":
                    total_time = time.time() - self.__start_time

                    log_info("last payload received from llm")

                    self._history.log_chat_response(self._response)
                    self._history.log_response_time(self.__latency, total_time)

                    last_response = {"role": "assistant", "content": self._response}
                    self.__conversation[self.__suspect - 1].append(last_response)
                    self.__busy = False

        return self._response

    def not_busy(self) -> bool:
        if self.__busy:
            log_warn("attempting to leave chat while waiting for response")
            return False

        log_info("leaving chat")
        return True

def get_llm_response(client: OpenAI, conversation: list, queue_text: queue.Queue) -> None:
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=conversation,
            stream=True
        )

        log_info("llm response awaiting stream")

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                queue_text.put_nowait({"type": "token", "payload": token})

    except Exception as e:
        log_warn(f"llm response failed: {e}")
        queue_text.put_nowait({"type": "error", "payload": None})

    finally:
        queue_text.put_nowait({"type": "done", "payload": None})


class ChatScript(NPC):
    type Questions = list[tuple[int, None | tuple[int, int], str]]
    type Events = list[str]

    def __init__(self):
        NPC.__init__(self, False)
        self.__questions_asked = []

    def new_chat(self, suspect: int) -> None:
        self.__suspect = suspect
        self.__questions: self.Questions = SUSPECTS_DATA[suspect - 1]["questions"] # ty: ignore[invalid-assignment]
        self.__events: self.Events = SUSPECTS_DATA[suspect - 1]["events"] # ty: ignore[invalid-assignment]
        self._response = ""

        self._history.log_new_chat(suspect)

        log_info(f"questioning suspect {suspect}")

    def get_questions(self) -> tuple[list[int], list[str]]:
        available_ids = []
        available_questions = []

        for id, required, text in self.__questions:
            if required is None:
                available_ids.append(id)
                available_questions.append(text)
            elif required in self.__questions_asked:
                available_ids.append(id)
                available_questions.append(text)

        return available_ids, available_questions

    def ask_question(self, question_id: int) -> None:
        self.__questions_asked.append((self.__suspect, question_id))

        self._response = self.__events[question_id - 1]

        question = self.__questions[question_id - 1]

        self._counter += 1
        self._history.log_chat_user(question[2])
        self._history.log_chat_response(self._response)

        self._counter = 0

        for evidence in REQUIRED_EVIDENCE:
            if evidence in self.__questions_asked:
                self._counter += 1

    def get_response(self) -> str:
        return self._response
