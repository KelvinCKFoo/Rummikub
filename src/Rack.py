from src.public.ProjectGlobals import *
from src.public.ProjectConstants import *

from src.public.Base import Base
from .Tile import Tiles, Tile

import pygame

from typing import *
import copy


class Rack(Base):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.grids = []

        self.tiles = []
        self.rack_tiles_turn_begin = []
        self.list_of_lst_table_tiles_turn_begin = copy.copy(get_value("TABLE").get_all_lst_tiles_on_table())

    def reset(self):
        self.reset_tiles_turn_begin()
        self.save_tiles_to_turn_begin()

    def reset_tiles_turn_begin(self):
        # Reset rack tiles begin
        self.rack_tiles_turn_begin = []
        # Reset table tiles begin
        self.list_of_lst_table_tiles_turn_begin = copy.copy(get_value("TABLE").get_all_lst_tiles_on_table())

    def get_tile_count(self):
        return len(self.tiles)

    def is_in_tile(self, tile: Tile):
        return tile in self.tiles

    def add_tile(self, tile: Tile):
        self.tiles.append(tile)

    def play_tile(self, tile: Tile):
        if tile in self.tiles:
            self.tiles.remove(tile)

    def save_tiles_to_turn_begin(self):
        self.rack_tiles_turn_begin = copy.copy(self.tiles)
        self.list_of_lst_table_tiles_turn_begin = copy.copy(get_value("TABLE").get_all_lst_tiles_on_table())

    def restore_tiles_from_turn_begin(self):
        TABLE = get_value("TABLE")
        # For each tile on the rack at turn begin
        for tile in self.rack_tiles_turn_begin:
            # If the tile is on the table，put it back to rack
            if tile.get_center_area() == TABLE:
                self.add_tile(tile)
                TABLE.play_tile(tile)

    def update(self, events):
        pass

    def draw(self, *args, **kwargs):
        pass

    def relocate_tiles(self):
        tiles = []
        TILES = get_value("TILES")
        for grid in self.grids:
            if tile := TILES.has_tile(grid):
                tiles.append(tile)

        for tile, grid in zip(tiles, self.grids):
            tile.move(grid)

    def relocate_tiles_by_group(self):
        tiles = self.tiles
        valid_groups, remaining_tiles = Tiles.group_by_number(tiles)
        idx = 0
        for tile_group in valid_groups:
            for tile in tile_group:
                tile.move(self.grids[idx])
                idx += 1

            idx += 1

        for tile in remaining_tiles:
            tile.move(self.grids[idx])
            idx += 1

    def relocate_tiles_by_run(self):
        tiles = self.tiles
        valid_run, remaining_tiles = Tiles.group_by_run(tiles)
        idx = 0
        for tile_run in valid_run:
            for tile in tile_run:
                tile.move(self.grids[idx])
                idx += 1

            idx += 1

        for tile in remaining_tiles:
            tile.move(self.grids[idx])
            idx += 1

    def relocate_tiles_by_group_AI(self):
        tiles = self.tiles
        valid_group = []
        used_tiles = set()
        _, all_lst_tiles_on_table = Tiles.find_all_combinations(tiles)
        for lst in all_lst_tiles_on_table:
            if Tiles.is_a_group(lst):
                valid_group.append(lst)
                for tile in lst:
                    used_tiles.add(tile)

        remaining_tiles = list(set(tiles) - used_tiles)
        remaining_tiles.sort(key=Tile.sort_key_number_first)

        idx = 0
        for tile_run in valid_group:
            for tile in tile_run:
                tile.move(self.grids[idx])
                idx += 1

            idx += 1

        for tile in remaining_tiles:
            tile.move(self.grids[idx])
            idx += 1

    def relocate_tiles_by_run_AI(self):
        tiles = self.tiles
        valid_run = []
        used_tiles = set()
        _, all_lst_tiles_on_table = Tiles.find_all_combinations(tiles)
        for lst in all_lst_tiles_on_table:
            if Tiles.is_a_run(lst):
                valid_run.append(lst)
                for tile in lst:
                    used_tiles.add(tile)

        remaining_tiles = list(set(tiles) - used_tiles)
        remaining_tiles.sort(key=Tile.sort_key_color_first)

        idx = 0
        for tile_run in valid_run:
            for tile in tile_run:
                tile.move(self.grids[idx])
                idx += 1

            idx += 1

        for tile in remaining_tiles:
            tile.move(self.grids[idx])
            idx += 1

    def relocate_tiles_by_number_and_color(self):
        tiles = self.tiles
        tiles.sort(key=Tile.sort_key_number_first)
        for tile, grid in zip(tiles, self.grids):
            tile.move(grid)


class Rack_AI(Rack):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save_tiles_to_turn_begin(self):
        super().save_tiles_to_turn_begin()

    def restore_tiles_from_turn_begin(self):
        super().restore_tiles_from_turn_begin()

    def set_player(self, player, idx):
        self.player = player
        self.player_idx = idx

    def make_grids(self):
        p_id = self.player_idx
        # Make grids
        self.grids = []
        for i in range(MAX_TILE_NUMBER * len(TILE_COLOURS) * 2 + 2):
            x = RACK_AI_X[p_id] + (TILE_W + TILE_SPACING_W * 2) * (i % RACK_AI_COL_LIMIT[p_id])
            y = RACK_AI_Y[p_id] + (TILE_H + TILE_SPACING_W * 2) * (i // RACK_AI_COL_LIMIT[p_id])
            self.grids.append((x, y))

    def update(self, events):
        super().update(events)

    def draw(self, color=TRANSPARENT, *args, **kwargs):
        super().draw(*args, **kwargs)

        p_id = self.player_idx

        self.rect = pygame.Rect(RACK_AI_X[p_id], RACK_AI_Y[p_id], RACK_AI_W[p_id], RACK_AI_H[p_id])

        rect_surface = pygame.Surface((RACK_AI_W[p_id], RACK_AI_H[p_id]), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, color, self.rect)

        GAME = self.game
        PLAYER = GAME.current_player
        if PLAYER != self:
            return

    def add_tile(self, tile: Tile):
        super().add_tile(tile)

        # # Find the last available blank space
        # TILES = get_value("TILES")
        # for idx in range(len(self.grids) - 1, -1, -1):
        #     grid = self.grids[idx]
        #     if TILES.has_tile(grid):
        #         last_idx = idx
        #         break
        # else:
        #     last_idx = -1
        #
        # tile.move(self.grids[last_idx + 1])

        # Find the first available blank space
        TILES = get_value("TILES")
        for idx in range(len(self.grids)):
            grid = self.grids[idx]
            if not TILES.has_tile(grid):
                last_idx = idx
                break
        else:
            last_idx = -1

        tile.move(self.grids[last_idx])


@SingletonDecorator
class Rack_User(Rack):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The rack for tiles
        self.rect = pygame.Rect(RACK_USER_X, RACK_USER_Y, RACK_USER_W, RACK_USER_H)

        # Make grids
        self.grids = []
        for i in range(MAX_TILE_NUMBER * len(TILE_COLOURS) * 2 + 2):
            x = RACK_USER_X + (TILE_W + TILE_SPACING_W * 2) * (i % RACK_USER_COL_LIMIT)
            y = RACK_USER_Y + (TILE_H + TILE_SPACING_W * 2) * (i // RACK_USER_COL_LIMIT)
            self.grids.append((x, y))

    def update(self, events):
        super().update(events)

    def draw(self, color: Optional[tuple] = TRANSPARENT):
        rect_surface = pygame.Surface((RACK_USER_W, RACK_USER_H), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, color, self.rect)

    def fit_grid(self, x, y):
        for idx, grid in enumerate(self.grids):
            rect = pygame.Rect(
                *grid, TILE_W + TILE_SPACING_W, TILE_H + TILE_SPACING_W
            )
            # Inside the grid rect
            if rect.collidepoint(x, y):
                # Check grid occupied
                return rect.center
        return None

    def add_tile(self, tile: Tile):
        super().add_tile(tile)

        # Find the last available blank space
        TILES = get_value("TILES")
        for idx in range(len(self.grids) - 1, -1, -1):
            grid = self.grids[idx]
            if TILES.has_tile(grid):
                last_idx = idx
                break
        else:
            last_idx = -1

        # Rack can not be full!
        tile.move(self.grids[last_idx + 1])

    #     self.adjust_RACK_ROW_LIMIT()
    #
    # def adjust_RACK_ROW_LIMIT(self):
    #     n = self.get_tile_count()
    #     row = n // RACK_USER_COL_LIMIT
    #     if n % RACK_USER_COL_LIMIT == 0:
    #         row += 1
    #
    #     RACK_USER_ROW_LIMIT = row
    #     set_value("RACK_USER_ROW_LIMIT", RACK_USER_ROW_LIMIT)

    def save_tiles_to_turn_begin(self):
        super().save_tiles_to_turn_begin()

    def restore_tiles_from_turn_begin(self):
        super().restore_tiles_from_turn_begin()
