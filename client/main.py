import pygame
import sys

from chat.chat import ChatLLM, ChatScript
from chat.story import TOTAL_SUSPECTS, SUSPECT_OPTIONS, INTRO_TEXT, get_outro_text
from game.screen import Screen
from game.state import GameState
from game.userinput import UserInput
from logs import log_info


def main() -> None:
    log_info("initialising")

    pygame.init()

    log_info("pygame init successfully")

    screen = Screen(pygame)

    log_info("screen init successfully")

    chat_LLM = ChatLLM()
    user_text = ""
    chat_script = ChatScript()
    selected_question = 1

    use_llm = False

    log_info("npc init successfully")

    user_input = UserInput()

    selected_suspect = 1

    game_state = GameState.INTRO
    previous_game_state = None

    log_info("finished initialising")

    while game_state != GameState.QUIT:
        user_input.reset()

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    log_info("game quit")

                    game_state = GameState.QUIT

                case pygame.VIDEORESIZE:
                    log_info("window resized")

                    screen.resize((event.w, event.h))

                case pygame.KEYDOWN:
                    log_info("key pressed: " + pygame.key.name(event.key))

                    user_input.process_key_event(event)

        if previous_game_state != game_state:
            log_info(f"game state: {game_state}")

            previous_game_state = game_state

        if user_input.f1_key and game_state != GameState.CHALLENGE:
            use_llm = not use_llm

        match game_state:
            case GameState.INTRO:
                if user_input.return_key:
                    game_state = GameState.OPTIONS

                screen.begin_drawing("INTRO")
                screen.draw_user_text(INTRO_TEXT)
                screen.end_drawing(pygame)

            case GameState.OPTIONS:
                if user_input.return_key:
                    if selected_suspect == TOTAL_SUSPECTS + 1:
                        selected_suspect = 1
                        game_state = GameState.ARREST
                    else:
                        chat_LLM.new_chat(selected_suspect)
                        user_text = ""
                        chat_script.new_chat(selected_suspect)
                        selected_question = 1
                        game_state = GameState.CHALLENGE

                if user_input.up_key:
                    selected_suspect -= 1 if selected_suspect != 1 else 0
                if user_input.down_key:
                    selected_suspect += 1 if selected_suspect != TOTAL_SUSPECTS + 1 else 0

                screen.begin_drawing("SUSPECTS")
                if selected_suspect == 7:
                    screen.draw_prison()
                else:
                    screen.draw_suspect(selected_suspect)
                screen.draw_options(SUSPECT_OPTIONS, selected_suspect)
                screen.end_drawing(pygame)

            case GameState.CHALLENGE if use_llm:
                if user_input.escape_key and chat_LLM.not_busy():
                    game_state = GameState.OPTIONS
                if user_input.backspace_key and len(user_text) > 0:
                    user_text = user_text[:-1]
                if user_input.tab_key:
                    user_text = ""

                user_text += user_input.text

                if user_input.return_key:
                    chat_LLM.send_question(user_text)

                response_text = chat_LLM.get_response()

                screen.begin_drawing("ASK QUESTIONS")
                screen.draw_suspect(selected_suspect)
                screen.draw_response_text(response_text)
                screen.draw_user_text(user_text)
                screen.end_drawing(pygame)
            case GameState.CHALLENGE:
                if user_input.escape_key:
                    game_state = GameState.OPTIONS

                ids, questions = chat_script.get_questions()

                if user_input.up_key:
                    selected_question -= 1 if selected_question != 1 else 0
                if user_input.down_key:
                    selected_question += 1 if selected_question != len(questions) else 0

                if user_input.return_key:
                    chat_script.ask_question(ids[selected_question - 1])

                response_text = chat_script.get_response()

                screen.begin_drawing("ASK QUESTIONS")
                screen.draw_suspect(selected_suspect)
                screen.draw_response_text(response_text)
                screen.draw_options(questions, selected_question)
                screen.end_drawing(pygame)

            case GameState.ARREST:
                if user_input.escape_key:
                    selected_suspect = 1
                    game_state = GameState.OPTIONS

                if user_input.up_key:
                    selected_suspect -= 1 if selected_suspect != 1 else 0
                if user_input.down_key:
                    selected_suspect += 1 if selected_suspect != TOTAL_SUSPECTS else 0

                if user_input.return_key:
                    clue_counter = chat_LLM.get_clue_counter() + chat_script.get_clue_counter()
                    outro_text = get_outro_text(selected_suspect, clue_counter)
                    game_state = GameState.OUTRO

                screen.begin_drawing("ARREST")
                screen.draw_suspect(selected_suspect)
                screen.draw_prison()
                screen.draw_options(SUSPECT_OPTIONS[:-1], selected_suspect)
                screen.end_drawing(pygame)

            case GameState.OUTRO:
                screen.begin_drawing("OUTRO")
                screen.draw_suspect(selected_suspect)
                screen.draw_prison()
                screen.draw_user_text(outro_text)
                screen.end_drawing(pygame)

    pygame.quit()


if __name__ == "__main__":
    main()
