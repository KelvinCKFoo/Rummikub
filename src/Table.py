from src.public.ProjectConstants import *
from src.public.ProjectGlobals import *

from src.public.Base import Base
from .Tile import Tiles, Tile

import pygame


@SingletonDecorator
class Table(Base):

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.rect = pygame.Rect(TABLE_X, TABLE_Y, TABLE_W, TABLE_H)

        self.tiles = []

        # Make grids (top left)
        self.grids: list[tuple] = []
        for i in range(TABLE_ROW_LIMIT * TABLE_COL_LIMIT):
            x = TABLE_X + (TILE_W + TILE_SPACING_W * 2) * (i % TABLE_COL_LIMIT)
            y = TABLE_Y + (TILE_H + TILE_SPACING_H * 2) * (i // TABLE_COL_LIMIT)

            x = int(x)
            y = int(y)

            self.grids.append((x, y))

    def is_tile_in(self, tile: Tile) -> bool:
        return tile in self.tiles

    def add_tile(self, tile: Tile):
        self.tiles.append(tile)

    def play_tile(self, tile: Tile):
        if tile in self.tiles:
            self.tiles.remove(tile)

    def find_consecutive_places(self, n: int):
        TILES = get_value("TILES")
        for i in range(TABLE_ROW_LIMIT):
            count = 0
            for j in range(TABLE_COL_LIMIT):
                idx = i * TABLE_COL_LIMIT + j
                grid = self.grids[idx]
                if TILES.has_tile(grid):
                    count = 0
                else:
                    count += 1
                    if count == n + 2:
                        idx = i * TABLE_COL_LIMIT + j - n
                        if j - n == 1:
                            idx -= 1
                        return idx

        return None

    def place_tiles(self, lst_tiles: list[Tile]):
        n = len(lst_tiles)
        idx = self.find_consecutive_places(n)
        if idx is not None:
            for tile in lst_tiles:
                grid = self.grids[idx]
                self.add_tile(tile)
                tile.move(grid)
                idx += 1

        else:
            # TODO 重新排列TABLE
            print("Table没有足够的位置放置这么多牌")

    def get_tile_count(self) -> int:
        return len(self.tiles)

    def draw(self, color=TRANSPARENT):
        rect_surface = pygame.Surface((TABLE_W, TABLE_H), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, color, self.rect)

        for tile in self.tiles:
            tile.setFold(False)

        # Vertical grid
        for i in range(1, TABLE_ROW_LIMIT):
            start_x = TABLE_X
            start_y = TABLE_Y + (TILE_SPACING_H * 2 + TILE_H) * i + 0
            end_x = TABLE_X + TABLE_W
            end_y = TABLE_Y + (TILE_SPACING_H * 2 + TILE_H) * i + 0

            pygame.draw.line(
                self.screen, WHITE,
                (start_x, start_y),
                (end_x, end_y),
            )

        # Horizontal grid
        for i in range(1, TABLE_COL_LIMIT):
            start_x = TABLE_X + (TILE_SPACING_W * 2 + TILE_W) * i + 0
            start_y = TABLE_Y
            end_x = TABLE_X + (TILE_SPACING_W * 2 + TILE_W) * i + 0
            end_y = TABLE_Y + TABLE_H

            pygame.draw.line(
                self.screen, WHITE,
                (start_x, start_y),
                (end_x, end_y),
            )

    def fit_grid(self, x, y):
        for idx, grid in enumerate(self.grids):
            rect = pygame.Rect(
                *grid, TILE_W + TILE_SPACING_W * 2, TILE_H + TILE_SPACING_H * 2
            )
            # Inside the grid rect
            if rect.collidepoint(x, y):
                # Check grid occupied
                return rect.center
        return None

    def get_all_lst_tiles_on_table(self):
        TILES = get_value("TILES")
        lst = []
        for row_idx in range(TABLE_ROW_LIMIT):
            cur_lst = []
            for col_idx in range(TABLE_COL_LIMIT):
                idx = row_idx * TABLE_COL_LIMIT + col_idx
                grid = self.grids[idx]
                # Check if there is a tile in this grid
                if tile := TILES.has_tile(grid):
                    cur_lst.append(tile)
                # Get consecutive tiles
                elif cur_lst:
                    if len(cur_lst) >= 1:
                        lst.append(cur_lst)
                    cur_lst = []

            if len(cur_lst) >= 1:
                lst.append(cur_lst)

        return lst

    def check_table_validity(self):
        lst_of_lst_tiles = self.get_all_lst_tiles_on_table()
        # for lst in lst_of_lst_tiles:
        #     if Tiles.is_a_run(lst):
        #         print("run")
        #     if Tiles.is_a_group(lst):
        #         print("group")
        return all(Tiles.is_a_run(lst) or Tiles.is_a_group(lst) for lst in lst_of_lst_tiles), lst_of_lst_tiles

    # def tiles_that_placed_on_table_before_ice_break(self, tiles_turn_begin: list[Tile]) -> list[Tile]:
    #     s_begin = set(tiles_turn_begin)
    #     s_end = set(self.tiles)
    #     s = s_end - s_begin
    #     return list(s)

    def sum_valid_lst_tile_number(self, lst: list[Tile]):
        number = 0
        lst_number = [tile.number for tile in lst]
        has_joker = JOKER_NUMBER in lst_number
        if Tiles.is_a_run(lst):
            if not has_joker:
                number += sum(lst_number)
            else:
                # Has joker
                non_joker_idx = lst_number.index(next(filter(lambda x: x != JOKER_NUMBER, lst_number)))
                common_difference = lst_number[non_joker_idx] - non_joker_idx * 2
                number += sum([i * 2 + common_difference for i in range(len(lst_number))])

        elif Tiles.is_a_group(lst):
            if not has_joker:
                number += max(lst_number) * len(lst_number)
            else:
                non_joker_idx = lst_number.index(next(filter(lambda x: x != JOKER_NUMBER, lst_number)))
                number += lst_number[non_joker_idx] * len(lst_number)

        return number

    def sum_valid_list_of_lst_tile_number(self, list_of_lst: list[list[Tile]]):
        number = 0
        for lst in list_of_lst:
            number += self.sum_valid_lst_tile_number(lst)
        return number

    def relocate_tiles(self, lst_of_lst_tiles: list[list[Tile]]):
        result_grid = [[] for _ in range(TABLE_ROW_LIMIT)]

        current_row = 0
        current_col = 0

        for sublist in lst_of_lst_tiles:
            # Check if the current row can accommodate the sublist with space
            if current_col + len(sublist) + (current_col > 0) > TABLE_COL_LIMIT:
                # Fill the remaining space in the current row with None
                remaining_space = TABLE_COL_LIMIT - current_col
                result_grid[current_row] += [None] * remaining_space
                current_row += 1
                current_col = 0

            # Check if the current row exceeds the row limit
            if current_row >= TABLE_ROW_LIMIT:
                break  # Stop if we've reached the row limit

            # Add space between sublists if needed
            if current_col > 0:
                result_grid[current_row].append(None)
                current_col += 1

            # Fill in the sublist in the selected row and column
            result_grid[current_row] += sublist
            current_col += len(sublist)

        # Fill the remaining space in the last row with None
        remaining_space = TABLE_COL_LIMIT - current_col
        result_grid[current_row] += [None] * remaining_space

        idx = 0
        for row in result_grid:
            for tile in row:
                if tile:
                    tile.move(self.grids[idx])
                idx += 1
