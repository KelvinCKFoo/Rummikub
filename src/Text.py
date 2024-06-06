from src.public.ProjectConstants import *

from src.public.Base import Base

import pygame

from typing import *


class Text(Base):
    def __init__(self, x, y, text="",
                 color: Optional[Tuple[int]] = BLACK,
                 background: Optional[Tuple[int]] = WHITE,
                 *args, **kwargs
                 ):
        super().__init__()

        self.x = x
        self.y = y
        self.text = str(text)
        self.color = color
        self.background = background

    def draw(self, new_text: str = None,
             color: Optional[Tuple[int]] = None,
             background: Optional[Tuple[int]] = None,
             *args, **kwargs):
        if color is None:
            color = self.color
        if background is None:
            background = self.background

        # Render and draw the text
        if new_text is not None:
            self.text = str(new_text)

        text_surface = self.font.render(self.text, True, color, background)
        text_rect = text_surface.get_rect(topleft=(self.x, self.y))
        self.screen.blit(text_surface, text_rect)


class Text_PlayerInfo(Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, new_text: str = None,
             color: Optional[Tuple[int]] = None,
             background: Optional[Tuple[int]] = None,
             *args, **kwargs):

        # Render and draw the text
        if new_text is not None:
            self.text = str(new_text)

        if color is None:
            color = self.color
        if background is None:
            background = self.background

        text_surface = self.font.render(self.text, True, color, background)
        rect = pygame.Rect(MESSAGE_BOX_X, MESSAGE_BOX_Y, MESSAGE_BOX_W, MESSAGE_BOX_H)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
