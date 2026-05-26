import os

from datetime import datetime


class History:
    def __init__(self, use_llm: bool, test=False):
        logs_dir = os.path.join(os.getcwd(), "logs")

        os.makedirs(logs_dir, exist_ok=True)

        self.__use_llm_str = "llm" if use_llm else "script"

        test_text = "_test" if test else ""

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(logs_dir, f"{timestamp}_{self.__use_llm_str}{test_text}.log")

        self.__file = open(filename, "w")

    def __del__(self):
        self.__file.close()

    def log_new_chat(self, suspect: int) -> None:
        self.__file.write(f"[suspect] {suspect}\n")
        self.__file.flush()

    def log_chat_user(self, text: str) -> None:
        self.__file.write(f"[user] {text}\n")
        self.__file.flush()

    def log_chat_response(self, text: str) -> None:
        self.__file.write(f"[{self.__use_llm_str}] {text}\n")
        self.__file.flush()

    def log_response_time(self, latency_s: None | float, total_time_s: float) -> None:
        if latency_s is None:
            latency_ms = -1
        else:
            latency_ms = int(latency_s * 1000)

        total_time_ms = int(total_time_s * 1000)

        self.__file.write(f"[timer] latency: {latency_ms}ms, finished: {total_time_ms}ms\n")
        self.__file.flush()
