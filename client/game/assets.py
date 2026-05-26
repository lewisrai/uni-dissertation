import os

import pygame

from logs import log_info


def load_font(filename: str, size: int) -> pygame.font.Font:
    path = os.path.join("assets", "font", filename)
    log_info(f"loading font at: {path}")

    return pygame.font.Font(path, size)


def load_image(filename: str) -> pygame.Surface:
    path = os.path.join("assets", "textures", filename)
    log_info(f"loading image at: {path}")

    return pygame.image.load(path).convert_alpha()
