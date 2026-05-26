from types import ModuleType

import pygame

from .assets import load_font
from .background import Background
from .prison import Prison
from .people import Investigator, Suspect
from color import *


class Screen:
    def __init__(self, pygame_instance: ModuleType):
        self.__screen = pygame_instance.display.set_mode((1280, 720))
        self.__clock = pygame_instance.time.Clock()
        self.__update_scale(self.__screen.get_size())
        self.__update_font()

        self.__background = Background(self.__screen.get_size(), "bar.png", COLOR_BACKGROUND)
        self.__investigator = Investigator(self.__scale, "investigator.png", COLOR_INVESTIGATOR)

        self.__suspects = []
        self.__suspects.append(Suspect(self.__scale, "suspect-1.png", COLOR_SUSPECT_1))
        self.__suspects.append(Suspect(self.__scale, "suspect-2.png", COLOR_SUSPECT_2))
        self.__suspects.append(Suspect(self.__scale, "suspect-3.png", COLOR_SUSPECT_3))
        self.__suspects.append(Suspect(self.__scale, "suspect-4.png", COLOR_SUSPECT_4))
        self.__suspects.append(Suspect(self.__scale, "suspect-5.png", COLOR_SUSPECT_5))
        self.__suspects.append(Suspect(self.__scale, "suspect-6.png", COLOR_SUSPECT_6))

        self.__prison = Prison(self.__scale, "prison.png")

    def __update_scale(self, screen_size: tuple) -> None:
        width_ratio = screen_size[0] / 16
        height_ratio = screen_size[1] / 9

        self.__scale = int(width_ratio if width_ratio < height_ratio else height_ratio)

    def __update_font(self) -> None:
        self.__font = load_font("bedstead.regular.otf", int(self.__scale / 4))
        self.__char_size = self.__font.render(" ", True, COLOR_TEXT).get_size()

    def resize(self, screen_size: tuple) -> None:
        self.__update_scale(screen_size)
        self.__update_font()

        self.__background.resize(screen_size)
        self.__investigator.resize(self.__scale)

        for suspect in self.__suspects:
            suspect.resize(self.__scale)

        self.__prison.resize(self.__scale)

    def begin_drawing(self, title_text: str) -> None:
        self.__background.draw(self.__screen)
        self.__investigator.draw(self.__screen, self.__scale)

        self.draw_title_text(title_text)

    def end_drawing(self, pygame_instance: ModuleType) -> None:
        pygame_instance.display.flip()
        self.__clock.tick(60)

    def draw_title_text(self, title_text: str) -> None:
        size = (self.__screen.get_size()[0], self.__scale)
        title_background = pygame.Surface(size, flags=pygame.SRCALPHA)
        title_background.fill((0, 0, 0, 128))
        self.__screen.blit(title_background, (0, 0))

        title_surface = self.__font.render(title_text, True, COLOR_TEXT)

        position = title_surface.get_rect(center=self.__screen.get_rect().center)
        position.y = int(self.__scale / 2 - title_surface.get_size()[1] / 2)
        self.__screen.blit(title_surface, position)

    def draw_suspect(self, selected_option: int) -> None:
        self.__suspects[selected_option - 1].draw(self.__screen, self.__scale)

    def draw_prison(self) -> None:
        self.__prison.draw(self.__screen, self.__scale)

    def draw_response_text(self, text: str) -> None:
        position = (self.__scale, self.__scale * 1.25)

        self.draw_multiline_text(text, position)

    def draw_user_text(self, text: str) -> None:
        position = (self.__scale * 3.75, self.__scale * 5.25)

        self.draw_multiline_text(text, position)

    def draw_multiline_text(self, text: str, position: tuple) -> None:
        max_width = self.__scale * 11.25

        text_split = text.split(" ")

        lines = []

        index_from = 0
        index_to = 0

        while True:
            line = " ".join(text_split[index_from:index_to])

            if len(line) * self.__char_size[0] > max_width:
                if index_to - index_from == 1:
                    lines.append(" ".join(text_split[index_from:index_to]))
                else:
                    index_to -= 1
                    lines.append(" ".join(text_split[index_from:index_to]))

                index_from = index_to

            elif index_to >= len(text_split) + 1:
                lines.append(line)
                break

            else:
                index_to += 1

        surface_size = (max_width, len(lines) * self.__char_size[1])
        surface = pygame.Surface(surface_size, flags=pygame.SRCALPHA)

        for i in range(0, len(lines)):
            surface.blit(self.__font.render(lines[i], True, COLOR_TEXT), (0, i * self.__char_size[1]))

        self.__screen.blit(surface, position)

    def draw_options(self, options: list[str], selected: int) -> None:
        options_surface = []

        for option in options:
            options_surface.append(self.__font.render(option, True, COLOR_TEXT))

        option_width = self.__scale * 11.25
        option_height = self.__char_size[1]
        surface = pygame.Surface((option_width, option_height * len(options_surface)))
        surface.fill(COLOR_OPTION)

        selected_box = (0, (selected - 1) * option_height, option_width, option_height)
        pygame.draw.rect(surface, COLOR_SELECTED, selected_box)

        for i in range(0, len(options_surface)):
            option_rect = pygame.Rect(0, i * option_height, option_width, option_height)
            center = options_surface[i].get_rect(center=option_rect.center)
            center.x = self.__scale / 8
            surface.blit(options_surface[i], center)

        position = (self.__scale * 3.75, self.__scale * 7 - surface.get_size()[1] / 2)
        self.__screen.blit(surface, position)
