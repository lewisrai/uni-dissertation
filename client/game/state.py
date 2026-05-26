from enum import Enum


class GameState(Enum):
    INTRO = 1
    OPTIONS = 2
    CHALLENGE = 3
    ARREST = 4
    OUTRO = 5
    QUIT = 6
