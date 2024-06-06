from src.public.ProjectGlobals import *
from src.public.ProjectConstants import *

from src.public.Base import Base

import pygame

from typing import *


class ScoreBoard(Base):
    def __init__(self,
                 x, y, w, h,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.img = pygame.image.load(Path(IMG_DIR, "score_board.png"))
        self.img = pygame.transform.scale(self.img, (SCREEN_W, SCREEN_H))

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.rect = pygame.Rect(self.x, self.y - 160, self.w, self.h)
        self.rect_winner = pygame.Rect(self.x, self.y - 120, self.w, self.h)
        self.rect_winner_score = pygame.Rect(self.x, self.y - 80, self.w, self.h)

        self.rect_commiserations = pygame.Rect(self.x, self.y + 0, self.w, self.h)
        self.rect_loser = pygame.Rect(self.x, self.y + 40, self.w, self.h)
        self.rect_loser_score = pygame.Rect(self.x, self.y + 80, self.w, self.h)

    def update(self, events, *args, **kwargs):

        for event in events:
            pass

    def draw(self, *args, **kwargs):
        self.screen.blit(self.img, self.img.get_rect(topleft=(0, 0)))

        GAME = self.game
        round_winner_idx = GAME.round_winner_idx
        if round_winner_idx == -1:
            return

        self.winner = GAME.players_list[round_winner_idx]
        self.losers = []
        for player in GAME.players_list:
            if player != self.winner:
                self.losers.append(player)

        self.winner.score = -sum([player.score for player in self.losers])

        # Sort Losers
        self.losers.sort(key=lambda x: -x.score)

        text_surface_winner = self.font.render("Congratulations Winner", True, RED)
        text_rect_winner = text_surface_winner.get_rect(center=self.rect.center)
        self.screen.blit(text_surface_winner, text_rect_winner)

        text_surface_winner = self.font.render(str(self.winner), True, BLACK)
        text_rect_winner = text_surface_winner.get_rect(center=self.rect_winner.center)
        self.screen.blit(text_surface_winner, text_rect_winner)

        text_surface_winner_score = self.font.render(str(self.winner.score), True, BLACK)
        text_rect_winner_score = text_surface_winner_score.get_rect(center=self.rect_winner_score.center)
        self.screen.blit(text_surface_winner_score, text_rect_winner_score)

        text_surface_commiserations = self.font.render("Commiserations Losers:", True, YELLOW)
        text_rect_commiserations = text_surface_commiserations.get_rect(center=self.rect_commiserations.center)
        self.screen.blit(text_surface_commiserations, text_rect_commiserations)
        for idx, loser in enumerate(self.losers):
            text_surface_loser = self.font.render(str(loser), True, BLACK)
            text_rect_loser = text_surface_loser.get_rect(
                centerx=self.rect_loser.centerx, y=self.rect_loser.y + idx * 80)
            self.screen.blit(text_surface_loser, text_rect_loser)

            text_surface_loser_score = self.font.render(str(loser.score), True, BLACK)
            text_rect_loser_score = text_surface_loser_score.get_rect(
                centerx=self.rect_loser_score.centerx, y=self.rect_loser_score.y + idx * 80)
            self.screen.blit(text_surface_loser_score, text_rect_loser_score)
