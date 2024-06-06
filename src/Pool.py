from src.public.ProjectGlobals import *
from src.public.ProjectConstants import *

from src.public.Base import Base
from .Tile import Tile

import pygame

import random


@SingletonDecorator
class Pool(Base):

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.rect = pygame.Rect(POOL_X, POOL_Y, POOL_W, POOL_H)

        self.tiles = list()

        self.__init_pool()

    def draw(self, background=None):
        img_plusplayer_button = pygame.image.load(Path(IMG_DIR, "pool.png"))
        img_plusplayer_button = pygame.transform.scale(img_plusplayer_button, (self.rect.w, self.rect.h))
        self.screen.blit(img_plusplayer_button, img_plusplayer_button.get_rect(topleft=(self.rect.x, self.rect.y)))

        text_surface = self.font.render(str(self.get_tile_count()), True, RED, background)
        text_rect = text_surface.get_rect(x=self.rect.x + 42, y=self.rect.y + self.rect.h - 80)
        self.screen.blit(text_surface, text_rect)

    def __init_pool(self):
        for tile in self.game.tiles.tiles:
            self.add_tile(tile)

    def is_tile_in(self, tile: Tile):
        return tile in self.tiles

    def get_tile_count(self) -> int:
        return len(self.tiles)

    def add_tile(self, tile: Tile):
        self.tiles.append(tile)
        tile.move_to_POOL_only()

        # # Debug
        # print("Return to pool:", tile)

    def play_tile(self, tile: Tile):
        # discard
        if tile in self.tiles:
            self.tiles.remove(tile)

    def shuffle_tiles(self):
        random.shuffle(self.tiles)

    def __draw_tiles(self, cnt: int) -> list[Tile]:
        self.shuffle_tiles()
        tiles = random.sample(self.tiles, k=min(cnt, self.get_tile_count()))
        for tile in tiles:
            self.play_tile(tile)

        # # Debug
        # print("Draw:", tiles)

        return tiles

    def deal__draw_14_tiles(self) -> list[Tile]:
        return self.__draw_tiles(14)

    def player__draw_2_tiles_from_pool(self) -> list[Tile]:
        # When you draw a tile from the pool, you choose two tiles,
        # choose one to add to your rack, and return the other one to the pool
        return self.__draw_tiles(2)

    def penalty__draw_1_tiles(self) -> list[Tile]:
        return self.__draw_tiles(1)
