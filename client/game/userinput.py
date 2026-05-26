import pygame


class UserInput:
    def __init__(self):
        self.reset()

    def process_key_event(self, event: pygame.event.Event) -> None:
        match event.key:
            case pygame.K_ESCAPE:
                self.escape_key = True

            case pygame.K_RETURN:
                self.return_key = True

            case pygame.K_UP:
                self.up_key = True

            case pygame.K_DOWN:
                self.down_key = True

            case pygame.K_F1:
                self.f1_key = True

            case pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
                else:
                    self.backspace_key = True

            case pygame.K_TAB:
                self.tab_key = True

            case _:
                self.text += event.unicode

    def reset(self) -> None:
        self.escape_key = False
        self.return_key = False
        self.up_key = False
        self.down_key = False
        self.f1_key = False
        self.backspace_key = False
        self.tab_key = False
        self.text = ""
