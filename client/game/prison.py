import pygame

from .assets import load_image


class Prison:
    def __init__(self, scale: int, filename: str):
        self.__img_original = load_image(filename)

        self.resize(scale)

    def resize(self, scale: int) -> None:
        size = (scale * 2.5, scale * 2.5)

        self.__img = pygame.transform.scale(self.__img_original, size)

    def draw(self, screen: pygame.Surface, scale: int) -> None:
        screen.blit(self.__img, (scale * 12.5, scale * 1.75))

