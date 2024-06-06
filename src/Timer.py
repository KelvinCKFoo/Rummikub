from src.public.ProjectConstants import *

from src.public.Base import Base

import pygame

from typing import *


class CountdownTimer(Base):
    def __init__(self, x, y, w, h,
                 default_time=TIME_LIMIT,
                 color: Optional[Tuple[int]] = WHITE,
                 background: Optional[Tuple[int]] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        #self.w = 100
        #self.h = 100
        #self.x = SCREEN_W - self.w * 1
        #self.y = 0
        self.rect = pygame.Rect(x, y, w, h)
        #self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.color = color
        self.background = background

        self.default_time: float = default_time
        self.remaining_time = default_time
        self.reset()

        self.font = pygame.font.SysFont('Arial', 35)

    def update(self, *args, **kwargs):
        self.update_current_time()
        self.remaining_time: float = max(0, self.end_time - self.current_time)

        if self.is_time_up():
            self.game.current_player.end_turn()

    def draw(self, color: Optional[Tuple[int]] = RED, background: Optional[Tuple[int]] = None,
             *args, **kwargs):
        if color is None:
            color = self.color
        if background is None:
            background = self.background

        img_plusplayer_button = pygame.image.load(Path(IMG_DIR, "countdown_timer.png"))

        img_plusplayer_button = pygame.transform.scale(img_plusplayer_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_plusplayer_button, img_plusplayer_button.get_rect(topleft=(self.rect.x, self.rect.y)))

        # Render and draw the text
        text_surface = self.font.render(self.get_remaining_time_str(), True, color, background)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

    def update_current_time(self):
        self.current_time: float = pygame.time.get_ticks() / 1000

    def reset(self):
        self.update_current_time()
        self.end_time: float = self.current_time + self.default_time

    def is_time_up(self):
        return self.remaining_time <= 0

    def get_remaining_time_str(self):
        return "%.0f" % self.remaining_time


class PlayerTimer:
    def __init__(self):
        self.elapsed_seconds = 0
        self.start_ticks = 0
        self.is_running = False

    def reset(self):
        self.elapsed_seconds = 0
        self.start_ticks = pygame.time.get_ticks()

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_ticks = pygame.time.get_ticks()
        else:
            self.reset()

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.update()

    def update(self):
        if self.is_running:
            current_ticks = pygame.time.get_ticks()
            self.elapsed_seconds = (current_ticks - self.start_ticks) / 1000.0

    def seconds_elapsed(self):
        self.update()
        return self.elapsed_seconds
