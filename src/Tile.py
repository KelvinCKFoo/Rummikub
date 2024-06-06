from src.public.ProjectConstants import *
from src.public.ProjectGlobals import *

from src.public.Base import Base

import pygame

from typing import *
from itertools import combinations, groupby, chain
from collections import Counter
import math


class Tile(Base):

    def __init__(self, img, number: int, color: tuple[int], *args, **kwargs):
        super().__init__()

        self.img = img
        self.tile_image = pygame.image.load(self.img)
        self.tile_image_fold = pygame.image.load(Path(TILES_DIR, "back_of_tiles.png"))

        self.number: int = number
        self.color: tuple[int] = color

        self.x = 0
        self.y = 0
        self.w = TILE_W
        self.h = TILE_H
        self.tile_rect = None
        self.number_rect = None
        self.pre_coord_before_dragging = self.get_center()

        self.is_hovered = False
        self.is_dragging = False
        self.is_visible = False
        self.is_fold = False

    def is_joker(self):
        return self.number == JOKER_NUMBER and self.color == JOKER_COLOR

    @property
    def score(self):
        return self.number

    def get_center(self):
        return self.x + 0.5 * self.w, self.y + 0.5 * self.h

    def set_center(self, center_x, center_y):
        self.x = center_x - 0.5 * self.w
        self.y = center_y - 0.5 * self.h

    def set_topleft(self, x, y):
        self.x = x
        self.y = y

    def setVisible(self, visible: bool = True):
        a, b = self.get_center()
        if a < 0 or b < 0:
            self.is_visible = False
            return

        self.is_visible = visible

    def setFold(self, fold: bool = False):
        self.is_fold = fold

    @staticmethod
    def get_area_by_x_y(x, y):
        # Valid move destinations
        for area_txt in ["TILES", "POOL", "TABLE", "RACK_USER"]:
            area = get_value(area_txt)
            if area is None:
                continue

            rect = getattr(area, "rect", None)
            if isinstance(rect, pygame.Rect) and rect.collidepoint(x, y):
                return area

        return None

    def get_center_area(self):
        return self.get_area_by_x_y(*self.get_center())

    def update(self, events, *args, **kwargs):
        if not self.tile_rect:
            return

        GAME = get_value("GAME")
        PLAYER_USER = get_value("PLAYER_USER")
        TILES = get_value("TILES")
        TABLE = get_value("TABLE")
        RACK_USER = get_value("RACK_USER")
        POOL = get_value("POOL")

        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.is_hovered = self.tile_rect.collidepoint(event.pos)
                if self.is_dragging:
                    # Let mouse at tile center
                    pos_x, pos_y = event.pos
                    self.set_center(pos_x, pos_y)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_hovered:
                    self.is_dragging = True
                    self.pre_coord_before_dragging = self.get_center()

            elif event.type == pygame.MOUSEBUTTONUP:
                self.is_dragging = False
                if self.is_hovered:
                    # Areas
                    pre_area = Tile.get_area_by_x_y(*self.pre_coord_before_dragging)
                    cur_area = Tile.get_area_by_x_y(*event.pos)

                    # print(pre_area, cur_area, self, self.get_center_area())

                    # IF Not valid area (both pre and cur)
                    # OR Overlap with other tiles
                    # OR Not user's turn
                    if pre_area is None or cur_area is None or TILES.check_overlap(
                            self) or not GAME.is_player_user_turn():
                        self.set_center(*self.pre_coord_before_dragging)
                        continue

                    # Rack to Rack
                    if pre_area == cur_area == RACK_USER:
                        if ret := RACK_USER.fit_grid(*event.pos):
                            self.set_center(*ret)
                            continue
                        continue

                    # Table to Table
                    if pre_area == cur_area == TABLE:
                        if ret := TABLE.fit_grid(*event.pos):
                            self.set_center(*ret)
                            continue
                        continue

                    # Table to Rack
                    if pre_area == TABLE and cur_area == RACK_USER:
                        if ret := RACK_USER.fit_grid(*event.pos):
                            self.set_center(*ret)
                            continue
                        continue

                    # Rack to Table
                    if pre_area == RACK_USER and cur_area == TABLE:
                        if not PLAYER_USER.has_drawn_two_tile():
                            if ret := TABLE.fit_grid(*event.pos):
                                self.set_center(*ret)
                                RACK_USER.play_tile(self)
                                TABLE.add_tile(self)
                                continue
                        else:
                            print("Can not move tile from rack to table after drawn tiles from pool")

                    # Draw and pick one (drag the other one tile return to the pool)
                    if pre_area == RACK_USER and cur_area == POOL:
                        if PLAYER_USER.has_drawn_two_tile():
                            if not PLAYER_USER.has_return_drawn_one_tile():
                                if PLAYER_USER.is_among_the_tile_drawn_from_pool(self):
                                    RACK_USER.play_tile(self)
                                    POOL.add_tile(self)
                                    PLAYER_USER.return_drawn_one_tile()
                                    continue
                                else:
                                    print("Can not return tiles that are not drawn from the pool")
                            else:
                                print("Already returned, can not return move")
                        else:
                            print("Did not draw, but tried to return tiles")

                    # Tile go back where it was
                    self.set_center(*self.pre_coord_before_dragging)
                    continue

    def draw(self):
        if not self.is_visible:
            return

        # Load the card background image
        if not self.is_fold:
            tile_image = pygame.transform.scale(self.tile_image, (self.w, self.h))
        else:
            tile_image = pygame.transform.scale(self.tile_image_fold, (self.w, self.h))

        self.tile_rect = tile_image.get_rect(topleft=(self.x, self.y))
        self.screen.blit(tile_image, self.tile_rect)

        # # Render and draw the tile number
        # if self.number > 0:
        #     number_text = str(self.number)
        # else:
        #     # Joker
        #     number_text = ""
        # number_surface = self.font.render(number_text, True, self.color)
        # number_rect = number_surface.get_rect(center=self.tile_rect.center)
        # self.screen.blit(number_surface, number_rect)

        if not self.is_dragging:
            # In case of overlapping after initialization
            self.pre_coord_before_dragging = self.get_center()

    def move(self, top_left: tuple, visible: bool = True):
        self.set_topleft(*top_left)
        self.setVisible(visible)
        self.draw()

    def move_to_POOL_only(self):
        POOL = get_value("POOL")
        if POOL is None:
            return

        self.set_topleft(*POOL.rect.topleft)
        # Order matters
        self.draw()
        self.setVisible(False)

    def __str__(self):
        if self.color == JOKER_COLOR:
            return f"Joker {JOKER_NUMBER}"

        color_name = [k for k, v in TILE_COLOURS.items() if v == self.color][0]
        return f"{color_name} {self.number}"

    def __repr__(self):
        return str(self)

    @staticmethod
    def rgb_to_int(rgb_tuple):
        r, g, b = rgb_tuple
        rgb_value = (r << 16) + (g << 8) + b
        return rgb_value

    @staticmethod
    def sort_key_number_first(tile: "Tile"):
        return (tile.number, Tile.rgb_to_int(tile.color))

    @staticmethod
    def sort_key_color_first(tile: "Tile"):
        return (Tile.rgb_to_int(tile.color), tile.number)

    def __lt__(self, other):
        if self.number < other.number:
            return True
        elif Tile.rgb_to_int(self.color) < Tile.rgb_to_int(other.color):
            return True
        else:
            return False

    def clicked(self):
        pass


@SingletonDecorator
class Tiles(Base):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.d_number_color_idx__tile = dict()

        self.__init_all_tiles()

    def __init_all_tiles(self):
        for color in TILE_COLOURS:
            for number in TILE_NUMBER_RANGE:
                fn = color.lower() + "_" + str(number) + ".png"
                tile_1 = Tile(Path(TILES_DIR, fn), number, TILE_COLOURS[color])
                self.d_number_color_idx__tile[(number, TILE_COLOURS[color], 1)] = tile_1
                tile_2 = Tile(Path(TILES_DIR, fn), number, TILE_COLOURS[color])
                self.d_number_color_idx__tile[(number, TILE_COLOURS[color], 2)] = tile_2

        # Joker
        tile_joker_1 = Tile(Path(TILES_DIR, "joker_1.png"), JOKER_NUMBER, JOKER_COLOR)
        tile_joker_2 = Tile(Path(TILES_DIR, "joker_2.png"), JOKER_NUMBER, JOKER_COLOR)
        self.d_number_color_idx__tile[(JOKER_NUMBER, JOKER_COLOR, 1)] = tile_joker_1
        self.d_number_color_idx__tile[(JOKER_NUMBER, JOKER_COLOR, 2)] = tile_joker_2

    @property
    def tiles(self):
        return list(self.d_number_color_idx__tile.values())

    def check_overlap(self, tile: Tile):
        for t in self.tiles:
            if not t.tile_rect:
                continue

            if t is tile:
                continue

            if t.is_visible and t.tile_rect.collidepoint(tile.get_center()):
                return t

        return

    def has_tile(self, topleft: Tuple):
        x, y = topleft
        x = x + TILE_W * 0.5
        y = y + TILE_H * 0.5
        for tile in self.tiles:
            if not tile.tile_rect:
                continue

            if tile.tile_rect.collidepoint(x, y):
                return tile

        return False

    @staticmethod
    def is_a_run(lst: list[Tile]) -> bool:
        # Runs are redefined as sequences of successive odd or even tiles
        # of the same colour

        n = len(lst)
        if not (3 <= n <= math.ceil((MAX_TILE_NUMBER - MIN_TILE_NUMBER + 1) / 2)):
            return False

        if any(tile.is_joker() for tile in lst):
            # Same color except joker
            set_color = set(tile.color for tile in lst)
            set_color.discard(JOKER_COLOR)
            if len(set_color) != 1:
                return False

            # if there is any joker
            def can_form_arithmetic_sequence(number_lst, start_index=0):
                # Check if the end of the list is reached
                if start_index >= len(number_lst):
                    # Check if the list is an arithmetic sequence with a common difference of 2
                    return all(number_lst[i] - number_lst[i - 1] == 2 for i in range(1, len(number_lst)))

                # If the current element is not joker, continue with the next element
                if number_lst[start_index] != JOKER_NUMBER:
                    return can_form_arithmetic_sequence(number_lst, start_index + 1)
                else:
                    # Try replacing the 0 with different numbers to form an arithmetic sequence
                    for replacement in range(1, min(max(number_lst) + 3, MAX_TILE_NUMBER + 1)):
                        number_lst[start_index] = replacement
                        if can_form_arithmetic_sequence(number_lst, start_index + 1):
                            return True
                    # Backtrack and restore the joker
                    number_lst[start_index] = JOKER_NUMBER
                    return False

            number_lst = [tile.number for tile in lst]
            if can_form_arithmetic_sequence(number_lst):
                return True

        else:
            # no joker
            if all(tile.color == lst[0].color for tile in lst):
                if all(lst[i + 1].number - lst[i].number == 2 for i in range(n - 1)):
                    return True

        return False

    @staticmethod
    def is_a_group(lst: list[Tile]) -> bool:
        # A group is a set of either 3, 4 or 5 tiles
        # of the same number in different colors.

        n = len(lst)
        if n in list(range(3, len(TILE_COLOURS) + 1)):
            # if there is any joker
            if any(tile.is_joker() for tile in lst):
                cnt_joker = 0
                c_color = Counter()
                for tile in lst:
                    if tile.color != JOKER_COLOR:
                        c_color.update([tile.color, ])
                    else:
                        cnt_joker += 1

                # Each color appears only once
                if len(set(c_color.values())) == 1:
                    number = -1
                    c_number = Counter()
                    for tile in lst:
                        if not tile.is_joker():
                            number = tile.number
                            c_number.update([tile.number, ])
                        else:
                            c_number.update([tile.number, ])

                    if c_number.get(JOKER_NUMBER) == cnt_joker:
                        if c_number.get(number) == n - cnt_joker:
                            return True

            else:
                # no joker
                if n == len(set(tile.color for tile in lst)):
                    if all(tile.number == lst[0].number for tile in lst):
                        return True

        return False

    @staticmethod
    def group_by_number(tiles: list[Tile]) -> tuple[list[list[Tile]], list[Tile]]:
        valid_groups = []

        # Group by number
        number_groups = {}
        for tile in tiles:
            number = tile.number
            l = number_groups.setdefault(number, list())
            l.append(tile)

        # Find valid groups
        for number, group in number_groups.items():
            if len(group) >= 3:
                valid_groups.append(group)

        # Extract selected tiles from the original list
        remaining_tiles = [
            tile for tile in tiles if tile not in [item for sublist in valid_groups for item in sublist]
        ]

        # Sort the remaining tiles
        remaining_tiles.sort(key=Tile.sort_key_number_first)

        return valid_groups, remaining_tiles

    @staticmethod
    def group_by_run(tiles: list[Tile]) -> tuple[list[list[Tile]], list[Tile]]:
        valid_runs = []

        # Group by color
        color_groups = {}
        for tile in tiles:
            color = tile.color
            if color not in color_groups:
                color_groups[color] = []
            color_groups[color].append(tile)

        # Find valid runs
        for color, group in color_groups.items():
            sorted_group = sorted(group, key=lambda x: x.number)
            current_run = [sorted_group[0]]

            for i in range(1, len(sorted_group)):
                if sorted_group[i].number - current_run[-1].number == 2:
                    current_run.append(sorted_group[i])
                else:
                    if len(current_run) >= 3:
                        valid_runs.append(current_run)
                    current_run = [sorted_group[i]]

            if len(current_run) >= 3:
                valid_runs.append(current_run)

        # Extract selected tiles from the original list
        remaining_tiles = [
            tile for tile in tiles if tile not in [item for sublist in valid_runs for item in sublist]
        ]

        # Sort the remaining tiles
        remaining_tiles.sort(key=Tile.sort_key_color_first)

        return valid_runs, remaining_tiles

    @staticmethod
    def find_all_combinations(tiles: list[Tile], all_lst_tiles_on_table: list[list[Tile]] = None):
        if all_lst_tiles_on_table is None:
            all_lst_tiles_on_table = []

        all_combinations = []
        used_tiles = set()

        # Sort
        sorted_by_color = sorted(tiles, key=lambda x: (x.color, x.number))
        for color, group in groupby(sorted_by_color, key=lambda x: x.color):
            color_tiles = list(group)
            # longest run
            for i in range(len(color_tiles)):
                for j in range(len(color_tiles), i + 1, -1):
                    combo = color_tiles[i:j]
                    if Tiles.is_a_run(combo) and all(tile not in used_tiles for tile in combo):
                        all_combinations.append(list(combo))
                        used_tiles.update(combo)

        # Sort number, color for groups
        sorted_by_number = sorted(tiles, key=lambda x: x.number)
        for number, group in groupby(sorted_by_number, key=lambda x: x.number):
            group_tiles = list(group)
            # longest group
            for n in range(min(6, len(group_tiles)), 2, -1):
                for combo in combinations(group_tiles, n):
                    if Tiles.is_a_group(combo) and all(tile not in used_tiles for tile in combo):
                        all_combinations.append(list(combo))
                        used_tiles.update(combo)

                        # extend combinations
        remaining_tiles = [tile for tile in tiles if tile not in used_tiles]
        for tile in remaining_tiles:
            for combo in all_combinations:
                if not any(
                        (tile.number, tile.color) == (combo_tile.number, combo_tile.color) for combo_tile in combo
                ):

                    new_combo = sorted(combo + [tile], key=lambda x: (x.color, x.number))

                    # Check run or group
                    if Tiles.is_a_run(new_combo) or Tiles.is_a_group(new_combo):
                        # add combination and used tiles
                        combo.append(tile)
                        combo.sort(key=lambda x: (x.color, x.number))
                        used_tiles.add(tile)
                        break

        all_lst_tiles_on_table.extend(all_combinations)

        if get_value('TABLE').get_all_lst_tiles_on_table():
            remaining_tiles = [tile for tile in tiles if tile not in used_tiles]
            for tile in remaining_tiles:
                for combo in all_lst_tiles_on_table:
                    if not any(
                            (tile.number, tile.color) == (combo_tile.number, combo_tile.color) for combo_tile in combo
                    ):
                        new_combo = sorted(combo + [tile], key=lambda x: (x.color, x.number))

                        # Check run or group
                        if Tiles.is_a_run(new_combo) or Tiles.is_a_group(new_combo):
                            # add combination and used tiles
                            combo.append(tile)
                            combo.sort(key=lambda x: (x.color, x.number))

                            used_tiles.add(tile)
                            break

        print(f'final_table: \n{all_lst_tiles_on_table}')
        return used_tiles, all_lst_tiles_on_table

    @staticmethod
    def calculate_score(tiles: list[Tile]):
        return sum(tile.score for tile in tiles)
