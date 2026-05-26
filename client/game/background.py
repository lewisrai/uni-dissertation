import pygame

from .assets import load_image


class Background:
    def __init__(self, size: tuple, filename: str, color: pygame.Color, alpha=192):
        self.__img_original = load_image(filename)
        self.__color = color
        self.__alpha = alpha

        self.resize(size)

    def resize(self, size: tuple):
        new_size = size[1] if size[0] > size[1] else size[0]

        self.__background = pygame.Surface(size)
        self.__background.fill(self.__color)

        self.__img = pygame.transform.scale(self.__img_original, (new_size, new_size))
        center = self.__img.get_rect(center=self.__background.get_rect().center)
        self.__background.blit(self.__img, center)

        self.__overlay = pygame.Surface(size, flags=pygame.SRCALPHA)
        self.__overlay.fill((0, 0, 0, self.__alpha))
        self.__background.blit(self.__overlay, (0, 0))

    def draw(self, screen: pygame.Surface):
        screen.blit(self.__background, (0, 0))
