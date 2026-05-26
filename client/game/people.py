from abc import abstractmethod

import pygame

from .assets import load_image


class Avatar:
    def __init__(self, scale: int, filename: str, color: pygame.Color):
        self._img_original = load_image(filename)
        self._color = color

        self.resize(scale)

    def resize(self, scale: int) -> None:
        square = scale * 2.5
        border = scale / 10

        interior_size = (square - 2 * border, square - 2 * border)

        self._img = pygame.Surface((square, square))
        self._img.fill(self._color)
        self._img_resized = pygame.transform.scale(self._img_original, interior_size)
        self._img.blit(self._img_resized, (border, border))

    @abstractmethod
    def draw(self, screen: pygame.Surface, scale: int) -> None:
        pass


class Investigator(Avatar):
    def draw(self, screen: pygame.Surface, scale: int) -> None:
        screen.blit(self._img, (scale, scale * 5.75))


class Suspect(Avatar):
    def draw(self, screen: pygame.Surface, scale: int) -> None:
        screen.blit(self._img, (scale * 12.5, scale * 1.75))
